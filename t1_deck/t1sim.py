"""Turn-1 win simulator for Commander (multiplayer, 3 passive opponents at 40 life).

Rules used (see sources/REGLES.md):
  * CR 103.8c: every player draws on their first turn  -> 7 + 1 cards.
  * CR 103.5 / 103.5c: London mulligan, first mulligan free in multiplayer.
  * Seat matters only through Gemstone Caverns (not usable by the starting player).
Win = Thassa's Oracle / Laboratory Maniac / Jace, Wielder of Mysteries with an empty
library (Demonic Consultation naming a card absent from the deck, or Tainted Pact).

Policy (non clairvoyant): the planner searches every line using known cards only.
Cards drawn from the unknown part of the library are placeholders ('?') that cannot be
used.  If a line wins, it is played.  Otherwise the planner plays the line up to the
most promising action that reveals new cards, the cards are revealed, and it re-plans.
"""
import random, sys, json, os, math
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = json.load(open(os.path.join(HERE, 'cache', 'cards.json')))

COLORS = 'WUBRGCAX'         # A = any color; X = Mishra's Workshop mana (artifact spells only)
CI = {}                      # filled by deck: commander colour identity

# ------------------------------------------------------------------ card specs
# Each spec was written from the Oracle text stored in cache/cards.json.
S = {}
def spec(name, **kw):
    assert name in CACHE, f'{name} not verified in cache'
    S[name] = kw

# win pieces
spec("Thassa's Oracle", kind='oracle', cost={'U': 2}, mv=2, type='creature', colors='U')
spec('Demonic Consultation', kind='consult', cost={'B': 1}, mv=1, type='instant', colors='B')
spec('Tainted Pact', kind='consult', cost={'B': 1, 'g': 1}, mv=2, type='instant', colors='B', pact=True)
spec('Laboratory Maniac', kind='labman', cost={'U': 1, 'g': 2}, mv=3, type='creature', colors='U')
spec('Jace, Wielder of Mysteries', kind='jace', cost={'U': 3, 'g': 1}, mv=4, type='planeswalker', colors='U')
# rocks / free mana
spec('Sol Ring', kind='rock', cost={'g': 1}, mv=1, out='CC', type='artifact')
spec('Mana Vault', kind='rock', cost={'g': 1}, mv=1, out='CCC', type='artifact')
spec('Grim Monolith', kind='rock', cost={'g': 2}, mv=2, out='CCC', type='artifact')
spec('Lotus Petal', kind='rock', cost={}, mv=0, out='A', type='artifact', sac_on_use=True)
spec('Chrome Mox', kind='chrome', cost={}, mv=0, type='artifact')
spec('Mox Diamond', kind='diamond', cost={}, mv=0, type='artifact')
spec('Mox Opal', kind='opal', cost={}, mv=0, type='artifact')
spec('Mox Amber', kind='amber', cost={}, mv=0, type='artifact')
spec("Lion's Eye Diamond", kind='led', cost={}, mv=0, type='artifact')
spec('Springleaf Drum', kind='drum', cost={'g': 1}, mv=1, type='artifact')
# rituals
spec('Dark Ritual', kind='ritual', cost={'B': 1}, out='BBB', mv=1, type='instant', colors='B')
spec('Cabal Ritual', kind='ritual', cost={'B': 1, 'g': 1}, out='BBB', mv=2, type='instant', colors='B')
spec('Culling the Weak', kind='ritual', cost={'B': 1}, out='BBBB', mv=1, type='instant', colors='B', sac=True)
spec('Rite of Flame', kind='ritual', cost={'R': 1}, out='RR', mv=1, type='sorcery', colors='R')
spec('Pyretic Ritual', kind='ritual', cost={'R': 1, 'g': 1}, out='RRR', mv=2, type='instant', colors='R')
spec('Desperate Ritual', kind='ritual', cost={'R': 1, 'g': 1}, out='RRR', mv=2, type='instant', colors='R')
spec('Seething Song', kind='ritual', cost={'R': 1, 'g': 2}, out='RRRRR', mv=3, type='instant', colors='R')
spec('Manamorphose', kind='ritual', cost={'RG': 1, 'g': 1}, out='AA', mv=2, type='instant', colors='RG', draw=1)
spec("Jeska's Will", kind='jeska', cost={'R': 1, 'g': 2}, mv=3, type='sorcery', colors='R')
spec('Strike It Rich', kind='treasure', cost={'R': 1}, mv=1, type='sorcery', colors='R')
spec('Simian Spirit Guide', kind='guide', out='R', mv=3, type='creature', colors='R')
spec('Elvish Spirit Guide', kind='guide', out='G', mv=3, type='creature', colors='G')
# tutors to hand
spec('Demonic Tutor', kind='tutor', cost={'B': 1, 'g': 1}, mv=2, type='sorcery', colors='B', filt='any')
spec('Grim Tutor', kind='tutor', cost={'B': 2, 'g': 1}, mv=3, type='sorcery', colors='B', filt='any', life=3)
spec('Diabolic Intent', kind='tutor', cost={'B': 1, 'g': 1}, mv=2, type='sorcery', colors='B', filt='any', sac=True)
spec('Gamble', kind='tutor', cost={'R': 1}, mv=1, type='sorcery', colors='R', filt='any', gamble=True)
spec('Merchant Scroll', kind='tutor', cost={'U': 1, 'g': 1}, mv=2, type='sorcery', colors='U', filt='blueinstant')
spec('Solve the Equation', kind='tutor', cost={'U': 1, 'g': 2}, mv=3, type='sorcery', colors='U', filt='instsorc')
spec('Beseech the Mirror', kind='beseech', cost={'B': 3, 'g': 1}, mv=4, type='sorcery', colors='B')
# transmute (from hand, sorcery speed, {1}{U}{U} or {1}{B}{B})
spec('Muddle the Mixture', kind='transmute', tcost={'U': 2, 'g': 1}, mv=2, type='instant', colors='U')
spec('Dizzy Spell', kind='transmute', tcost={'U': 2, 'g': 1}, mv=1, type='instant', colors='U')
spec('Shred Memory', kind='transmute', tcost={'B': 2, 'g': 1}, mv=2, type='instant', colors='B')
spec('Drift of Phantasms', kind='transmute', tcost={'U': 2, 'g': 1}, mv=3, type='creature', colors='U')
# tutors to top
spec('Vampiric Tutor', kind='toptutor', cost={'B': 1}, mv=1, type='instant', colors='B', filt='any')
spec('Imperial Seal', kind='toptutor', cost={'B': 1}, mv=1, type='sorcery', colors='B', filt='any')
spec('Mystical Tutor', kind='toptutor', cost={'U': 1}, mv=1, type='instant', colors='U', filt='instsorc')
spec('Worldly Tutor', kind='toptutor', cost={'G': 1}, mv=1, type='instant', colors='G', filt='creature')
spec('Enlightened Tutor', kind='toptutor', cost={'W': 1}, mv=1, type='instant', colors='W', filt='artench')
spec('Personal Tutor', kind='toptutor', cost={'U': 1}, mv=1, type='sorcery', colors='U', filt='sorcery')
spec('Scheming Symmetry', kind='toptutor', cost={'B': 1}, mv=1, type='sorcery', colors='B', filt='any')
spec("Lim-Dûl's Vault", kind='toptutor', cost={'U': 1, 'B': 1}, mv=2, type='instant', colors='UB', filt='any')
# draw
spec('Brainstorm', kind='draw', cost={'U': 1}, mv=1, type='instant', colors='U', n=3, back=2)
spec('Ponder', kind='draw', cost={'U': 1}, mv=1, type='sorcery', colors='U', n=1, look=3)
spec('Preordain', kind='draw', cost={'U': 1}, mv=1, type='sorcery', colors='U', n=1, look=3)
spec('Opt', kind='draw', cost={'U': 1}, mv=1, type='instant', colors='U', n=1, look=2)
spec('Sleight of Hand', kind='draw', cost={'U': 1}, mv=1, type='sorcery', colors='U', n=1, look=2, nodraw=True)
spec('Gitaxian Probe', kind='draw', cost={}, mv=1, type='sorcery', colors='U', n=1, life=2)
spec('Street Wraith', kind='cycle', mv=5, type='creature', colors='B', n=1, life=2)
spec("Night's Whisper", kind='draw', cost={'B': 1, 'g': 1}, mv=2, type='sorcery', colors='B', n=2, life=2)
spec('Wheel of Fortune', kind='wheel', cost={'R': 1, 'g': 2}, mv=3, type='sorcery', colors='R')
spec('Windfall', kind='wheel', cost={'U': 1, 'g': 2}, mv=3, type='sorcery', colors='U')
spec('Timetwister', kind='wheel', cost={'U': 1, 'g': 2}, mv=3, type='sorcery', colors='U', twister=True)
# lands
for n in ['City of Brass', 'Mana Confluence', 'Gemstone Mine', 'Forbidden Orchard', 'Command Tower']:
    spec(n, kind='land', out='A', mv=0, type='land')
spec('Ancient Tomb', kind='land', out='CC', mv=0, type='land')
spec('Gemstone Caverns', kind='land', out='C', mv=0, type='land', caverns=True)
spec('Tolaria West', kind='land', out='', mv=0, type='land', transmute0=True, tcost={'U': 2, 'g': 1})
DUALS = {'Underground Sea': 'UB', 'Volcanic Island': 'UR', 'Badlands': 'BR', 'Watery Grave': 'UB',
         'Steam Vents': 'UR', 'Blood Crypt': 'BR', 'Tropical Island': 'GU', 'Bayou': 'BG', 'Taiga': 'RG'}
for n, c in DUALS.items():
    spec(n, kind='land', out=c, mv=0, type='land', dual=True)
for n, c in {'Island': 'U', 'Swamp': 'B', 'Mountain': 'R', 'Forest': 'G', 'Plains': 'W'}.items():
    spec(n, kind='land', out=c, mv=0, type='land', basic=True)
FETCH = {'Scalding Tarn': 'UR', 'Polluted Delta': 'UB', 'Bloodstained Mire': 'BR', 'Misty Rainforest': 'UG',
         'Verdant Catacombs': 'BG', 'Wooded Foothills': 'RG', 'Flooded Strand': 'UW', 'Marsh Flats': 'BW',
         'Windswept Heath': 'GW', 'Arid Mesa': 'RW'}
for n, c in FETCH.items():
    spec(n, kind='fetch', types=c, mv=0, type='land')
spec('Prismatic Vista', kind='fetch', types='basic', mv=0, type='land')
for n in ['Memnite', 'Ornithopter', 'Phyrexian Walker', 'Shield Sphere']:
    spec(n, kind='freecre', cost={}, mv=0, type='artifact')
spec('Consider', kind='draw', cost={'U': 1}, mv=1, type='instant', colors='U', n=1, look=2)
spec('Serum Visions', kind='draw', cost={'U': 1}, mv=1, type='sorcery', colors='U', n=1)
spec('Tarnished Citadel', kind='land', out='A', mv=0, type='land')
spec('Morphic Pool', kind='land', out='UB', mv=0, type='land', dual=True)
for n, c in {'Savannah': 'GW', 'Scrubland': 'BW', 'Plateau': 'RW', 'Hallowed Fountain': 'UW', 'Godless Shrine': 'BW',
             'Sacred Foundry': 'RW', 'Breeding Pool': 'GU', 'Overgrown Tomb': 'BG', 'Stomping Ground': 'RG',
             'Temple Garden': 'GW'}.items():
    spec(n, kind='land', out=c, mv=0, type='land', dual=True)
spec('Faithless Looting', kind='draw', cost={'R': 1}, mv=1, type='sorcery', colors='R', n=2, discard=2)
spec('Dark Petition', kind='tutor', cost={'B': 2, 'g': 3}, mv=5, type='sorcery', colors='B', filt='any', mastery=True)
spec("Mishra's Workshop", kind='land', out='XXX', mv=0, type='land')
spec('Ad Nauseam', kind='adnaus', cost={'B': 2, 'g': 3}, mv=5, type='instant', colors='B')
spec('Serum Powder', kind='blank', mv=3, type='artifact')
spec('Silas Renn, Seeker Adept', kind='blank', mv=3, type='creature', colors='UB')
spec('Rograkh, Son of Rohgahh', kind='free_creature', mv=0, type='creature', colors='R', legendary=True)

LAND_TYPES = {'Island': 'U', 'Swamp': 'B', 'Mountain': 'R', 'Forest': 'G', 'Plains': 'W'}
def land_subtypes(name):
    t = CACHE[name]['type_line']
    return ''.join(c for k, c in LAND_TYPES.items() if k in t)

def is_blue_instant(n):
    s = S.get(n); return s and s.get('type') == 'instant' and 'U' in s.get('colors', '')
def matches(filt, n):
    s = S.get(n)
    if s is None: return False
    t = s['type']
    if filt == 'any': return True
    if filt == 'instsorc': return t in ('instant', 'sorcery')
    if filt == 'sorcery': return t == 'sorcery'
    if filt == 'creature': return t == 'creature'
    if filt == 'artench': return t in ('artifact',) or 'Enchantment' in CACHE[n]['type_line']
    if filt == 'blueinstant': return is_blue_instant(n)
    return False

# ------------------------------------------------------------------ card value (for discards / put-backs)
WINP = {"Thassa's Oracle", 'Demonic Consultation', 'Tainted Pact', 'Laboratory Maniac', 'Jace, Wielder of Mysteries'}
def value(n, st=None):
    if n == '?': return 0.5
    s = S.get(n)
    if s is None: return 0.0
    k = s['kind']
    if n in WINP: return 10
    if k in ('tutor', 'toptutor', 'beseech', 'transmute'): return 7
    if k in ('led', 'ritual', 'rock', 'jeska', 'chrome', 'diamond', 'guide', 'drum', 'treasure'): return 6
    if k in ('draw', 'wheel', 'cycle'): return 4
    if k in ('land', 'fetch'):
        if st is not None and st.land: return 0.3
        return 5 if st is None or sum(1 for c in st.hand if S.get(c, {}).get('type') == 'land') <= 1 else 0.4
    return 0.1

# ------------------------------------------------------------------ state
class St:
    __slots__ = ('hand', 'unk', 'top', 'lib', 'pool', 'land', 'art', 'cre', 'treas', 'led', 'drum', 'opal', 'amber',
                 'cmdr', 'cz', 'lab', 'jace', 'libempty', 'life', 'phase', 'won', 'seq', 'gy', 'pact_ok', 'caverns', 'acre', 'ctax')
    def copy(self):
        n = St.__new__(St)
        for f in St.__slots__:
            setattr(n, f, getattr(self, f))
        return n
    def key(self):
        return (self.hand, self.unk, self.top, self.pool, self.land, self.art, self.cre, self.treas, self.led,
                self.drum, self.opal, self.amber, self.cmdr, self.cz, self.lab, self.jace, self.libempty, self.phase, self.acre, self.ctax)

def h_add(hand, card):
    return tuple(sorted(hand + (card,)))
def h_rem(hand, card):
    l = list(hand); l.remove(card); return tuple(l)

PI = {c: i for i, c in enumerate(COLORS)}
def padd(pool, out):
    p = list(pool)
    for ch in out:
        p[PI[ch]] += 1
    return tuple(p)

GEN_ORDER = ['C', 'R', 'G', 'W', 'B', 'U', 'A']  # X never pays non-artifact costs
def pay(pool, cost, artifact=False):
    p = list(pool)
    if artifact:
        g = cost.get('g', 0)
        use = min(g, p[PI['X']]); p[PI['X']] -= use
        cost = dict(cost); cost['g'] = g - use
    for c, n in cost.items():
        if c == 'g': continue
        for _ in range(n):
            if c == 'RG':
                for x in ('R', 'G', 'A'):
                    if p[PI[x]] > 0: p[PI[x]] -= 1; break
                else: return None
            elif p[PI[c]] > 0: p[PI[c]] -= 1
            elif p[PI['A']] > 0: p[PI['A']] -= 1
            else: return None
    g = cost.get('g', 0)
    for x in GEN_ORDER:
        while g and p[PI[x]] > 0:
            p[PI[x]] -= 1; g -= 1
    if g: return None
    return tuple(p)

def lib_remove(lib, card):
    l = dict(lib); l[card] -= 1
    if l[card] == 0: del l[card]
    return tuple(sorted(l.items()))

def lib_has(lib, card):
    return any(c == card for c, n in lib)

def lib_add(lib, card):
    l = dict(lib); l[card] = l.get(card, 0) + 1
    return tuple(sorted(l.items()))

# ------------------------------------------------------------------ actions
TARGETS = list(WINP) + ['Dark Ritual', "Lion's Eye Diamond", 'Lotus Petal', "Jeska's Will", 'Seething Song',
                        'Culling the Weak', 'Sol Ring', 'Mana Vault', 'Grim Monolith', 'Cabal Ritual', 'Demonic Tutor',
                        'Beseech the Mirror', 'Chrome Mox', 'Mox Diamond', 'Springleaf Drum']
INSTANT_KINDS_UPKEEP = {'guide', 'toptutor', 'ritual', 'draw'}

def is_instant_speed(n):
    s = S[n]; return s['type'] == 'instant' or s['kind'] in ('guide', 'cycle')

def do_draw(st, n, real, rng):
    hand = st.hand
    for _ in range(n):
        if st.libempty or (real and not st.seq):
            if st.lab or st.jace:
                st.won = True; return st
            return None
        if real:
            c = st.seq[0]; st.seq = st.seq[1:]; st.lib = lib_remove(st.lib, c)
            st.top = st.top[1:] if st.top else ()
            hand = h_add(hand, c)
        elif st.top:
            c = st.top[0]; st.top = st.top[1:]; st.lib = lib_remove(st.lib, c); hand = h_add(hand, c)
        else:
            st.unk += 1
    st.hand = hand
    return st

def shuffle_put(st, card, real, rng, top=True):
    """remove card from library (search), shuffle, optionally put on top.
    Returns False if the card is no longer in the library (already drawn in real mode)."""
    if not lib_has(st.lib, card):
        if real and rng is not None:
            s = list(st.seq); rng.shuffle(s); st.seq = tuple(s); st.top = ()
        return False
    st.lib = lib_remove(st.lib, card)
    if real:
        s = list(st.seq); s.remove(card); rng.shuffle(s); st.seq = tuple(s)
    if top:
        st.lib = lib_add(st.lib, card)
        if real: st.seq = (card,) + st.seq
        st.top = (card,)
    else:
        st.top = ()
    return True

def legendary_colors(st):
    cols = ''
    if st.cmdr: cols += 'R'
    if st.jace: cols += 'U'
    return cols

def tutor_targets(st, filt=None, mv=None):
    seen = []
    for c, n in st.lib:
        if c in TARGETS and (filt is None or matches(filt, c)) and (mv is None or S[c]['mv'] == mv):
            seen.append(c)
    return seen

def gen_actions(st):
    """yield action descriptors"""
    acts = []
    pending_oracle = st.phase == 'oracle_pending'
    upkeep = st.phase == 'upkeep'
    distinct = sorted(set(st.hand))
    for n in distinct:
        s = S.get(n)
        if s is None: continue
        k = s['kind']
        if upkeep and not (is_instant_speed(n) and k in ('guide', 'toptutor', 'ritual', 'draw', 'cycle')):
            continue
        if pending_oracle and not (k in ('consult', 'guide') or (k == 'ritual' and s['type'] == 'instant')):
            continue
        if k == 'land':
            if st.land or upkeep: continue
            out = s['out']
            if s.get('dual'):
                for c in out: acts.append(('land', n, c))
            else:
                acts.append(('land', n, out))
            if s.get('transmute0') and not upkeep:
                for t in tutor_targets(st, mv=0): acts.append(('transmute', n, t))
        elif k == 'fetch':
            if st.land or upkeep: continue
            cols = set()
            for c, cnt in st.lib:
                sc = S.get(c)
                if sc and sc['kind'] == 'land' and (sc.get('dual') or sc.get('basic')):
                    if s['types'] == 'basic':
                        if sc.get('basic'): cols.add((c, sc['out']))
                    elif set(land_subtypes(c)) & set(s['types']):
                        for col in sc['out']: cols.add((c, col))
            seen_col = set()
            for c, col in sorted(cols):
                if col in seen_col: continue
                seen_col.add(col); acts.append(('fetch', n, c, col))
        elif k == 'freecre':
            if upkeep or pending_oracle: continue
            acts.append(('freecre', n))
        elif k in ('rock', 'opal', 'amber', 'led', 'drum', 'diamond'):
            if upkeep or pending_oracle: continue
            if k == 'diamond':
                lands = sorted({c for c in st.hand if S.get(c, {}).get('type') == 'land'})
                for l in lands: acts.append(('diamond', n, l))
            else:
                acts.append(('rock', n))
        elif k == 'chrome':
            if upkeep or pending_oracle: continue
            for c in sorted(set(st.hand)):
                sc = S.get(c)
                if c != n and sc and sc['type'] not in ('land', 'artifact') and sc.get('colors'):
                    for col in sorted(set(sc['colors'])):
                        acts.append(('chrome', n, c, col))
        elif k == 'ritual':
            if s.get('sac') and st.cre == 0: continue
            acts.append(('ritual', n))
        elif k == 'jeska':
            acts.append(('jeska', n))
        elif k == 'treasure':
            acts.append(('treasure', n))
        elif k == 'guide':
            acts.append(('guide', n))
        elif k == 'tutor':
            if s.get('sac') and st.cre == 0: continue
            for t in tutor_targets(st, s['filt']): acts.append(('tutor', n, t))
        elif k == 'toptutor':
            for t in tutor_targets(st, s['filt']): acts.append(('toptutor', n, t))
        elif k == 'transmute':
            if upkeep: continue
            for t in tutor_targets(st, mv=s['mv']): acts.append(('transmute', n, t))
        elif k == 'beseech':
            for t in tutor_targets(st): acts.append(('beseech', n, t, False))
            fod = st.treas + st.art
            if fod:
                for t in tutor_targets(st):
                    if S[t]['mv'] <= 4: acts.append(('beseech', n, t, True))
        elif k in ('draw', 'cycle', 'wheel', 'adnaus'):
            acts.append((k, n))
        elif k in ('oracle', 'consult', 'labman', 'jace'):
            acts.append((k, n))
    if not upkeep:
        if st.cz and not st.cmdr and not pending_oracle: acts.append(('cmdr',))
        if st.drum and st.cre: acts.append(('drumtap',))
        if st.treas: acts.append(('treastap',))
        if st.opal and st.art >= 3: acts.append(('opaltap',))
        if st.amber and legendary_colors(st): 
            for c in legendary_colors(st): acts.append(('ambertap', c))
    if st.caverns: acts.append(('caverns',))
    return acts

def sac_creature(n2):
    n2.cre -= 1
    nonart = n2.cre + 1 - n2.acre          # creatures that are not artifacts (Rograkh, Lab Maniac)
    if n2.acre and (n2.opal == 0 or nonart <= 0):
        n2.acre -= 1; n2.art -= 1
    elif n2.cmdr:
        n2.cmdr = False
    elif n2.acre:
        n2.acre -= 1; n2.art -= 1
    elif n2.lab:
        n2.lab = False

def cost_of(st, n, s):
    return dict(s.get('cost', {}))

def apply(st, a, real=False, rng=None, led=False):
    """apply action a; returns new state or None. led=True: sacrifice LED(s) to pay (discard hand after)."""
    n2 = st.copy()
    t = a[0]
    if t == 'land':
        _, n, out = a
        n2.hand = h_rem(n2.hand, n); n2.land = True
        n2.pool = padd(n2.pool, out)
        return n2
    if t == 'fetch':
        _, n, c, col = a
        n2.hand = h_rem(n2.hand, n); n2.land = True; n2.life -= 1
        if not shuffle_put(n2, c, real, rng, top=False): return None
        n2.pool = padd(n2.pool, col)
        return n2
    if t == 'cmdr':
        # CR 903.8: commander tax, {2} more for each previous cast from the command zone
        if n2.ctax:
            p = pay(n2.pool, {'g': 2 * n2.ctax})
            if p is None: return None
            n2.pool = p
        n2.ctax += 1
        n2.cmdr = True; n2.cre += 1; return n2
    if t == 'drumtap':
        n2.cre -= 1; n2.pool = padd(n2.pool, 'A'); n2.drum -= 1; return n2
    if t == 'treastap':
        n2.treas -= 1; n2.art -= 1; n2.pool = padd(n2.pool, 'A'); return n2
    if t == 'opaltap':
        n2.opal -= 1; n2.pool = padd(n2.pool, 'A'); return n2
    if t == 'ambertap':
        n2.amber -= 1; n2.pool = padd(n2.pool, a[1]); return n2
    if t == 'caverns':
        n2.caverns = 0; n2.pool = padd(n2.pool, 'A'); return n2
    n = a[1]; s = S[n]
    # ---- casting / using a card from hand
    if t == 'guide':
        n2.hand = h_rem(n2.hand, n); n2.pool = padd(n2.pool, s['out']); return n2
    if t == 'cycle':
        n2.hand = h_rem(n2.hand, n); n2.life -= s['life']
        return do_draw(n2, s['n'], real, rng)
    if t == 'transmute':
        p = pay(n2.pool, s['tcost'])
        if p is None: return None
        n2.pool = p; n2.hand = h_rem(n2.hand, n)
        if shuffle_put(n2, a[2], real, rng, top=False): n2.hand = h_add(n2.hand, a[2])
        return n2
    if t == 'freecre':
        n2.hand = h_rem(n2.hand, n); n2.art += 1; n2.cre += 1; n2.acre += 1; return n2
    if t == 'chrome':
        _, n, imp, col = a
        n2.hand = h_rem(h_rem(n2.hand, n), imp); n2.art += 1; n2.pool = padd(n2.pool, col); return n2
    if t == 'diamond':
        _, n, l = a
        n2.hand = h_rem(h_rem(n2.hand, n), l); n2.art += 1; n2.pool = padd(n2.pool, 'A'); return n2
    if t == 'rock':
        p = pay(n2.pool, s['cost'], artifact=True)
        if p is None: return None
        n2.pool = p; n2.hand = h_rem(n2.hand, n); n2.art += 1
        k = s['kind']
        if k == 'rock':
            n2.pool = padd(n2.pool, s['out'])
            if s.get('sac_on_use'): n2.art -= 1      # Lotus Petal: {T}, Sacrifice -> no longer an artifact
        elif k == 'opal': n2.opal += 1
        elif k == 'amber': n2.amber += 1
        elif k == 'led': n2.led += 1
        elif k == 'drum': n2.drum += 1
        return n2
    # spells with a mana cost
    cost = cost_of(n2, n, s)
    pool = n2.pool
    if led:
        if n2.led <= 0: return None
        n2.led -= 1; n2.art -= 1; pool = padd(pool, 'AAA')
    p = pay(pool, cost)
    if p is None: return None
    n2.pool = p
    n2.hand = h_rem(n2.hand, n)
    if s['type'] in ('instant', 'sorcery'):
        n2.gy += 1
    if led:
        n2.hand = (); n2.unk = 0
    if s.get('life'): n2.life -= s['life']
    if t == 'ritual':
        if s.get('sac'):
            sac_creature(n2)
        n2.pool = padd(n2.pool, s['out'])
        if s.get('draw'): return do_draw(n2, s['draw'], real, rng)
        return n2
    if t == 'jeska':
        n2.pool = padd(n2.pool, 'R' * 7)
        if n2.cmdr:  # both modes: exile top 3, playable this turn (treated as drawn)
            return do_draw(n2, 3, real, rng) if not n2.libempty else n2
        return n2
    if t == 'treasure':
        n2.treas += 1; n2.art += 1; return n2
    if t == 'tutor':
        if s.get('sac'):
            sac_creature(n2)
        if shuffle_put(n2, a[2], real, rng, top=False):
            n2.hand = h_add(n2.hand, a[2])
        if s.get('mastery') and n2.gy - 1 >= 2:      # Dark Petition itself is still on the stack
            n2.pool = padd(n2.pool, 'BBB')
        if s.get('gamble'):
            if real:
                h = list(n2.hand); h.remove(rng.choice(h)) if h else None; n2.hand = tuple(sorted(h))
            else:
                n2.unk += 0  # planner treats Gamble as a random action (see RANDOM_ACTS)
        return n2
    if t == 'toptutor':
        if n == "Lim-Dûl's Vault": n2.life -= 5
        elif n in ('Vampiric Tutor', 'Imperial Seal'): n2.life -= 2
        shuffle_put(n2, a[2], real, rng, top=True)
        return n2
    if t == 'beseech':
        _, n, tgt, barg = a
        if barg:   # Bargain: sacrifice an artifact, enchantment or token (Oracle text)
            if n2.treas: n2.treas -= 1; n2.art -= 1
            elif n2.art - n2.acre > 0: n2.art -= 1
            elif n2.acre: n2.acre -= 1; n2.art -= 1; n2.cre -= 1
            else: return None
            if not shuffle_put(n2, tgt, real, rng, top=False): return n2
            return cast_free(n2, tgt, real, rng)
        if shuffle_put(n2, tgt, real, rng, top=False): n2.hand = h_add(n2.hand, tgt)
        return n2
    if t == 'draw':
        if s.get('look') and n2.top:
            look = list(n2.top[:s['look']])
            best = max(look, key=value)
            l = list(n2.top); l.remove(best); n2.top = (best,) + tuple(l)
        before = Counter(n2.hand)
        r = do_draw(n2, s['n'], real, rng)
        if r is None or r.won: return r
        if s.get('discard'):
            drawn = Counter(r.hand) - before
            vals = []
            for c in r.hand:
                if drawn.get(c, 0) > 0: drawn[c] -= 1; vals.append((0.5, c))
                else: vals.append((value(c, r), c))
            cands = sorted(vals + ([(0.5, '?')] * r.unk))
            for _, c in cands[:s['discard']]:
                if c == '?': r.unk -= 1
                else: r.hand = h_rem(r.hand, c)
                r.gy += 1
            return r
        if s.get('back'):
            drawn = Counter(r.hand) - before          # cards revealed by this draw (real mode only)
            vals = []
            for c in r.hand:
                if drawn.get(c, 0) > 0:
                    drawn[c] -= 1; vals.append((0.5, c))   # same rule as the planner: new cards count as unknown
                else:
                    vals.append((value(c, r), c))
            cands = sorted(vals + ([(0.5, '?')] * r.unk))
            back = [c for _, c in cands[:s['back']]]
            for c in back:
                if c == '?': r.unk -= 1
                else: r.hand = h_rem(r.hand, c); r.lib = lib_add(r.lib, c)
            if real: r.seq = tuple(back) + r.seq
            r.top = tuple(back) if '?' not in back else ()
        return r
    if t == 'adnaus':
        # Oracle text: reveal the top card, put it into hand, lose life = its mana value; repeat at will.
        # Policy: keep going while life stays >= 8 after the reveal.
        if real:
            hand = n2.hand
            while n2.seq:
                c = n2.seq[0]; mvc = CACHE[c]['cmc'] if c in CACHE else 0
                if n2.life - mvc < 8: break
                n2.life -= mvc; n2.seq = n2.seq[1:]; n2.lib = lib_remove(n2.lib, c); hand = h_add(hand, c)
            n2.hand = hand; n2.top = ()
        else:
            n2.unk += 25
        return n2
    if t == 'wheel':
        if s.get('twister'):
            if real:
                sq = list(n2.seq) + list(n2.hand); rng.shuffle(sq); n2.seq = tuple(sq)
            for c in n2.hand: n2.lib = lib_add(n2.lib, c)
            n2.top = ()
        n2.hand = (); n2.unk = 0
        return do_draw(n2, 7, real, rng)
    if t == 'oracle':
        if n2.libempty:
            n2.won = True
        else:
            n2.phase = 'oracle_pending'
        return n2
    if t == 'consult':
        if s.get('pact') and not n2.pact_ok: return None
        n2.libempty = True; n2.lib = (); n2.top = ()
        if real: n2.seq = ()
        if n2.phase == 'oracle_pending' or n2.jace:
            n2.won = True
        return n2
    if t == 'labman':
        n2.lab = True; n2.cre += 1; return n2
    if t == 'jace':
        n2.jace = True
        if n2.libempty: n2.won = True
        return n2
    raise ValueError(a)

def cast_free(n2, tgt, real, rng):
    s = S[tgt]; k = s['kind']
    if k == 'oracle':
        if n2.libempty: n2.won = True
        else: n2.phase = 'oracle_pending'
        return n2
    if k == 'consult':
        if s.get('pact') and not n2.pact_ok: return None
        n2.libempty = True; n2.lib = (); n2.top = ()
        if real: n2.seq = ()
        if n2.phase == 'oracle_pending' or n2.jace: n2.won = True
        return n2
    if k == 'labman': n2.lab = True; n2.cre += 1; return n2
    if k == 'jace':
        n2.jace = True
        if n2.libempty: n2.won = True
        return n2
    if k == 'ritual':
        n2.pool = padd(n2.pool, s['out']); return n2
    n2.hand = h_add(n2.hand, tgt)
    return n2

RANDOM_TYPES = {'draw', 'cycle', 'wheel'}
def is_random(st, a):
    t = a[0]
    if t in ('draw', 'cycle', 'wheel', 'adnaus'):
        return not st.libempty
    if t == 'ritual' and S[a[1]].get('draw'): return not st.top and not st.libempty
    if t == 'jeska' and st.cmdr: return True
    if t == 'tutor' and S[a[1]].get('gamble'): return True
    return False

# ------------------------------------------------------------------ planner
LED_KINDS = {'oracle', 'consult', 'labman', 'jace', 'draw', 'wheel', 'adnaus'}
def expand(st):
    out = []
    for a in gen_actions(st):
        for led in ((False, True) if st.led and a[0] in LED_KINDS else (False,)):
            n = apply(st, a, False, None, led)
            if n is not None:
                out.append(((a, led), n))
    return out

def H(n):
    return n.unk * 1.0 + 0.6 * sum(n.pool) + 0.4 * sum(1 for c in n.hand if value(c, n) >= 4) + 0.3 * n.art

def plan(st0, limit=4000):
    """returns ('win', path) | ('dig', path) | ('stuck', [])"""
    stack = [(st0, ())]
    seen = {st0.key()}
    best = None; nodes = 0
    while stack and nodes < limit:
        st, path = stack.pop(); nodes += 1
        for (a, led), n in expand(st):
            p2 = path + ((a, led),)
            if n.won:
                return 'win', p2
            rnd = is_random(st, a)
            if rnd and (n.unk > st0.unk or a[0] == 'tutor'):
                h = H(n) + (0 if a[0] != 'tutor' else 2)
                if best is None or h > best[0]: best = (h, p2)
                if a[0] == 'tutor':  # Gamble: outcome unknown, do not expand
                    continue
            if n.phase == 'oracle_pending' and not any(True for _ in gen_actions(n)):
                continue
            k = n.key()
            if k in seen: continue
            seen.add(k)
            stack.append((n, p2))
    if best: return 'dig', best[1]
    return 'stuck', ()

def execute(st, path, rng):
    for a, led in path:
        try:
            n = apply(st, a, True, rng, led)
        except (ValueError, KeyError):
            n = None
        if n is None:
            return None
        st = n
        if st.won: return st
    return st

def new_state(hand, seq, seat, cz, pact_ok):
    st = St.__new__(St)
    st.hand = tuple(sorted(hand)); st.unk = 0; st.top = ()
    st.lib = tuple(sorted(Counter(seq).items())); st.seq = tuple(seq)
    st.pool = (0,) * 8; st.land = False; st.art = 0; st.cre = 0; st.treas = 0; st.led = 0; st.drum = 0
    st.opal = 0; st.amber = 0; st.cmdr = False; st.cz = cz; st.lab = False; st.jace = False
    st.libempty = False; st.life = 40; st.phase = 'main'; st.won = False; st.gy = 0; st.pact_ok = pact_ok
    st.caverns = 0; st.acre = 0; st.ctax = 0
    return st

def planning_view(st):
    v = st.copy(); v.seq = None; return v

def upkeep_phase(st, rng, limit):
    """try instant-speed top-tutoring during upkeep so that the draw step gives the missing piece"""
    if not any(S.get(c, {}).get('kind') == 'toptutor' and S[c]['type'] == 'instant' for c in st.hand):
        return st
    if not (st.caverns or any(S.get(c, {}).get('kind') == 'guide' for c in st.hand)):
        return st
    up = planning_view(st); up.phase = 'upkeep'
    # small DFS over upkeep actions (no draws)
    stack = [(up, ())]; seen = set(); cands = []
    while stack:
        s, path = stack.pop()
        for (a, led), n in expand(s):
            if a[0] in ('draw', 'cycle') or is_random(s, a): continue
            p2 = path + ((a, led),)
            if a[0] == 'toptutor': cands.append((n, p2)); continue
            k = n.key()
            if k in seen or len(p2) > 4: continue
            seen.add(k); stack.append((n, p2))
    for n, p in cands:
        v = n.copy(); v.phase = 'main'; v.pool = (0,) * 8
        v = do_draw(v, 1, False, None)
        if v is None: continue
        r, _ = plan(v, limit)
        if r == 'win':
            real = st.copy(); real.phase = 'upkeep'
            real = execute(real, p, rng)
            if real is not None:
                real.phase = 'main'; real.pool = (0,) * 8
                return real
    return st

DRAW_T1 = True   # CR 103.8c (multiplayer): no player skips the first draw. False = sensitivity test only.
def play_turn(st, rng, limit=4000, max_iter=25):
    st = upkeep_phase(st, rng, limit)
    if DRAW_T1:
        st = do_draw(st, 1, True, rng)                # draw step (CR 103.8c)
    if st is None: return False
    st.phase = 'main'; st.pool = (0,) * 8
    for _ in range(max_iter):
        res, path = plan(planning_view(st), limit)
        if res == 'stuck': return False
        n = execute(st, path, rng)
        if n is None: return False
        if n.won: return True
        if res == 'win':      # should not happen (deterministic line failed in real mode)
            return False
        st = n
        st.unk = 0
    return False

# ------------------------------------------------------------------ mulligan + game
def det_score(hand, lib_list, cz, pact_ok, rng, K, limit):
    """estimate P(win | keep) = fraction of sampled draw-step cards giving a deterministic win"""
    base = new_state(hand, lib_list, 1, cz, pact_ok)
    v = planning_view(base); v.unk = 1
    if plan(v, limit)[0] == 'win':
        return 1.0
    if K == 0: return 0.0
    sample = rng.sample(lib_list, min(K, len(lib_list)))
    w = 0
    for c in sample:
        v = planning_view(base); v.hand = h_add(v.hand, c); v.lib = lib_remove(v.lib, c)
        if plan(v, limit)[0] == 'win': w += 1
    return w / len(sample)

def game(deck, seat, rng, cz=False, max_mull=3, free_mull=1, K=6, taus=(0.34, 0.2, 0.1, 0.0), limit=3000,
         return_info=False):
    pact_ok = len(set(deck)) == len(deck)
    m = 0
    pool = list(deck)                                   # cards not exiled by Serum Powder
    def bottom(seven, rest, nb):
        h = sorted(seven, key=value)
        return h[nb:], rest + h[:nb]
    while True:
        lib = list(pool); rng.shuffle(lib)
        seven, rest = lib[:7], lib[7:]
        nb = max(0, m - free_mull)                      # CR 103.5 / 103.5c
        if m >= max_mull:
            hand, rest = bottom(seven, rest, nb); break
        tau = taus[min(m, len(taus) - 1)]
        hand, r2 = bottom(seven, rest, nb)
        sc = det_score(hand, r2, cz, pact_ok, rng, K, limit)
        # Serum Powder (Oracle text): exile the 7-card hand and draw that many, in addition to mulligans
        while sc < tau and 'Serum Powder' in seven:
            for c in seven: pool.remove(c)
            rng.shuffle(rest)
            seven, rest = rest[:7], rest[7:]
            hand, r2 = bottom(seven, rest, nb)
            sc = det_score(hand, r2, cz, pact_ok, rng, K, limit)
        if sc >= tau:
            rest = r2; break
        m += 1
    st = new_state(hand, rest, seat, cz, pact_ok)
    if seat > 1 and 'Gemstone Caverns' in hand:        # Oracle text: not the starting player
        h = list(hand); h.remove('Gemstone Caverns')
        h.sort(key=lambda c: value(c, None))
        exiled = h.pop(0) if h else None
        st.hand = tuple(sorted(h)); st.caverns = 1
    win = play_turn(st, rng, limit)
    if return_info: return win, m
    return win

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)

def run(deck, seat, n, seed, cz=False, **kw):
    rng = random.Random(seed)
    w = 0
    for i in range(n):
        w += game(deck, seat, rng, cz, **kw)
    return w, n

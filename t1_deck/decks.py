"""Deck construction from verified card pool (cache) and modeled specs."""
import t1sim
from t1sim import S, CACHE

COMMANDERS = {
    'A': (['Rograkh, Son of Rohgahh', 'Silas Renn, Seeker Adept'], True),   # cz=True: Rograkh castable for {0}
    'B': (['Kenrith, the Returned King'], False),
    'C': (['Tymna the Weaver', 'Kraum, Ludevic\'s Opus'], False),
    'D': (['Silas Renn, Seeker Adept'], False),
}
# real cards included as fillers when the modeled pool is too small (not modeled -> counted as blanks)
FILLERS = ['Underworld Breach', 'Brain Freeze', 'Doomsday', 'Ad Nauseam', 'Tendrils of Agony', 'Grapeshot',
           'Necropotence', 'Faithless Looting', 'Dark Petition', 'Intuition', 'Frantic Search', 'Snap',
           'Mystic Remora', 'Rhystic Study', 'Hermit Druid', 'Power Artifact', 'Basalt Monolith', 'Walking Ballista',
           'Serum Powder', 'Mishra\'s Bauble', 'Echo of Eons', 'Gush', 'Spoils of the Vault']

def identity(cmds):
    ci = set()
    for c in cmds: ci |= set(CACHE[c]['color_identity'])
    return ci

def legal(name, ci):
    r = CACHE[name]
    return r['legalities']['commander'] == 'legal' and set(r['color_identity']) <= ci

def build(code, extra_exclude=(), fill='blank', basics_dup=False, min_lands=15):
    cmds, cz = COMMANDERS[code]
    ci = identity(cmds)
    size = 100 - len(cmds)
    nonland, lands = [], []
    for n, s in S.items():
        if n in cmds or (s['kind'] == 'blank' and n != 'Serum Powder') or n in extra_exclude: continue
        if not legal(n, ci): continue
        if s['kind'] == 'free_creature': continue
        if s['kind'] in ('land', 'fetch'): lands.append(n)
        else: nonland.append(n)
    if not cz and 'Mox Amber' in nonland: nonland.remove('Mox Amber')     # needs a legendary creature on T1
    # fetchlands only if something to fetch
    def fetchable(f):
        s = S[f]
        for l in lands:
            sl = S[l]
            if sl['kind'] != 'land': continue
            if s['types'] == 'basic':
                if sl.get('basic'): return True
            elif sl.get('dual') or sl.get('basic'):
                if set(t1sim.land_subtypes(l)) & set(s['types']): return True
        return False
    lands = [l for l in lands if S[l]['kind'] != 'fetch' or fetchable(l)]
    def lprio(l):
        s = S[l]
        if s['kind'] == 'land' and s.get('out') == 'A': return 0
        if s.get('dual'): return 1
        if s['kind'] == 'fetch': return 2
        if l in ('Ancient Tomb', 'Gemstone Caverns'): return 3
        if s.get('basic'): return 4
        return 5
    lands.sort(key=lambda l: (lprio(l), l))
    nonland.sort(key=lambda n: -t1sim.value(n))
    nonland = nonland[:size - min_lands]
    deck = nonland + lands[:size - len(nonland)]
    fillers = [f for f in FILLERS if f in CACHE and legal(f, ci) and f not in deck]
    while len(deck) < size and fill == 'blank' and fillers:
        deck.append(fillers.pop(0))
    basics = [b for b in ['Island', 'Swamp', 'Mountain', 'Forest', 'Plains'] if b in deck]
    i = 0
    while len(deck) < size:
        deck.append(basics[i % len(basics)]); i += 1
    return deck, cmds, cz

if __name__ == '__main__':
    for code in 'ABCD':
        d, cmds, cz = build(code)
        nl = [c for c in d if c in S and S[c]['kind'] not in ('land', 'fetch')]
        ld = [c for c in d if c in S and S[c]['kind'] in ('land', 'fetch')]
        bl = [c for c in d if c not in S]
        print(code, cmds, len(d), 'modeled nonland', len(nl), 'lands', len(ld), 'fillers', len(bl), 'unique', len(set(d)) == len(d))

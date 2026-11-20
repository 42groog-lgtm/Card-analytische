"""Step 5: card-by-card control of the 100 cards with a FRESH Scryfall query (not the cache)."""
import json, re, urllib.request, time, html
names, cmds, section = [], [], None
for line in open('decklist.txt'):
    line = line.strip()
    if line in ('Commander', 'Deck'): section = line; continue
    if not line: continue
    n = line.split(' ', 1)[1]
    (cmds if section == 'Commander' else names).append(n)
allc = cmds + names
fresh = {}
for i in range(0, len(allc), 70):
    body = json.dumps({'identifiers': [{'name': n} for n in allc[i:i + 70]]}).encode()
    req = urllib.request.Request('https://api.scryfall.com/cards/collection', data=body,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'deckcheck/1.0'})
    d = json.load(urllib.request.urlopen(req))
    assert not d.get('not_found'), d['not_found']
    for c in d['data']: fresh[c['name']] = c
    time.sleep(0.15)
def rec(n):
    for k, v in fresh.items():
        if k == n or k.split(' // ')[0] == n: return v
    raise KeyError(n)
cache = json.load(open('cache/cards.json'))
# official ban list and game changers (Wizards pages saved in sources/)
t = open('sources/banned-restricted-list.txt').read()
seg = t[t.find('Commander Banned Cards'):t.find('Pauper Banned Cards')]
banned = {l.strip() for l in seg.split('\n') if l.strip() and len(l.strip()) < 40}
gc = {c for v in json.load(open('sources/game_changers_wizards.json')).values() for c in v['cards']}
ci = set()
for c in cmds: ci |= set(rec(c)['color_identity'])
rows, problems = [], []
for n in allc:
    r = rec(n)
    oracle = r.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in r.get('card_faces', []))
    ok_leg = r['legalities']['commander'] == 'legal'
    ok_ci = set(r['color_identity']) <= ci
    ok_ban = n not in banned
    same = cache.get(n, {}).get('oracle_text') == r.get('oracle_text')
    is_gc = n in gc
    rows.append((n, ''.join(r['color_identity']) or 'C', r['legalities']['commander'], is_gc, ok_ci, ok_ban, same))
    if not (ok_leg and ok_ci and ok_ban): problems.append(n)   # empty Oracle text = vanilla creature (Memnite, Phyrexian Walker)
basics = {'Island', 'Swamp', 'Mountain', 'Forest', 'Plains', 'Wastes'}
dups = [n for n in set(allc) if allc.count(n) > 1 and n not in basics]
partner = all('Partner' in (rec(c).get('oracle_text') or '') for c in cmds) if len(cmds) == 2 else True
with open('controle_final.md', 'w') as f:
    f.write(f'# Contrôle final ({time.strftime("%Y-%m-%d")}, requête Scryfall fraîche)\n\n')
    f.write(f'- Cartes : {len(allc)} (commandants : {len(cmds)}) ; singleton hors bases : {"OK" if not dups else dups}\n')
    f.write(f'- Identité des commandants : {"".join(sorted(ci))} ; Partner sur les deux commandants : {partner}\n')
    f.write(f'- Problèmes (légalité, identité, banlist, texte manquant) : {problems or "aucun"}\n')
    f.write(f'- Game Changers (liste officielle) : {sum(1 for r in rows if r[3])} : {", ".join(r[0] for r in rows if r[3])}\n\n')
    f.write('| Carte | Identité | Commander | GC | Identité OK | Pas bannie | Oracle = cache |\n|---|---|---|---|---|---|---|\n')
    for r in rows:
        f.write(f'| {r[0]} | {r[1]} | {r[2]} | {"oui" if r[3] else ""} | {"OK" if r[4] else "NON"} | {"OK" if r[5] else "NON"} | {"OK" if r[6] else "diff"} |\n')
print('cards', len(allc), 'problems', problems, 'dups', dups, 'partner', partner, 'GC', sum(1 for r in rows if r[3]),
      'oracle diffs', [r[0] for r in rows if not r[6]])

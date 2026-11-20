"""Scryfall card cache: every card used must come from here (never from memory)."""
import json, os, time, urllib.request, sys
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'cards.json')
FIELDS = ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text', 'color_identity', 'legalities', 'game_changer',
          'reserved', 'layout', 'card_faces', 'power', 'toughness', 'keywords', 'scryfall_uri', 'id']

def load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def fetch(names):
    cache = load()
    need = [n for n in names if n not in cache]
    missing = []
    for i in range(0, len(need), 70):
        body = json.dumps({'identifiers': [{'name': n} for n in need[i:i + 70]]}).encode()
        req = urllib.request.Request('https://api.scryfall.com/cards/collection', data=body,
                                     headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                              'User-Agent': 'deckcheck/1.0'})
        d = json.load(urllib.request.urlopen(req))
        for c in d['data']:
            rec = {k: c.get(k) for k in FIELDS}
            rec['fetched'] = time.strftime('%Y-%m-%d')
            # map requested name (front face or full) to record
            for n in need[i:i + 70]:
                if n == c['name'] or n == c['name'].split(' // ')[0]:
                    cache[n] = rec
        missing += [x.get('name') for x in d.get('not_found', [])]
        time.sleep(0.15)
    json.dump(cache, open(CACHE, 'w'), indent=1, ensure_ascii=False)
    return cache, missing

def oracle(rec):
    if rec.get('oracle_text') is not None:
        return rec['oracle_text']
    return ' // '.join(f"{f['name']}: {f.get('oracle_text','')}" for f in rec.get('card_faces') or [])

if __name__ == '__main__':
    names = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    cache, missing = fetch(names)
    print('missing:', missing)
    for n in names:
        r = cache.get(n)
        if not r: continue
        print(f"## {r['name']} | {r['mana_cost'] or (r['card_faces'][0]['mana_cost'] if r.get('card_faces') else '')} | {r['type_line']} | CI={''.join(r['color_identity'])} | cmd={r['legalities']['commander']} | GC={r.get('game_changer')}")
        print('   ' + oracle(r).replace('\n', ' / '))

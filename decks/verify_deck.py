# Vérifie une decklist Commander : structure, légalité, identité couleur, Game Changers,
# MLD / tours supplémentaires, combos et bracket estimé (Scryfall + Commander Spellbook).
# Usage : python3 decks/verify_deck.py decks/korvold-bracket3.txt /tmp/rapport.json
import json, re, sys, time, urllib.request, urllib.parse
H={"Accept":"application/json","User-Agent":"deckcheck/1.0"}
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=H)))
def post(url,p):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(p).encode(),headers={**H,"Content-Type":"application/json"})))
def search_all(q):
    url="https://api.scryfall.com/cards/search?"+urllib.parse.urlencode({"q":q,"unique":"cards"}); out=[]
    while url:
        d=get(url); out+= [c["name"] for c in d["data"]]; url=d.get("next_page"); time.sleep(0.12)
    return set(out)
# --- parse
cmd, main, sec = [], [], None
for line in open(sys.argv[1]):
    line=line.strip()
    if not line: continue
    if line in ("Commander","Deck"): sec=line; continue
    n,name=re.match(r"(\d+)\s+(.+)",line).groups()
    (cmd if sec=="Commander" else main).append((int(n),name))
BASICS={"Forest","Swamp","Mountain","Island","Plains","Wastes"}
allc=cmd+main; names=[n for _,n in allc]
report={}
# PASS 0: structure
total=sum(q for q,_ in allc)
nonsingle=[n for q,n in allc if q>1 and n not in BASICS]+[n for n in set(names) if names.count(n)>1]
report["P0 structure"]=f"total={total} (attendu 100), commandants={len(cmd)}, non-singleton={nonsingle or 'aucun'}"
# PASS 1: Scryfall /cards/collection (bulk)
coll={}
for i in range(0,len(names),75):
    r=post("https://api.scryfall.com/cards/collection",{"identifiers":[{"name":n} for n in names[i:i+75]]})
    assert not r["not_found"], r["not_found"]
    for asked,c in zip(names[i:i+75],r["data"]): coll[asked]=c
    time.sleep(0.12)
full=lambda n: coll[n]["name"]
cmdr=coll[cmd[0][1]]; CI=set(cmdr["color_identity"])
p1_ban=[n for n,c in coll.items() if c["legalities"]["commander"]!="legal"]
p1_ci=[(n,c["color_identity"]) for n,c in coll.items() if not set(c["color_identity"])<=CI]
p1_gc=sorted(n for n,c in coll.items() if c.get("game_changer"))
p1_cmdr_ok = "Legendary" in cmdr["type_line"] and "Creature" in cmdr["type_line"]
report["P1 Scryfall collection"]=f"identité commandant={''.join(sorted(CI))}, commandant légendaire créature={p1_cmdr_ok}, non légales={p1_ban or 'aucune'}, hors couleurs={p1_ci or 'aucune'}, GC={p1_gc}"
# PASS 2: Scryfall per-card exact query (independent endpoint)
p2_fail=[]; p2_gc=[]
for n in dict.fromkeys(names):
    if n in BASICS: continue
    q=f'!"{n}" legal:commander id<={"".join(sorted(CI)).lower()}'
    try: d=get("https://api.scryfall.com/cards/search?"+urllib.parse.urlencode({"q":q}))
    except urllib.error.HTTPError: p2_fail.append(n); time.sleep(0.12); continue
    if n not in [c["name"] for c in d["data"]] and not any(c["name"].split(" // ")[0]==n for c in d["data"]): p2_fail.append(n)
    try:
        g=get("https://api.scryfall.com/cards/search?"+urllib.parse.urlencode({"q":f'!"{n}" is:gamechanger'}))
        if any(c["name"]==n or c["name"].split(" // ")[0]==n for c in g["data"]): p2_gc.append(n)
    except urllib.error.HTTPError: pass
    time.sleep(0.12)
report["P2 Scryfall carte par carte (!nom legal:commander id<=identité ; is:gamechanger)"]=f"échecs={p2_fail or 'aucun'}, GC={sorted(p2_gc)}"
# PASS 3: Scryfall global lists intersect
banned=search_all("banned:commander"); gcs=search_all("is:gamechanger")
deckset={full(n) for n in names}
report["P3 Scryfall listes globales"]=f"bannies Commander={len(banned)} cartes -> dans le deck: {sorted(deckset&banned) or 'aucune'} ; GC={len(gcs)} cartes -> dans le deck: {sorted(deckset&gcs)}"
# PASS 4: Commander Spellbook estimate-bracket
b=post("https://backend.commanderspellbook.com/estimate-bracket",{"commanders":[{"card":full(n),"quantity":q} for q,n in cmd],"main":[{"card":full(n),"quantity":q} for q,n in main]})
sb_names={c["card"]["name"] for c in b["cards"]}
report["P4 Spellbook"]=f"cartes reconnues={len(sb_names)}/{len(set(names))}, manquantes={sorted({full(n) for n in set(names)}-sb_names) or 'aucune'}, bannies={[c['card']['name'] for c in b['cards'] if c['banned']] or 'aucune'}, GC={sorted(c['card']['name'] for c in b['cards'] if c['gameChanger'])}, MLD={[c['card']['name'] for c in b['cards'] if c['massLandDenial']] or 'aucune'}, tours sup.={[c['card']['name'] for c in b['cards'] if c['extraTurn']] or 'aucun'}, bracket={b['bracketTag']}"
# PASS 5: oracle text heuristics (MLD / extra turns) on Scryfall text
txt=lambda c: (c.get("oracle_text") or " ".join(f.get("oracle_text","") for f in c.get("card_faces",[]))).lower()
mld=[n for n,c in coll.items() if re.search(r"destroy all lands|destroy all .*lands|each player sacrifices .*lands|lands don't untap",txt(c))]
xt=[n for n,c in coll.items() if "extra turn" in txt(c)]
report["P5 texte Oracle"]=f"MLD={mld or 'aucune'}, tours sup.={xt or 'aucun'}"
for k,v in report.items(): print(f"[{k}]\n  {v}")
fm=post("https://backend.commanderspellbook.com/find-my-combos",{"commanders":[{"card":full(n),"quantity":q} for q,n in cmd],"main":[{"card":full(n),"quantity":q} for q,n in main]})
json.dump(fm,open(sys.argv[2]+".combos.json","w"),indent=1)
print("[P6 Spellbook find-my-combos]\n  inclus:",len(fm["results"]["included"]),"| ids:",sorted(c["id"] for c in fm["results"]["included"]))
json.dump(report,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)

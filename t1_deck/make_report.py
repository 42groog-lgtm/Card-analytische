"""Builds rapport.md from the result files produced by the scripts (no number is typed by hand)."""
import json, os, time
import decks
from t1sim import S

H = os.path.dirname(os.path.abspath(__file__))
res = [json.loads(l) for l in open(os.path.join(H, 'results.jsonl'))]
sens = json.load(open(os.path.join(H, 'sensitivity.json'))) if os.path.exists(os.path.join(H, 'sensitivity.json')) else None
val = open(os.path.join(H, 'validation.txt')).read()
gc_off = {c for v in json.load(open(os.path.join(H, 'sources', 'game_changers_wizards.json'))).values() for c in v['cards']}
d, cmds, cz = decks.build('A')
gcs = sorted(c for c in d + cmds if c in gc_off)
unmodeled = sorted(c for c in d if c not in S or S[c]['kind'] == 'blank')

def pct(x): return f'{100 * x:.3f} %'.replace('.', ',')
def nn(n): return f'{n:,}'.replace(',', ' ')
def one_in(p): return f'1 sur {1 / p:,.0f}'.replace(',', ' ') if p > 0 else '—'
def get(label, seat=1, deck='A'):
    for r in res:
        if r['label'] == label and r['seat'] == seat and r.get('deck', 'A') == deck: return r
    return None

L = []
L.append('# Rapport : deck Commander optimisé pour gagner au tour 1\n')
L.append(f'Généré le {time.strftime("%Y-%m-%d")} par `make_report.py` à partir de `results.jsonl`, `sensitivity.json` et `validation.txt`.\n')
L.append('## Résultat principal\n')
L.append(f'Commandants : **{" + ".join(cmds)}** (identité bleu-noir-rouge). Decklist : `decklist.txt`.\n')
L.append('| Place | Mulligans | P(victoire T1) | IC 95 % | Simulations |\n|---|---|---|---|---|')
for label, name in [('sans_mulligan', 'aucun'), ('mulligan_officiel_1_gratuit', '1 gratuit (règle officielle)')]:
    for seat in (1, 2, 3, 4):
        r = get(label, seat if seat <= 2 else 2)
        if not r: continue
        note = '' if seat <= 2 else ' (= place 2, voir hypothèses)'
        L.append(f'| {seat}{note} | {name} | **{pct(r["p"])}** ({one_in(r["p"])}) | [{pct(r["lo"])} ; {pct(r["hi"])}] | {nn(r["n"])} |')
L.append('\nLes places 2, 3 et 4 sont strictement équivalentes dans le modèle : la seule différence entre places est Gemstone Caverns, utilisable par tout joueur qui ne commence pas. La place 1 est la moins favorable ; c\'est sur elle que le deck a été optimisé.\n')

L.append('## Règles vérifiées (sources officielles)\n')
L.append(open(os.path.join(H, 'sources', 'REGLES.md')).read().split('\n', 1)[1])
L.append('\n## Game Changers utilisés\n')
L.append(f'{len(gcs)} cartes de la liste officielle Wizards : ' + ', '.join(gcs) + '.\n')

L.append('## Comparaison des commandants (sans mulligan, place 1)\n')
L.append('| Option | Commandant(s) | P(victoire T1) | IC 95 % | Simulations |\n|---|---|---|---|---|')
names = {'A': 'Rograkh + Silas Renn (UBR)', 'B': 'Kenrith, the Returned King (5 couleurs)', 'C': 'Tymna + Kraum (WUBR)', 'D': 'Silas Renn seul (UB)'}
rA = get('sans_mulligan', 1, 'A')
if rA: L.append(f'| A | {names["A"]} | **{pct(rA["p"])}** | [{pct(rA["lo"])} ; {pct(rA["hi"])}] | {nn(rA["n"])} |')
for code in 'BCD':
    r = get('cmp_sans_mulligan', 1, code)
    if r: L.append(f'| {code} | {names[code]} | {pct(r["p"])} | [{pct(r["lo"])} ; {pct(r["hi"])}] | {nn(r["n"])} |')
L.append('\nChaque option utilise toutes les cartes modélisées légales dans son identité. L\'avantage de A vient surtout de Rograkh, créature à {0} qui alimente Culling the Weak, Springleaf Drum, Mox Amber, Diabolic Intent et les deux modes de Jeska\'s Will.\n')

L.append('## Analyse de sensibilité\n')
L.append('| Variante | P(victoire T1) | IC 95 % | Simulations |\n|---|---|---|---|')
for label, name in [('sensib_pas_de_pioche_T1', 'Pas de pioche au tour 1 (règle 2 joueurs, pour comparaison)'),
                    ('sensib_london_jusqua_6', '1 mulligan gratuit puis London jusqu\'à 6 cartes'),
                    ('sensib_2_mulligans_gratuits', '2 mulligans gratuits (règle maison)')]:
    r = get(label, 1)
    if r: L.append(f'| {name} | {pct(r["p"])} | [{pct(r["lo"])} ; {pct(r["hi"])}] | {nn(r["n"])} |')
if sens:
    L.append(f'\n### Perte d\'une pièce clé (comparaison appariée, mêmes mélanges, sans mulligan, {nn(sens["n"])} parties)\n')
    L.append(f'Deck de base : {sens["base_wins"]} victoires ({pct(sens["base_wins"] / sens["n"])}).\n')
    L.append('| Carte retirée (remplacée par une carte vide) | Victoires | Écart | Parties perdues / gagnées en plus | z |\n|---|---|---|---|---|')
    for v in sens['variants']:
        L.append(f'| {v["swap"].split(" -> ")[0]} | {v["wins"]} | {100 * (v["wins"] - sens["base_wins"]) / max(1, sens["base_wins"]):+.0f} % | {v["base_only"]} / {v["variant_only"]} | {v["z"]:.1f} |')
    nr = sens['no_rograkh']
    L.append(f'| Rograkh non lançable (commandant inutilisé) | {nr["wins"]} | {100 * (nr["wins"] - sens["base_wins"]) / max(1, sens["base_wins"]):+.0f} % | (simulation non appariée) | |')

L.append('\n## Validation du simulateur\n')
L.append('Decks-tests dont la probabilité de victoire au tour 1 est calculée exactement (hypergéométrique multivariée), comparée à 100 000 simulations :\n')
L.append('```\n' + val.strip() + '\n```\n')

L.append('## Hypothèses et limites du modèle\n')
L.append('- 3 adversaires passifs à 40 PV, aucun bloqueur ni interaction ; au moins un adversaire a 7 cartes en main (Jeska\'s Will, Windfall).')
L.append('- Victoire = victoire alternative de Thassa\'s Oracle, Laboratory Maniac ou Jace, Wielder of Mysteries avec la bibliothèque vide (Demonic Consultation en nommant une carte absente du deck, ou Tainted Pact, valable car aucune carte n\'est en double).')
L.append('- Le joueur simulé ne regarde jamais l\'ordre de la bibliothèque : il cherche toutes les lignes avec les cartes connues, joue une ligne gagnante s\'il en trouve une, sinon la meilleure ligne qui pioche ou révèle des cartes, puis recommence. Recherche limitée à 2 000 états par décision : des lignes gagnantes très longues peuvent être manquées.')
L.append('- Mulligan heuristique : on garde une main si elle gagne avec la pioche inconnue, ou si au moins une des 4 cartes de pioche tirées au hasard la fait gagner ; sinon mulligan. Les cartes mises au-dessous sont celles de plus faible valeur.')
L.append('- Simplifications : Lion\'s Eye Diamond produit trois mana « de n\'importe quelle couleur » au lieu de trois mana d\'une seule couleur ; Ponder, Preordain, Opt et Consider sont modélisés comme « prendre la meilleure carte parmi celles vues » ; Lim-Dûl\'s Vault coûte 5 PV ; Gamble défausse au hasard dans la main réelle ; Cabal Ritual sans seuil ; les cartes défaussées ne comptent pas pour Dark Petition.')
L.append(f'- Cartes du deck non modélisées (comptées comme cartes vides) : {", ".join(unmodeled)}. Elles peuvent avoir une utilité réelle (Underworld Breach, Doomsday…) : les probabilités sont donc un **minimum**.')
L.append('- Graines fixes indiquées dans `results.jsonl` ; tout se relance avec les commandes de la section suivante.\n')

L.append('## Historique des changements et effet sur P(victoire T1)\n')
L.append('| Étape | Modification | Effet mesuré |\n|---|---|---|')
for row in json.load(open(os.path.join(H, 'historique.json'))):
    L.append(f'| {row[0]} | {row[1]} | {row[2]} |')

L.append('\n## Reproduire les chiffres\n')
L.append('```bash\ncd t1_deck\npython3 validate.py 100000\npython3 final_run.py sans_mulligan 1 100000 201 \'{"max_mull":0}\'\npython3 final_run.py mulligan_officiel_1_gratuit 1 100000 202 \'{"max_mull":1,"free_mull":1,"K":4,"taus":[0.01]}\'\npython3 sensitivity.py 60000\npython3 final_check.py\n```')
open(os.path.join(H, 'rapport.md'), 'w').write('\n'.join(L) + '\n')
print('rapport.md written')

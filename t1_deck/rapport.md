# Rapport : deck Commander optimisé pour gagner au tour 1

Généré le 2026-11-20 par `make_report.py` à partir de `results.jsonl`, `sensitivity.json` et `validation.txt`.

## Résultat principal

Commandants : **Rograkh, Son of Rohgahh + Silas Renn, Seeker Adept** (identité bleu-noir-rouge). Decklist : `decklist.txt`.

| Place | Mulligans | P(victoire T1) | IC 95 % | Simulations |
|---|---|---|---|---|
| 1 | aucun | **0,235 %** (1 sur 426) | [0,207 % ; 0,267 %] | 100 000 |
| 2 | aucun | **0,251 %** (1 sur 398) | [0,222 % ; 0,284 %] | 100 000 |
| 3 (= place 2, voir hypothèses) | aucun | **0,251 %** (1 sur 398) | [0,222 % ; 0,284 %] | 100 000 |
| 4 (= place 2, voir hypothèses) | aucun | **0,251 %** (1 sur 398) | [0,222 % ; 0,284 %] | 100 000 |
| 1 | 1 gratuit (règle officielle) | **0,332 %** (1 sur 301) | [0,298 % ; 0,370 %] | 100 000 |
| 2 | 1 gratuit (règle officielle) | **0,366 %** (1 sur 273) | [0,330 % ; 0,405 %] | 100 000 |
| 3 (= place 2, voir hypothèses) | 1 gratuit (règle officielle) | **0,366 %** (1 sur 273) | [0,330 % ; 0,405 %] | 100 000 |
| 4 (= place 2, voir hypothèses) | 1 gratuit (règle officielle) | **0,366 %** (1 sur 273) | [0,330 % ; 0,405 %] | 100 000 |

Les places 2, 3 et 4 sont strictement équivalentes dans le modèle : la seule différence entre places est Gemstone Caverns, utilisable par tout joueur qui ne commence pas. La place 1 est la moins favorable ; c'est sur elle que le deck a été optimisé.

## Règles vérifiées (sources officielles)


Sources :
- Comprehensive Rules, en vigueur au 6 novembre 2026 : https://media.wizards.com/2026/downloads/MagicCompRules%2020261106.txt (copie locale : sources/CR_20261106.txt)
- Banned & Restricted officiel : https://magic.wizards.com/en/banned-restricted-list (copie : sources/banned-restricted-list.html)
- Annonce Commander du 9 février 2026 : https://magic.wizards.com/en/news/announcements/commander-banned-and-restricted-february-9-2026
- Annonce B&R du 12 octobre 2026 (aucune section Commander ; les bannissements « as a commander » concernent Competitive Brawl) : https://magic.wizards.com/en/news/announcements/banned-and-restricted-october-12-2026
- Page format Commander / Game Changers : https://magic.wizards.com/en/formats/commander (liste extraite : sources/game_changers_wizards.json)

1. Pioche T1 : CR 103.8a (2 joueurs : le premier saute sa pioche), 103.8c (« In all other multiplayer games, no player skips the draw step of their first turn »). Toutes les places piochent : 7 + 1 = 8 cartes vues.
   Adversaires passifs : ils piochent à leur tour puis défaussent à 7 au nettoyage (CR 402.2, 514.1).
   Seule différence de place identifiée : Gemstone Caverns ne marche que si l'on n'est pas joueur de départ (texte Oracle).
2. Mulligan : CR 103.5 (London : on repioche 7 et on met au-dessous autant de cartes que de mulligans), 103.5c (multijoueur : le premier mulligan ne compte pas).
3. Commander : 903.5a (100 cartes, commandant inclus), 903.5b (singleton sauf terrains de base), 903.5c-d (identité de couleur), 903.4 (définition de l'identité), 903.7 (40 PV, main de 7), 903.8 (taxe : +{2} par lancement précédent depuis la zone de commandement).
4. Banlist Commander (page officielle) : Ancestral Recall, Balance, Black Lotus, Chaos Orb, Channel, Dockside Extortionist, Emrakul the Aeons Torn, Erayo Soratami Ascendant, Falling Star, Fastbond, Flash, Golos Tireless Pilgrim, Griselbrand, Hullbreacher, Iona Shield of Emeria, Karakas, Jeweled Lotus, Leovold Emissary of Trest, Library of Alexandria, Limited Resources, Mana Crypt, Mox Emerald, Mox Jet, Mox Pearl, Mox Ruby, Mox Sapphire, Nadu Winged Wisdom, Paradox Engine, Primeval Titan, Prophet of Kruphix, Recurring Nightmare, Rofellos Llanowar Emissary, Shahrazad, Sundering Titan, Sylvan Primordial, Time Vault, Time Walk, Tinker, Tolarian Academy, Trade Secrets, Upheaval, Yawgmoth's Bargain ; + cartes Conspiracy, ante, cartes offensantes ; Lutri banni uniquement comme compagnon.
   Dernière annonce Commander trouvée : 9 février 2026. L'entrée CMS « Format | Commander | B&R » a été modifiée le 2026-04-03. Prochaine annonce B&R : 30 novembre 2026.
5. Game Changers : 53 cartes (sources/game_changers_wizards.json), entrées mises à jour entre le 2025-10-22 et le 2026-02-09.


## Game Changers utilisés

16 cartes de la liste officielle Wizards : Ad Nauseam, Ancient Tomb, Chrome Mox, Demonic Tutor, Gamble, Grim Monolith, Imperial Seal, Jeska's Will, Lion's Eye Diamond, Mana Vault, Mishra's Workshop, Mox Diamond, Mystical Tutor, Thassa's Oracle, Underworld Breach, Vampiric Tutor.

## Comparaison des commandants (sans mulligan, place 1)

| Option | Commandant(s) | P(victoire T1) | IC 95 % | Simulations |
|---|---|---|---|---|
| A | Rograkh + Silas Renn (UBR) | **0,235 %** | [0,207 % ; 0,267 %] | 100 000 |
| B | Kenrith, the Returned King (5 couleurs) | 0,169 % | [0,145 % ; 0,196 %] | 100 000 |
| C | Tymna + Kraum (WUBR) | 0,144 % | [0,122 % ; 0,169 %] | 100 000 |
| D | Silas Renn seul (UB) | 0,064 % | [0,050 % ; 0,082 %] | 100 000 |

Chaque option utilise toutes les cartes modélisées légales dans son identité. L'avantage de A vient surtout de Rograkh, créature à {0} qui alimente Culling the Weak, Springleaf Drum, Mox Amber, Diabolic Intent et les deux modes de Jeska's Will.

## Analyse de sensibilité

| Variante | P(victoire T1) | IC 95 % | Simulations |
|---|---|---|---|
| Pas de pioche au tour 1 (règle 2 joueurs, pour comparaison) | 0,114 % | [0,088 % ; 0,148 %] | 50 000 |
| 1 mulligan gratuit puis London jusqu'à 6 cartes | 0,286 % | [0,243 % ; 0,337 %] | 50 000 |
| 2 mulligans gratuits (règle maison) | 0,398 % | [0,346 % ; 0,457 %] | 50 000 |

### Perte d'une pièce clé (comparaison appariée, mêmes mélanges, sans mulligan, 60 000 parties)

Deck de base : 154 victoires (0,257 %).

| Carte retirée (remplacée par une carte vide) | Victoires | Écart | Parties perdues / gagnées en plus | z |
|---|---|---|---|---|
| Lion's Eye Diamond | 25 | -84 % | 129 / 0 | -11.4 |
| Culling the Weak | 78 | -49 % | 80 / 4 | -8.3 |
| Thassa's Oracle | 88 | -43 % | 70 / 4 | -7.7 |
| Demonic Consultation | 67 | -56 % | 87 / 0 | -9.3 |
| Tainted Pact | 114 | -26 % | 44 / 4 | -5.8 |
| Ad Nauseam | 92 | -40 % | 63 / 1 | -7.8 |
| Beseech the Mirror | 125 | -19 % | 35 / 6 | -4.5 |
| Demonic Tutor | 134 | -13 % | 24 / 4 | -3.8 |
| Rograkh non lançable (commandant inutilisé) | 78 | -49 % | (simulation non appariée) | |

## Validation du simulateur

Decks-tests dont la probabilité de victoire au tour 1 est calculée exactement (hypergéométrique multivariée), comparée à 100 000 simulations :

```
T1 10 Oracle + 10 Consult, 30 City of Brass, 10 Lotus Petal
   exact = 0.03854   sim = 0.03827  IC95 [0.03710, 0.03948]  n=100000  OK  (6s)
T2 = T1 + 5 Dark Ritual (ne doit rien changer : BBB ne paie pas UU)
   exact = 0.03854   sim = 0.03827  IC95 [0.03710, 0.03948]  n=100000  OK  (8s)
T4 10 Oracle + 10 Consult + 10 Demonic Tutor, 30 City, 10 Petal
   exact = 0.03894   sim = 0.03928  IC95 [0.03809, 0.04050]  n=100000  OK  (12s)
T3 = T1 + 6 Worldly Tutor + 6 Elvish Spirit Guide (entretien)
   exact = 0.04020   sim = 0.04115  IC95 [0.03994, 0.04240]  n=100000  OK  (12s)
```

## Hypothèses et limites du modèle

- 3 adversaires passifs à 40 PV, aucun bloqueur ni interaction ; au moins un adversaire a 7 cartes en main (Jeska's Will, Windfall).
- Victoire = victoire alternative de Thassa's Oracle, Laboratory Maniac ou Jace, Wielder of Mysteries avec la bibliothèque vide (Demonic Consultation en nommant une carte absente du deck, ou Tainted Pact, valable car aucune carte n'est en double).
- Le joueur simulé ne regarde jamais l'ordre de la bibliothèque : il cherche toutes les lignes avec les cartes connues, joue une ligne gagnante s'il en trouve une, sinon la meilleure ligne qui pioche ou révèle des cartes, puis recommence. Recherche limitée à 2 000 états par décision : des lignes gagnantes très longues peuvent être manquées.
- Mulligan heuristique : on garde une main si elle gagne avec la pioche inconnue, ou si au moins une des 4 cartes de pioche tirées au hasard la fait gagner ; sinon mulligan. Les cartes mises au-dessous sont celles de plus faible valeur.
- Simplifications : Lion's Eye Diamond produit trois mana « de n'importe quelle couleur » au lieu de trois mana d'une seule couleur ; Ponder, Preordain, Opt et Consider sont modélisés comme « prendre la meilleure carte parmi celles vues » ; Lim-Dûl's Vault coûte 5 PV ; Gamble défausse au hasard dans la main réelle ; Cabal Ritual sans seuil ; les cartes défaussées ne comptent pas pour Dark Petition.
- Cartes du deck non modélisées (comptées comme cartes vides) : Brain Freeze, Doomsday, Grapeshot, Serum Powder, Tendrils of Agony, Underworld Breach. Elles peuvent avoir une utilité réelle (Underworld Breach, Doomsday…) : les probabilités sont donc un **minimum**.
- Graines fixes indiquées dans `results.jsonl` ; tout se relance avec les commandes de la section suivante.

## Historique des changements et effet sur P(victoire T1)

| Étape | Modification | Effet mesuré |
|---|---|---|
| v1 | Deck A initial : toutes les cartes modélisées légales en UBR + cartes de remplissage ; modèle : Oracle/Lab/Jace + Consultation/Pact, mana rapide, tutors, pioches | 0,150 % sans mulligan, place 1 (8 000 parties) |
| v2 | Ajout des mulligans (1 gratuit puis London jusqu'à 3) | 0,350 % (8 000 parties) |
| v2b | Réglage du mulligan : 1 seul mulligan gratuit, puis on garde | 0,337 % (8 000 parties), écart non significatif avec v2 ; règle retenue car plus simple |
| v3 | Ad Nauseam modélisé (il était compté comme carte vide) | 0,287 % sans mulligan (24 000 parties), contre ~0,15 % avant |
| v4 | Faithless Looting, Dark Petition et Mishra's Workshop modélisés ; Workshop ajouté à la place d'une carte vide | 0,346 % sans mulligan (24 000 parties) |
| v5 | Correction d'erreur : taxe de commandant (+{2}) quand Rograkh est relancé après un sacrifice (CR 903.8) | 0,267 % sans mulligan (24 000 parties) |
| v6 | Corrections d'erreurs : Lotus Petal sacrifié ne compte plus comme artefact ; une créature sacrifiée au bargain n'est plus réutilisable ; Transmute et Laboratory Maniac corrigés | 0,283 % sans mulligan (24 000 parties) ; chiffres finaux ci-dessus |

## Reproduire les chiffres

```bash
cd t1_deck
python3 validate.py 100000
python3 final_run.py sans_mulligan 1 100000 201 '{"max_mull":0}'
python3 final_run.py mulligan_officiel_1_gratuit 1 100000 202 '{"max_mull":1,"free_mull":1,"K":4,"taus":[0.01]}'
python3 sensitivity.py 60000
python3 final_check.py
```

# Korvold, Fae-Cursed King — Jund Aristocrats (Bracket 3 haut / « 3++ »)

Liste importable : [`korvold-bracket3.txt`](korvold-bracket3.txt) (format Arena/MTGO, sections Commander/Deck).

## Vérifications (10 nov. 2026) — contrôle multiple

Script : [`verify_deck.py`](verify_deck.py) (`python3 decks/verify_deck.py decks/korvold-bracket3.txt /tmp/rapport.json`).
Lancé **3 fois**, avec des résultats identiques à chaque fois. Chaque point est contrôlé par plusieurs méthodes différentes :

| Point | Méthodes | Résultat |
|---|---|---|
| Structure | décompte du fichier | 100 cartes, 1 commandant (créature légendaire), singleton hors bases |
| Banlist | ① `legalities.commander` (Scryfall, en lot) ② requête `!"nom" legal:commander` carte par carte ③ intersection avec `banned:commander` (83 cartes) ④ indicateur `banned` de Spellbook | **0 carte bannie** (4/4) |
| Identité couleur | ① `color_identity` de chaque carte ⊆ celle de Korvold (BGR) ② requête `id<=bgr` carte par carte | **0 carte hors couleurs** (2/2) |
| Game Changers | ① indicateur `game_changer` (Scryfall, en lot) ② `!"nom" is:gamechanger` carte par carte ③ intersection avec `is:gamechanger` (53 cartes) ④ indicateur `gameChanger` de Spellbook | **3** : Demonic Tutor, The One Ring, Orcish Bowmasters (4/4) |
| Destruction massive de terrains / tours supplémentaires | ① indicateurs Spellbook ② recherche dans le texte Oracle | aucune (2/2) |
| Combos / bracket | Spellbook `find-my-combos` + `estimate-bracket`, noms complets des cartes double face | 13 combos, bracket « S » |

Limites honnêtes :
- **Listes officielles non consultées :** magic.wizards.com et mtgcommander.net sont bloqués par le réseau de cette session. Les listes de référence viennent donc de Scryfall et de Spellbook, qui se basent probablement sur les mêmes données officielles : les méthodes sont différentes, mais les sources ne sont pas totalement indépendantes. Le nombre de 53 Game Changers concorde avec plusieurs guides tiers de 2026.
- **Deux erreurs corrigées pendant les contrôles :** ① un faux positif sur Demonic Tutor, dû à l'existence d'une autre carte « Emeritus of Woe // Demonic Tutor » (la vraie carte est bien légale) ; ② au premier passage, Spellbook ne reconnaissait pas les 4 cartes double face (noms abrégés). Après correction, les combos restent identiques.

Prix indicatif Scryfall : ~640 € (quelques prix EUR manquants).

## Plan de jeu
Rampe + trésors/nourriture → Korvold pioche à chaque sacrifice. Gagne par drain (Blood Artist, Zulaport, Bastion, Mayhem Devil) une fois une boucle en place, ou par dégâts de Korvold.

## Combos détectés (Commander Spellbook)

Aucun combo infini à 2 cartes rapide. Le seul « à 2 cartes » est cher (8 mana au total).

| Cartes | Prérequis | Résultat | Tag Spellbook |
|---|---|---|---|
| Chatterfang + Pitiless Plunderer | un autre Écureuil, {B} | trésors, écureuils, morts infinis ; −X/−X sur les créatures adverses | S |
| Gravecrawler + Phyrexian Altar | un autre Zombie (Carrion Feeder, Grave Titan, Nim Deathmantle) | morts et sacrifices infinis | E |
| Pitiless Plunderer + Ashnod's Altar + Reassembling Skeleton | — | mana incolore et morts infinis | E |
| Pitiless Plunderer + Phyrexian Altar + Reassembling Skeleton | — | morts infinis | E |
| Gravecrawler + Pitiless Plunderer + Ashnod's Altar | un autre Zombie | mana et morts infinis | E |
| Gravecrawler + Pitiless Plunderer + Viscera Seer / Carrion Feeder / Woe Strider | un autre Zombie | morts infinis (3 variantes) | E |
| Nim Deathmantle + Ashnod's Altar + Wurmcoil Engine | — | mana, jetons et morts infinis | E |
| Nim Deathmantle + Ashnod's Altar + Grave Titan | {2} | mana, jetons et morts infinis | E |
| Nim Deathmantle + Ashnod's Altar + Orcish Bowmasters | {2} | dégâts infinis | P |
| Nim Deathmantle + Ashnod's Altar + Woe Strider | {2} | morts infinies | E |
| Nim Deathmantle + Ashnod's Altar + Prosperous Innkeeper + Goldspan Dragon | {2} | morts infinies | E |

Avec Korvold en jeu, chaque boucle de sacrifice = pioche infinie (la pioche est obligatoire, mais la boucle est facultative : on s'arrête quand on veut).
Conditions de victoire : Blood Artist, Zulaport Cutthroat, Bastion of Remembrance, Mayhem Devil, Orcish Bowmasters (boucle Deathmantle), ou Chatterfang qui vide le board adverse.

**Variante plus sage (testée)** : si ta table refuse tout combo à 2 cartes, remplace Chatterfang, Squirrel General par **Mahadi, Emporium Master**. Vérifié : légal, identité OK, toujours 3 Game Changers ; Spellbook passe de « S » à **« P »** (bracket 3 standard), 12 combos restants, tous à 3 cartes ou plus.

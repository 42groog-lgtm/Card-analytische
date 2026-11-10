# Korvold, Fae-Cursed King — Jund Aristocrats (Bracket 3 haut / « 3++ »)

Liste importable : [`korvold-bracket3.txt`](korvold-bracket3.txt) (format Arena/MTGO, sections Commander/Deck).

## Vérifications (10 nov. 2026)

| Contrôle | Source | Résultat |
|---|---|---|
| 100 cartes, singleton (hors bases) | script | OK |
| Les 88 noms uniques existent | Scryfall `/cards/collection` | OK |
| Légales en Commander | Scryfall `legalities.commander` | OK, aucune bannie |
| Identité couleur ⊆ BRG | Scryfall `color_identity` | OK |
| Game Changers | Scryfall `is:gamechanger` (53 cartes) | **3/3** : Demonic Tutor, The One Ring, Orcish Bowmasters |
| Destruction massive de terrains / tours supplémentaires | Spellbook `estimate-bracket` | Aucune |
| Combos | Spellbook `find-my-combos` | 13 combos (voir plus bas) |
| Bracket estimé | Spellbook `estimate-bracket` | **S « Spicy »** = palier 3 dans leur code (le palier le plus haut avant « Ruthless » = 4) |

Prix indicatif Scryfall : ~640 € (quelques prix EUR manquants : Toxic Deluge, Beast Within, Talisman of Indulgence, terrains de base).

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

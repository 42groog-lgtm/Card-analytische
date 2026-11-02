# Mimir

Analyseur de decklist **Magic: The Gathering**, pensé pour le téléphone (PWA installable).

- **Import** : colle une decklist (Arena, MTGO, « 4 Lightning Bolt », sections Deck / Sideboard / Commander).
- **Légalité** : Standard, Pioneer, Modern, Legacy, Vintage, Commander (taille, copies, bannies/restreintes, identité couleur).
- **Analyse** : couleurs et symboles de mana, types de cartes, courbe de mana, terrains.
- **Catégories & tags** : tags libres ou catégories colorées par carte, groupement/filtre, multi-sélection.
- **Local** : tout est stocké dans le navigateur (IndexedDB), export/import JSON. Données cartes : [Scryfall](https://scryfall.com).

## Développement
```
npm install
npm run dev      # serveur local
npm test         # tests (logique pure)
npm run build    # build de production (dist/)
```

## Déploiement
Workflow GitHub Pages dans `.github/workflows/pages.yml` (déclenché sur `main`).
À activer une fois : Settings → Pages → Source : **GitHub Actions**.

export type Format = 'standard' | 'pioneer' | 'modern' | 'legacy' | 'vintage' | 'commander'
export const FORMATS: { id: Format; label: string }[] = [
  { id: 'standard', label: 'Standard' },
  { id: 'pioneer', label: 'Pioneer' },
  { id: 'modern', label: 'Modern' },
  { id: 'legacy', label: 'Legacy' },
  { id: 'vintage', label: 'Vintage' },
  { id: 'commander', label: 'Commander' },
]

export type Zone = 'main' | 'side' | 'commander'
export type Color = 'W' | 'U' | 'B' | 'R' | 'G'
export const COLORS: Color[] = ['W', 'U', 'B', 'R', 'G']

export type Legality = 'legal' | 'not_legal' | 'banned' | 'restricted'

/** Sous-ensemble utile d'une carte Scryfall. */
export interface Card {
  id: string
  name: string
  manaCost: string
  cmc: number
  typeLine: string
  oracleText: string
  colors: Color[]
  colorIdentity: Color[]
  legalities: Partial<Record<Format, Legality>>
  image?: string
}

export interface DeckEntry {
  qty: number
  name: string
  zone: Zone
}

export interface ResolvedEntry extends DeckEntry {
  card?: Card
}

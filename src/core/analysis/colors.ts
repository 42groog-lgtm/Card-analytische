import { COLORS, type Color, type ResolvedEntry } from '../types'

export interface ColorReport {
  /** Nombre de cartes (non-terrains) par couleur ; multicolore compté dans chaque couleur. */
  cards: Record<Color, number>
  colorless: number
  multicolor: number
  /** Symboles de mana dans les coûts (hybride compté pour chaque couleur). */
  pips: Record<Color, number>
  totalPips: number
  identity: Color[]
}

const zeroes = (): Record<Color, number> => ({ W: 0, U: 0, B: 0, R: 0, G: 0 })

export function analyzeColors(entries: ResolvedEntry[]): ColorReport {
  const cards = zeroes()
  const pips = zeroes()
  let colorless = 0
  let multicolor = 0
  const identity = new Set<Color>()

  for (const e of entries) {
    const c = e.card
    if (!c || e.zone === 'side') continue
    c.colorIdentity.forEach((x) => identity.add(x))
    if (/\bLand\b/.test(c.typeLine)) continue
    if (c.colors.length === 0) colorless += e.qty
    if (c.colors.length > 1) multicolor += e.qty
    c.colors.forEach((x) => (cards[x] += e.qty))
    for (const sym of c.manaCost.match(/\{[^}]+\}/g) ?? []) {
      for (const col of COLORS) if (sym.includes(col)) pips[col] += e.qty
    }
  }
  return {
    cards,
    colorless,
    multicolor,
    pips,
    totalPips: COLORS.reduce((n, c) => n + pips[c], 0),
    identity: COLORS.filter((c) => identity.has(c)),
  }
}

import type { Card, Format } from './types'

export interface FormatRules {
  minMain: number
  maxMain?: number
  maxSide: number
  maxCopies: number
  singleton: boolean
  commander: boolean
}

export const RULES: Record<Format, FormatRules> = {
  standard: { minMain: 60, maxSide: 15, maxCopies: 4, singleton: false, commander: false },
  pioneer: { minMain: 60, maxSide: 15, maxCopies: 4, singleton: false, commander: false },
  modern: { minMain: 60, maxSide: 15, maxCopies: 4, singleton: false, commander: false },
  legacy: { minMain: 60, maxSide: 15, maxCopies: 4, singleton: false, commander: false },
  vintage: { minMain: 60, maxSide: 15, maxCopies: 4, singleton: false, commander: false },
  commander: { minMain: 100, maxMain: 100, maxSide: 0, maxCopies: 1, singleton: true, commander: true },
}

export const isBasicLand = (c?: Card) => !!c && /\bBasic\b.*\bLand\b/.test(c.typeLine)

const NUMBER_WORDS: Record<string, number> = {
  two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
}

/** Nombre max de copies pour une carte (hors règle du format). `Infinity` = illimité. */
export function copyLimit(card: Card | undefined, rules: FormatRules, format: Format): number {
  if (isBasicLand(card)) return Infinity
  const text = card?.oracleText ?? ''
  if (/A deck can have any number of cards named/i.test(text)) return Infinity
  const up = text.match(/A deck can have up to (\w+) cards named/i)
  if (up && NUMBER_WORDS[up[1].toLowerCase()]) return NUMBER_WORDS[up[1].toLowerCase()]
  if (format === 'vintage' && card?.legalities.vintage === 'restricted') return 1
  return rules.maxCopies
}

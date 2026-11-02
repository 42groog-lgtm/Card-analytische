import { checkLegality } from './analysis/legality'
import { analyzeColors } from './analysis/colors'
import { analyzeTypes } from './analysis/types'
import { analyzeCurve } from './analysis/curve'
import type { Format, ResolvedEntry } from './types'

export function analyzeDeck(entries: ResolvedEntry[], format: Format) {
  return {
    legality: checkLegality(entries, format),
    colors: analyzeColors(entries),
    types: analyzeTypes(entries),
    curve: analyzeCurve(entries),
  }
}
export type DeckAnalysis = ReturnType<typeof analyzeDeck>

import { mainType } from './types'
import type { ResolvedEntry } from '../types'

export interface CurveReport {
  /** Index 0..7 ; la dernière case regroupe 7+. */
  buckets: number[]
  averageCmc: number
  nonLand: number
  lands: number
}

export function analyzeCurve(entries: ResolvedEntry[]): CurveReport {
  const buckets = new Array(8).fill(0) as number[]
  let total = 0
  let nonLand = 0
  let lands = 0
  for (const e of entries) {
    if (!e.card || e.zone === 'side') continue
    if (mainType(e.card.typeLine) === 'Land') { lands += e.qty; continue }
    buckets[Math.min(7, Math.floor(e.card.cmc))] += e.qty
    total += e.card.cmc * e.qty
    nonLand += e.qty
  }
  return { buckets, averageCmc: nonLand ? total / nonLand : 0, nonLand, lands }
}

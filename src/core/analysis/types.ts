import type { ResolvedEntry } from '../types'

export const TYPE_ORDER = [
  'Creature', 'Planeswalker', 'Battle', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land',
] as const
export type MainType = (typeof TYPE_ORDER)[number]

/** Type principal (priorité : Terrain > Créature > … comme sur la plupart des sites). */
export function mainType(typeLine: string): MainType | 'Other' {
  const front = typeLine.split('//')[0]
  if (/\bLand\b/.test(front)) return 'Land'
  for (const t of TYPE_ORDER) if (t !== 'Land' && new RegExp(`\\b${t}\\b`).test(front)) return t
  return 'Other'
}

export interface TypeReport {
  counts: Partial<Record<MainType | 'Other', number>>
  total: number
}

export function analyzeTypes(entries: ResolvedEntry[]): TypeReport {
  const counts: TypeReport['counts'] = {}
  let total = 0
  for (const e of entries) {
    if (!e.card || e.zone === 'side') continue
    const t = mainType(e.card.typeLine)
    counts[t] = (counts[t] ?? 0) + e.qty
    total += e.qty
  }
  return { counts, total }
}

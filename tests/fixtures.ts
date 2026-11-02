import type { Card, Color, Format, Legality } from '../src/core/types'

export function mk(p: Partial<Card> & { name: string }, legal: Legality = 'legal'): Card {
  const legalities: Card['legalities'] = {}
  for (const f of ['standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander'] as Format[]) legalities[f] = legal
  return {
    id: p.name, manaCost: '', cmc: 0, typeLine: 'Instant', oracleText: '',
    colors: [] as Color[], colorIdentity: [] as Color[], legalities, ...p,
  }
}

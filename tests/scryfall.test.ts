import { describe, expect, it, vi } from 'vitest'
import { attachCards, fetchCards, mapCard } from '../src/core/scryfall'

const raw = (name: string) => ({
  id: name, name, mana_cost: '{R}', cmc: 1, type_line: 'Instant', oracle_text: 'x', colors: ['R'], color_identity: ['R'],
  legalities: { modern: 'legal', commander: 'banned' }, image_uris: { normal: 'img' },
})

describe('scryfall', () => {
  it('mappe une carte, y compris double face', () => {
    expect(mapCard(raw('Bolt')).legalities.commander).toBe('banned')
    const dfc = mapCard({ id: '1', name: 'A // B', cmc: 2, type_line: 'Creature // Land', color_identity: [], legalities: {},
      card_faces: [{ mana_cost: '{1}{G}', colors: ['G'], image_uris: { normal: 'f' }, oracle_text: 'o' }, { mana_cost: '' }] })
    expect(dfc.manaCost).toBe('{1}{G}')
    expect(dfc.colors).toEqual(['G'])
    expect(dfc.image).toBe('f')
  })
  it('découpe par lots de 75 et retrouve par nom de face', async () => {
    const names = Array.from({ length: 80 }, (_, i) => `Card ${i}`)
    const f = vi.fn(async (_u: unknown, init: { body: string }) => {
      const ids = JSON.parse(init.body).identifiers as { name: string }[]
      return { ok: true, json: async () => ({ data: ids.map((i) => raw(i.name)) }) }
    })
    const map = await fetchCards(names, f as unknown as typeof fetch)
    expect(f).toHaveBeenCalledTimes(2)
    const r = attachCards([{ qty: 1, name: 'card 3', zone: 'main' }], map)
    expect(r[0].card?.name).toBe('Card 3')
  })
})

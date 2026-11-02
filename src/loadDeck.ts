import { attachCards, fetchCards } from './core/scryfall'
import type { Card, DeckEntry, ResolvedEntry } from './core/types'
import { db } from './db'

const frontName = (n: string) => n.split('//')[0].trim().toLowerCase()

/** Résout les cartes : cache IndexedDB d'abord, puis Scryfall pour les manquantes. */
export async function resolveEntries(entries: DeckEntry[]): Promise<ResolvedEntry[]> {
  const keys = entries.map((e) => frontName(e.name))
  const cached = await db.cards.bulkGet(keys)
  const map = new Map<string, Card>()
  const missing: string[] = []
  cached.forEach((c, i) => {
    if (c) map.set(keys[i], c.card)
    else missing.push(entries[i].name)
  })
  if (missing.length) {
    const fetched = await fetchCards(missing)
    const now = Date.now()
    const rows = new Map<string, { key: string; card: Card; at: number }>()
    for (const c of fetched.values()) rows.set(frontName(c.name), { key: frontName(c.name), card: c, at: now })
    await db.cards.bulkPut([...rows.values()])
    for (const [k, v] of fetched) map.set(k, v)
  }
  return attachCards(entries, map)
}

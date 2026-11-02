import type { Card, Color, DeckEntry, Format, ResolvedEntry } from './types'
import { FORMATS } from './types'

const API = 'https://api.scryfall.com'

/* eslint-disable @typescript-eslint/no-explicit-any */
export function mapCard(raw: any): Card {
  const faces: any[] = raw.card_faces ?? []
  const front = faces[0] ?? raw
  const legalities: Card['legalities'] = {}
  for (const f of FORMATS) legalities[f.id] = raw.legalities?.[f.id]
  return {
    id: raw.id,
    name: raw.name,
    manaCost: raw.mana_cost || faces.map((f) => f.mana_cost).filter(Boolean).join(' // ') || '',
    cmc: raw.cmc ?? 0,
    typeLine: raw.type_line ?? '',
    oracleText: raw.oracle_text ?? faces.map((f) => f.oracle_text).filter(Boolean).join('\n'),
    colors: (raw.colors ?? front.colors ?? []) as Color[],
    colorIdentity: (raw.color_identity ?? []) as Color[],
    legalities,
    image: raw.image_uris?.normal ?? front.image_uris?.normal,
  }
}

const key = (name: string) => name.toLowerCase()
const frontName = (name: string) => name.split('//')[0].trim().toLowerCase()

/** Résout des noms de cartes via /cards/collection (75 max/requête). */
export async function fetchCards(
  names: string[],
  fetchImpl: typeof fetch = fetch,
): Promise<Map<string, Card>> {
  const out = new Map<string, Card>()
  const unique = [...new Set(names)]
  for (let i = 0; i < unique.length; i += 75) {
    const chunk = unique.slice(i, i + 75)
    const res = await fetchImpl(`${API}/cards/collection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ identifiers: chunk.map((name) => ({ name })) }),
    })
    if (!res.ok) throw new Error(`Scryfall a répondu ${res.status}`)
    const json = await res.json()
    for (const raw of json.data ?? []) {
      const card = mapCard(raw)
      out.set(key(card.name), card)
      out.set(frontName(card.name), card)
    }
  }
  return out
}

export function attachCards(entries: DeckEntry[], cards: Map<string, Card>): ResolvedEntry[] {
  return entries.map((e) => ({
    ...e,
    card: cards.get(key(e.name)) ?? cards.get(frontName(e.name)),
  }))
}

export type { Format }

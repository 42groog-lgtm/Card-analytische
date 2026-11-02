import Dexie, { type EntityTable } from 'dexie'
import type { Card, DeckEntry, Format } from './core/types'
import type { CardTags, Category } from './core/tags'
import { DEFAULT_CATEGORIES } from './core/tags'

export interface StoredDeck {
  id?: number
  name: string
  format: Format
  entries: DeckEntry[]
  updatedAt: number
}
export interface CachedCard { key: string; card: Card; at: number }
export interface Meta { key: string; value: unknown }

export const db = new Dexie('mimir') as Dexie & {
  decks: EntityTable<StoredDeck, 'id'>
  cards: EntityTable<CachedCard, 'key'>
  meta: EntityTable<Meta, 'key'>
}
db.version(1).stores({ decks: '++id, name, updatedAt', cards: 'key', meta: 'key' })

export async function getMeta<T>(key: string, fallback: T): Promise<T> {
  const m = await db.meta.get(key)
  return (m?.value as T) ?? fallback
}
export const setMeta = (key: string, value: unknown) => db.meta.put({ key, value })

export const getTags = () => getMeta<CardTags>('tags', {})
export const getCategories = () => getMeta<Category[]>('categories', DEFAULT_CATEGORIES)

export async function exportAll() {
  return {
    version: 1,
    decks: await db.decks.toArray(),
    tags: await getTags(),
    categories: await getCategories(),
  }
}

export async function importAll(data: Awaited<ReturnType<typeof exportAll>>) {
  if (data?.version !== 1) throw new Error('Fichier non reconnu')
  await db.transaction('rw', db.decks, db.meta, async () => {
    for (const d of data.decks) await db.decks.put(d)
    await setMeta('tags', data.tags ?? {})
    await setMeta('categories', data.categories ?? DEFAULT_CATEGORIES)
  })
}

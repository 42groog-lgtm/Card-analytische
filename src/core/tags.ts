/** Tags/catégories : stockés par nom de carte (réutilisables d'un deck à l'autre). */
export interface Category {
  id: string
  name: string
  color: string
}

export const DEFAULT_CATEGORIES: Category[] = [
  { id: 'ramp', name: 'Ramp', color: '#34d399' },
  { id: 'draw', name: 'Pioche', color: '#60a5fa' },
  { id: 'removal', name: 'Removal', color: '#f87171' },
  { id: 'wincon', name: 'Win-con', color: '#fbbf24' },
  { id: 'protect', name: 'Protection', color: '#a78bfa' },
]

export type CardTags = Record<string, string[]>

export const normName = (n: string) => n.toLowerCase()

export function addTag(tags: CardTags, card: string, tag: string): CardTags {
  const k = normName(card)
  const t = tag.trim()
  if (!t) return tags
  const cur = tags[k] ?? []
  return cur.includes(t) ? tags : { ...tags, [k]: [...cur, t] }
}

export function removeTag(tags: CardTags, card: string, tag: string): CardTags {
  const k = normName(card)
  const cur = (tags[k] ?? []).filter((x) => x !== tag)
  const next = { ...tags }
  if (cur.length) next[k] = cur
  else delete next[k]
  return next
}

export function removeTagEverywhere(tags: CardTags, tag: string): CardTags {
  const next: CardTags = {}
  for (const [k, v] of Object.entries(tags)) {
    const f = v.filter((x) => x !== tag)
    if (f.length) next[k] = f
  }
  return next
}

/** Nombre de cartes (exemplaires) par tag pour une liste d'entrées. */
export function countByTag(entries: { name: string; qty: number; zone: string }[], tags: CardTags) {
  const out: Record<string, number> = {}
  for (const e of entries) {
    if (e.zone === 'side') continue
    for (const t of tags[normName(e.name)] ?? []) out[t] = (out[t] ?? 0) + e.qty
  }
  return out
}

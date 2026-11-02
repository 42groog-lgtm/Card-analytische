import type { DeckEntry, Zone } from './types'

const SECTION: Record<string, Zone> = {
  deck: 'main', main: 'main', maindeck: 'main', mainboard: 'main',
  sideboard: 'side', side: 'side',
  commander: 'commander', commandant: 'commander',
}

/**
 * Parse une decklist texte (Arena / MTGO / "4 Nom").
 * Accepte : sections "Deck/Sideboard/Commander", "SB: 2 Nom", ligne vide avant la réserve,
 * suffixes d'édition "(SET) 123", "4x Nom", commentaires "//" et "#".
 */
export function parseDecklist(text: string): DeckEntry[] {
  const entries: DeckEntry[] = []
  let zone: Zone = 'main'
  let blankSeen = false
  let hasExplicitSection = false

  for (const raw of text.split(/\r?\n/)) {
    let line = raw.trim()
    if (!line) { blankSeen = true; continue }
    if (line.startsWith('//') || line.startsWith('#')) continue

    const sec = SECTION[line.replace(/:$/, '').toLowerCase()]
    if (sec) { zone = sec; hasExplicitSection = true; blankSeen = false; continue }

    // Format MTGO : une ligne vide sépare main et réserve (si aucune section explicite)
    if (blankSeen && !hasExplicitSection && zone === 'main' && entries.length > 0) zone = 'side'
    blankSeen = false

    let lineZone = zone
    const sb = line.match(/^SB:\s*(.*)$/i)
    if (sb) { lineZone = 'side'; line = sb[1] }

    const m = line.match(/^(\d+)\s*x?\s+(.+)$/i)
    if (!m) continue
    const name = cleanName(m[2])
    if (name) entries.push({ qty: parseInt(m[1], 10), name, zone: lineZone })
  }
  return mergeEntries(entries)
}

function cleanName(s: string): string {
  return s
    .replace(/\s+\([A-Za-z0-9]{2,6}\)\s*\S*$/, '') // (SET) 123
    .replace(/\s+\*[A-Za-z]+\*$/, '') // *F*
    .replace(/\s*\/\/\s*/g, ' // ') // DFC
    .trim()
}

function mergeEntries(list: DeckEntry[]): DeckEntry[] {
  const map = new Map<string, DeckEntry>()
  for (const e of list) {
    const key = `${e.zone}|${e.name.toLowerCase()}`
    const prev = map.get(key)
    if (prev) prev.qty += e.qty
    else map.set(key, { ...e })
  }
  return [...map.values()]
}

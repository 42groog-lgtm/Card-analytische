import { RULES, copyLimit } from '../rules'
import type { Card, Format, ResolvedEntry } from '../types'

export interface Issue {
  level: 'error' | 'warning'
  message: string
  card?: string
}

export interface LegalityReport {
  legal: boolean
  issues: Issue[]
  mainCount: number
  sideCount: number
}

const sum = (l: ResolvedEntry[]) => l.reduce((n, e) => n + e.qty, 0)

export function checkLegality(entries: ResolvedEntry[], format: Format): LegalityReport {
  const rules = RULES[format]
  const issues: Issue[] = []
  const main = entries.filter((e) => e.zone === 'main')
  const side = entries.filter((e) => e.zone === 'side')
  const cmd = entries.filter((e) => e.zone === 'commander')
  const mainCount = sum(main) + (rules.commander ? sum(cmd) : 0)
  const sideCount = sum(side)

  // Cartes inconnues
  for (const e of entries) {
    if (!e.card) issues.push({ level: 'error', message: 'Carte introuvable', card: e.name })
  }

  // Légalité par format
  for (const e of entries) {
    const l = e.card?.legalities[format]
    if (!e.card || l === undefined) continue
    if (l === 'banned') issues.push({ level: 'error', message: `Bannie en ${format}`, card: e.card.name })
    else if (l === 'not_legal') issues.push({ level: 'error', message: `Non légale en ${format}`, card: e.card.name })
  }

  // Taille
  if (mainCount < rules.minMain)
    issues.push({ level: 'error', message: `Deck trop petit : ${mainCount}/${rules.minMain} cartes` })
  if (rules.maxMain && mainCount > rules.maxMain)
    issues.push({ level: 'error', message: `Deck trop grand : ${mainCount}/${rules.maxMain} cartes` })
  if (sideCount > rules.maxSide)
    issues.push({ level: 'error', message: `Réserve trop grande : ${sideCount}/${rules.maxSide} cartes` })

  // Copies (main + side cumulés, commandant inclus)
  const byName = new Map<string, { qty: number; card?: Card }>()
  for (const e of entries) {
    const key = (e.card?.name ?? e.name).toLowerCase()
    const prev = byName.get(key)
    if (prev) prev.qty += e.qty
    else byName.set(key, { qty: e.qty, card: e.card })
  }
  for (const { qty, card } of byName.values()) {
    const limit = copyLimit(card, rules, format)
    if (qty > limit)
      issues.push({ level: 'error', message: `${qty} exemplaires (maximum ${limit})`, card: card?.name })
  }

  // Commander : commandant + identité couleur
  if (rules.commander) {
    if (cmd.length === 0) {
      issues.push({ level: 'error', message: 'Aucun commandant défini (section « Commander »)' })
    } else {
      if (sum(cmd) > 2) issues.push({ level: 'error', message: 'Trop de commandants' })
      for (const c of cmd) {
        const t = c.card
        if (!t) continue
        const ok =
          (/\bLegendary\b/.test(t.typeLine) && /\bCreature\b/.test(t.typeLine)) ||
          /can be your commander/i.test(t.oracleText)
        if (!ok) issues.push({ level: 'error', message: 'Ne peut pas être commandant', card: t.name })
      }
      const allowed = new Set(cmd.flatMap((c) => c.card?.colorIdentity ?? []))
      for (const e of main) {
        const bad = e.card?.colorIdentity.filter((c) => !allowed.has(c))
        if (e.card && bad && bad.length)
          issues.push({ level: 'error', message: `Hors identité couleur (${bad.join('')})`, card: e.card.name })
      }
    }
  }

  if (!rules.commander && cmd.length)
    issues.push({ level: 'warning', message: 'Section « Commander » ignorée dans ce format' })

  return { legal: !issues.some((i) => i.level === 'error'), issues, mainCount, sideCount }
}

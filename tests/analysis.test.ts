import { describe, expect, it } from 'vitest'
import { mk } from './fixtures'
import { checkLegality } from '../src/core/analysis/legality'
import { analyzeColors } from '../src/core/analysis/colors'
import { analyzeTypes } from '../src/core/analysis/types'
import { analyzeCurve } from '../src/core/analysis/curve'
import type { ResolvedEntry } from '../src/core/types'

const mountain = mk({ name: 'Mountain', typeLine: 'Basic Land — Mountain', colorIdentity: ['R'] })
const bolt = mk({ name: 'Lightning Bolt', manaCost: '{R}', cmc: 1, colors: ['R'], colorIdentity: ['R'] })
const goyf = mk({ name: 'Tarmogoyf', manaCost: '{1}{G}', cmc: 2, colors: ['G'], colorIdentity: ['G'], typeLine: 'Creature — Lhurgoyf' })
const e = (qty: number, card: ResolvedEntry['card'], zone: ResolvedEntry['zone'] = 'main'): ResolvedEntry => ({ qty, name: card!.name, zone, card })

describe('légalité (constructed)', () => {
  it('deck de 60 cartes légal', () => {
    const r = checkLegality([e(56, mountain), e(4, bolt)], 'modern')
    expect(r.legal).toBe(true)
    expect(r.mainCount).toBe(60)
  })
  it('détecte 5 copies, deck trop petit et réserve trop grande', () => {
    const r = checkLegality([e(5, bolt), e(16, mountain, 'side')], 'modern')
    const msgs = r.issues.map((i) => i.message).join('|')
    expect(r.legal).toBe(false)
    expect(msgs).toMatch(/5 exemplaires/)
    expect(msgs).toMatch(/trop petit/)
    expect(msgs).toMatch(/Réserve trop grande/)
  })
  it('détecte carte bannie et non légale', () => {
    const banned = mk({ name: 'Ban' }, 'banned')
    const nl = mk({ name: 'NL' }, 'not_legal')
    const r = checkLegality([e(1, banned), e(1, nl)], 'modern')
    expect(r.issues.filter((i) => /Bannie|Non légale/.test(i.message))).toHaveLength(2)
  })
  it('vintage : restreinte = 1 exemplaire', () => {
    const power = mk({ name: 'Ancestral' }, 'restricted')
    const r = checkLegality([e(2, power)], 'vintage')
    expect(r.issues.some((i) => /maximum 1/.test(i.message))).toBe(true)
  })
  it('cumule main + réserve pour le nombre de copies', () => {
    const r = checkLegality([e(3, bolt), e(2, bolt, 'side')], 'modern')
    expect(r.issues.some((i) => /5 exemplaires/.test(i.message))).toBe(true)
  })
})

describe('légalité (commander)', () => {
  const cmd = mk({ name: 'Boss', typeLine: 'Legendary Creature — Elf', colorIdentity: ['G'] })
  it('exige un commandant', () => {
    expect(checkLegality([e(99, mountain)], 'commander').issues.some((i) => /Aucun commandant/.test(i.message))).toBe(true)
  })
  it('singleton hors terrains de base, et identité couleur', () => {
    const r = checkLegality([e(1, cmd, 'commander'), e(98, mountain), e(2, goyf), e(1, bolt)], 'commander')
    const msgs = r.issues.map((i) => i.message).join('|')
    expect(msgs).toMatch(/2 exemplaires/)
    expect(msgs).toMatch(/Hors identité couleur/)
  })
  it('deck de 100 valide', () => {
    const forest = mk({ name: 'Forest', typeLine: 'Basic Land — Forest', colorIdentity: ['G'] })
    const r = checkLegality([e(1, cmd, 'commander'), e(99, forest)], 'commander')
    expect(r.legal).toBe(true)
  })
})

describe('analyses', () => {
  const entries = [e(20, mountain), e(4, bolt), e(4, goyf), e(3, bolt, 'side')]
  it('couleurs', () => {
    const c = analyzeColors(entries)
    expect(c.cards.R).toBe(4)
    expect(c.pips.G).toBe(4)
    expect(c.totalPips).toBe(8)
    expect(c.identity).toEqual(['R', 'G'])
  })
  it('types', () => {
    const t = analyzeTypes(entries)
    expect(t.counts).toEqual({ Land: 20, Instant: 4, Creature: 4 })
    expect(t.total).toBe(28)
  })
  it('courbe', () => {
    const c = analyzeCurve(entries)
    expect(c.buckets[1]).toBe(4)
    expect(c.buckets[2]).toBe(4)
    expect(c.averageCmc).toBe(1.5)
    expect(c.lands).toBe(20)
  })
})

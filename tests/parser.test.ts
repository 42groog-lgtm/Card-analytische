import { describe, expect, it } from 'vitest'
import { parseDecklist } from '../src/core/parser'

describe('parseDecklist', () => {
  it('parse le format simple et les sections', () => {
    const r = parseDecklist('Deck\n4 Lightning Bolt\n20 Mountain\n\nSideboard\n2 Smash to Smithereens')
    expect(r).toEqual([
      { qty: 4, name: 'Lightning Bolt', zone: 'main' },
      { qty: 20, name: 'Mountain', zone: 'main' },
      { qty: 2, name: 'Smash to Smithereens', zone: 'side' },
    ])
  })
  it('gère le format Arena avec édition et numéro', () => {
    const r = parseDecklist('4 Lightning Bolt (M11) 149\n1x Island')
    expect(r.map((e) => e.name)).toEqual(['Lightning Bolt', 'Island'])
  })
  it('traite une ligne vide comme début de réserve (MTGO)', () => {
    const r = parseDecklist('4 Opt\n\n3 Negate')
    expect(r[1].zone).toBe('side')
  })
  it('gère SB: et la section Commander', () => {
    const r = parseDecklist('Commander\n1 Atraxa, Praetors\' Voice\nDeck\n1 Sol Ring\nSB: 1 Foo')
    expect(r.map((e) => e.zone)).toEqual(['commander', 'main', 'side'])
  })
  it('fusionne les doublons', () => {
    expect(parseDecklist('2 Opt\n2 Opt')).toEqual([{ qty: 4, name: 'Opt', zone: 'main' }])
  })
  it('ignore commentaires et lignes invalides', () => {
    expect(parseDecklist('// hello\nnope\n1 Opt')).toHaveLength(1)
  })
})

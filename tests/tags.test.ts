import { describe, expect, it } from 'vitest'
import { addTag, removeTag, removeTagEverywhere, countByTag } from '../src/core/tags'

describe('tags', () => {
  it('ajoute sans doublon, insensible à la casse du nom', () => {
    let t = addTag({}, 'Sol Ring', 'ramp')
    t = addTag(t, 'sol ring', 'ramp')
    expect(t).toEqual({ 'sol ring': ['ramp'] })
  })
  it('supprime et nettoie la clé vide', () => {
    expect(removeTag({ a: ['x'] }, 'a', 'x')).toEqual({})
  })
  it('supprime un tag partout', () => {
    expect(removeTagEverywhere({ a: ['x', 'y'], b: ['x'] }, 'x')).toEqual({ a: ['y'] })
  })
  it('compte par tag hors réserve', () => {
    const c = countByTag(
      [{ name: 'A', qty: 3, zone: 'main' }, { name: 'B', qty: 2, zone: 'side' }],
      { a: ['ramp'], b: ['ramp'] },
    )
    expect(c).toEqual({ ramp: 3 })
  })
})

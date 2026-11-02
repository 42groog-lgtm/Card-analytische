import { MANA_HEX } from '../colors'
import type { Color } from '../../core/types'

export function ManaCost({ cost }: { cost: string }) {
  const syms = cost.match(/\{[^}]+\}/g) ?? []
  return (
    <span className="inline-flex gap-0.5 align-middle">
      {syms.map((s, i) => {
        const t = s.slice(1, -1)
        const c = (['W', 'U', 'B', 'R', 'G'] as Color[]).find((x) => t.startsWith(x))
        return (
          <span
            key={i}
            className="inline-flex h-4 min-w-4 items-center justify-center rounded-full px-0.5 text-[10px] font-bold text-black"
            style={{ background: c ? MANA_HEX[c] : '#c9ccdf' }}
          >
            {t.replace('/', '')}
          </span>
        )
      })}
    </span>
  )
}

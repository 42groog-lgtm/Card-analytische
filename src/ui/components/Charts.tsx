import { COLORS, type Color } from '../../core/types'
import type { ColorReport } from '../../core/analysis/colors'
import type { CurveReport } from '../../core/analysis/curve'
import type { TypeReport } from '../../core/analysis/types'
import { TYPE_ORDER } from '../../core/analysis/types'
import { COLOR_NAME, MANA_HEX } from '../colors'

const TYPE_FR: Record<string, string> = {
  Creature: 'Créatures', Planeswalker: 'Planeswalkers', Battle: 'Batailles', Instant: 'Éphémères',
  Sorcery: 'Rituels', Artifact: 'Artefacts', Enchantment: 'Enchantements', Land: 'Terrains', Other: 'Autres',
}

export function ColorRing({ report }: { report: ColorReport }) {
  const R = 52, C = 2 * Math.PI * R
  const total = report.totalPips
  let off = 0
  return (
    <div className="flex items-center gap-4">
      <svg width="130" height="130" viewBox="0 0 130 130" className="shrink-0 -rotate-90">
        <circle cx="65" cy="65" r={R} fill="none" stroke="#222544" strokeWidth="18" />
        {total > 0 && COLORS.map((c) => {
          const len = (report.pips[c] / total) * C
          const el = (
            <circle key={c} cx="65" cy="65" r={R} fill="none" stroke={MANA_HEX[c]} strokeWidth="18"
              strokeDasharray={`${len} ${C - len}`} strokeDashoffset={-off} />
          )
          off += len
          return el
        })}
      </svg>
      <ul className="flex-1 space-y-1.5 text-sm">
        {COLORS.filter((c) => report.pips[c] > 0 || report.cards[c] > 0).map((c: Color) => (
          <li key={c} className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full" style={{ background: MANA_HEX[c] }} />
            <span className="flex-1">{COLOR_NAME[c]}</span>
            <span className="text-muted">{report.cards[c]} cartes · {report.pips[c]} symboles</span>
          </li>
        ))}
        {report.colorless > 0 && (
          <li className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-slate-400" />
            <span className="flex-1">Incolore</span><span className="text-muted">{report.colorless} cartes</span></li>
        )}
      </ul>
    </div>
  )
}

export function TypeBars({ report }: { report: TypeReport }) {
  const rows = [...TYPE_ORDER, 'Other' as const].filter((t) => report.counts[t])
  const max = Math.max(1, ...rows.map((t) => report.counts[t] ?? 0))
  return (
    <ul className="space-y-2">
      {rows.map((t) => {
        const n = report.counts[t] ?? 0
        return (
          <li key={t} className="text-sm">
            <div className="mb-1 flex justify-between"><span>{TYPE_FR[t]}</span>
              <span className="text-muted">{n} · {Math.round((n / report.total) * 100)}%</span></div>
            <div className="h-2 overflow-hidden rounded-full bg-surface2">
              <div className="h-full rounded-full bg-accent" style={{ width: `${(n / max) * 100}%` }} />
            </div>
          </li>
        )
      })}
    </ul>
  )
}

export function ManaCurve({ report }: { report: CurveReport }) {
  const max = Math.max(1, ...report.buckets)
  return (
    <div>
      <div className="flex h-32 items-end gap-1.5">
        {report.buckets.map((n, i) => (
          <div key={i} className="flex flex-1 flex-col items-center justify-end gap-1">
            <span className="text-xs text-muted">{n || ''}</span>
            <div className="w-full rounded-t-md bg-accent" style={{ height: `${(n / max) * 100}%`, minHeight: n ? 4 : 0 }} />
          </div>
        ))}
      </div>
      <div className="mt-1 flex gap-1.5 text-center text-xs text-muted">
        {report.buckets.map((_, i) => <span key={i} className="flex-1">{i === 7 ? '7+' : i}</span>)}
      </div>
    </div>
  )
}

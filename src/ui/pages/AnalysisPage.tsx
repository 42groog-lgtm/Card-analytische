import type { DeckAnalysis } from '../../core/analyze'
import { FORMATS, type Format, type ResolvedEntry } from '../../core/types'
import { countByTag, type CardTags, type Category } from '../../core/tags'
import { ColorRing, ManaCurve, TypeBars } from '../components/Charts'
import { TagChip } from '../components/TagChip'

const Card = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="rounded-2xl bg-surface p-4">
    <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted">{title}</h2>
    {children}
  </section>
)

export function AnalysisPage({ a, format, entries, tags, cats, name }: {
  a: DeckAnalysis | null; format: Format; entries: ResolvedEntry[]; tags: CardTags; cats: Category[]; name: string
}) {
  if (!a) return <p className="py-20 text-center text-muted">Importe une decklist pour voir l'analyse.</p>
  const { legality: l, colors, curve, types } = a
  const label = FORMATS.find((f) => f.id === format)?.label
  const byTag = Object.entries(countByTag(entries, tags)).sort((x, y) => y[1] - x[1])
  const errors = l.issues.filter((i) => i.level === 'error')
  return (
    <div className="space-y-4">
      <div className={`rounded-2xl border p-4 ${l.legal ? 'border-ok/50 bg-ok/10' : 'border-bad/50 bg-bad/10'}`}>
        <div className="text-xs text-muted">{name || 'Deck'} · {label}</div>
        <div className={`text-xl font-bold ${l.legal ? 'text-ok' : 'text-bad'}`}>
          {l.legal ? `Légal en ${label}` : `Illégal en ${label}`}
        </div>
        {!l.legal && <div className="text-sm text-muted">{errors.length} problème{errors.length > 1 ? 's' : ''}</div>}
        {!!l.issues.length && (
          <ul className="mt-3 space-y-1.5 text-sm">
            {l.issues.map((i, k) => (
              <li key={k} className="flex gap-2">
                <span className={i.level === 'error' ? 'text-bad' : 'text-warn'}>●</span>
                <span>{i.card && <b>{i.card} — </b>}{i.message}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          [l.mainCount, 'Cartes'],
          [curve.lands, 'Terrains'],
          [curve.averageCmc.toFixed(2), 'CMC moyen'],
        ].map(([v, t]) => (
          <div key={t} className="rounded-2xl bg-surface p-3">
            <div className="text-2xl font-bold">{v}</div><div className="text-xs text-muted">{t}</div>
          </div>
        ))}
      </div>
      {l.sideCount > 0 && <p className="text-center text-xs text-muted">Réserve : {l.sideCount} cartes</p>}

      <Card title="Couleurs"><ColorRing report={colors} /></Card>
      <Card title="Types de cartes"><TypeBars report={types} /></Card>
      <Card title="Courbe de mana"><ManaCurve report={curve} /></Card>
      {!!byTag.length && (
        <Card title="Catégories & tags">
          <div className="flex flex-wrap gap-2">
            {byTag.map(([t, n]) => <TagChip key={t} tag={t} cats={cats} count={n} />)}
          </div>
        </Card>
      )}
    </div>
  )
}

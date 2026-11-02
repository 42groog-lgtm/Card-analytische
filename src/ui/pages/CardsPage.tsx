import { useMemo, useState } from 'react'
import type { ResolvedEntry } from '../../core/types'
import { mainType, TYPE_ORDER } from '../../core/analysis/types'
import { addTag, normName, removeTag, type CardTags, type Category } from '../../core/tags'
import { ManaCost } from '../components/ManaCost'
import { TagChip } from '../components/TagChip'

type GroupBy = 'type' | 'tag'
const TYPE_FR: Record<string, string> = {
  Creature: 'Créatures', Planeswalker: 'Planeswalkers', Battle: 'Batailles', Instant: 'Éphémères', Sorcery: 'Rituels',
  Artifact: 'Artefacts', Enchantment: 'Enchantements', Land: 'Terrains', Other: 'Autres',
}
const ZONE_FR = { main: '', side: 'Réserve', commander: 'Commandant' }

export function CardsPage({ entries, tags, cats, setTags }: {
  entries: ResolvedEntry[]; tags: CardTags; cats: Category[]; setTags: (t: CardTags) => void
}) {
  const [q, setQ] = useState('')
  const [group, setGroup] = useState<GroupBy>('type')
  const [filter, setFilter] = useState<string[]>([])
  const [selecting, setSelecting] = useState(false)
  const [selected, setSelected] = useState<string[]>([])
  const [sheet, setSheet] = useState<string[] | null>(null) // noms de cartes édités

  const tagOf = (e: ResolvedEntry) => tags[normName(e.name)] ?? []
  const allTags = useMemo(() => {
    const s = new Set<string>(cats.map((c) => c.name))
    Object.values(tags).forEach((l) => l.forEach((t) => s.add(t)))
    return [...s]
  }, [cats, tags])

  const visible = entries.filter((e) =>
    e.name.toLowerCase().includes(q.toLowerCase()) &&
    (!filter.length || filter.every((t) => tagOf(e).includes(t))))

  const groups = useMemo(() => {
    const m = new Map<string, ResolvedEntry[]>()
    const push = (k: string, e: ResolvedEntry) => m.set(k, [...(m.get(k) ?? []), e])
    for (const e of visible) {
      if (group === 'type') {
        const t = e.zone === 'side' ? 'Réserve' : e.zone === 'commander' ? 'Commandant'
          : TYPE_FR[e.card ? mainType(e.card.typeLine) : 'Other']
        push(t, e)
      } else if (e.zone === 'side') push('Réserve', e)
      else if (!tagOf(e).length) push('Sans tag', e)
      else tagOf(e).forEach((t) => push(t, e))
    }
    const order = group === 'type'
      ? ['Commandant', ...TYPE_ORDER.map((t) => TYPE_FR[t]), 'Autres', 'Réserve']
      : [...allTags, 'Sans tag', 'Réserve']
    return [...m.entries()].sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]))
  }, [visible, group, allTags]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!entries.length) return <p className="py-20 text-center text-muted">Aucune carte. Importe une decklist.</p>

  const toggleSel = (n: string) => setSelected((s) => (s.includes(n) ? s.filter((x) => x !== n) : [...s, n]))
  const tap = (e: ResolvedEntry) => (selecting ? toggleSel(e.name) : setSheet([e.name]))

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Rechercher une carte"
          className="min-w-0 flex-1 rounded-xl border border-line bg-surface px-4 py-2.5 outline-none focus:border-accent" />
        <button onClick={() => { setSelecting(!selecting); setSelected([]) }}
          className={`rounded-xl border px-3 text-sm ${selecting ? 'border-accent text-accent' : 'border-line text-muted'}`}>
          {selecting ? 'Annuler' : 'Sélection'}
        </button>
      </div>
      <div className="flex gap-2 text-sm">
        {(['type', 'tag'] as const).map((g) => (
          <button key={g} onClick={() => setGroup(g)}
            className={`rounded-full px-3 py-1 ${group === g ? 'bg-accent text-black font-semibold' : 'bg-surface text-muted'}`}>
            {g === 'type' ? 'Par type' : 'Par tag'}
          </button>
        ))}
      </div>
      <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
        {allTags.map((t) => (
          <TagChip key={t} tag={t} cats={cats} active={filter.includes(t)}
            onClick={() => setFilter((f) => (f.includes(t) ? f.filter((x) => x !== t) : [...f, t]))} />
        ))}
      </div>

      {groups.map(([title, list]) => (
        <section key={title}>
          <h3 className="mb-1 mt-3 flex justify-between text-xs font-semibold uppercase tracking-wide text-muted">
            <span>{title}</span><span>{list.reduce((n, e) => n + e.qty, 0)}</span>
          </h3>
          <ul className="divide-y divide-line overflow-hidden rounded-xl bg-surface">
            {list.map((e) => (
              <li key={e.zone + e.name}>
                <button onClick={() => tap(e)} className="flex w-full items-center gap-3 px-3 py-3 text-left active:bg-surface2">
                  {selecting && (
                    <span className={`h-5 w-5 shrink-0 rounded-full border-2 ${selected.includes(e.name) ? 'border-accent bg-accent' : 'border-line'}`} />
                  )}
                  <span className="w-5 shrink-0 text-center text-sm text-muted">{e.qty}</span>
                  <span className="min-w-0 flex-1">
                    <span className={`block truncate ${e.card ? '' : 'text-bad'}`}>{e.name}</span>
                    {!!tagOf(e).length && (
                      <span className="mt-1 flex flex-wrap gap-1">
                        {tagOf(e).map((t) => <TagChip key={t} tag={t} cats={cats} />)}
                      </span>
                    )}
                  </span>
                  {e.card && <ManaCost cost={e.card.manaCost} />}
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}
      <div className="h-16" />

      {selecting && selected.length > 0 && (
        <button onClick={() => setSheet(selected)}
          className="fixed bottom-20 left-1/2 z-10 -translate-x-1/2 rounded-full bg-accent px-6 py-3 font-semibold text-black shadow-lg">
          Taguer {selected.length} carte{selected.length > 1 ? 's' : ''}
        </button>
      )}

      {sheet && (
        <TagSheet names={sheet} entries={entries} tags={tags} cats={cats} allTags={allTags}
          onChange={setTags} onClose={() => { setSheet(null); setSelecting(false); setSelected([]) }} />
      )}
    </div>
  )
}

function TagSheet({ names, entries, tags, cats, allTags, onChange, onClose }: {
  names: string[]; entries: ResolvedEntry[]; tags: CardTags; cats: Category[]; allTags: string[]
  onChange: (t: CardTags) => void; onClose: () => void
}) {
  const [draft, setDraft] = useState('')
  const single = names.length === 1 ? entries.find((e) => e.name === names[0]) : undefined
  const has = (t: string) => names.every((n) => (tags[normName(n)] ?? []).includes(t))
  const toggle = (t: string) =>
    onChange(names.reduce((acc, n) => (has(t) ? removeTag(acc, n, t) : addTag(acc, n, t)), tags))
  const add = () => {
    const t = draft.trim()
    if (!t) return
    onChange(names.reduce((acc, n) => addTag(acc, n, t), tags))
    setDraft('')
  }
  return (
    <div className="fixed inset-0 z-30 flex items-end bg-black/60" onClick={onClose}>
      <div className="safe-b mx-auto max-h-[85%] w-full max-w-xl overflow-y-auto rounded-t-3xl bg-surface p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-line" />
        <div className="flex gap-4">
          {single?.card?.image && <img src={single.card.image} alt={single.name} className="w-28 rounded-lg" />}
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-bold">{single ? single.name : `${names.length} cartes`}</h2>
            {single?.card && <p className="text-sm text-muted">{single.card.typeLine}</p>}
            {single && ZONE_FR[single.zone] && <p className="text-xs text-muted">{ZONE_FR[single.zone]}</p>}
          </div>
        </div>
        <h3 className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wide text-muted">Tags</h3>
        <div className="flex flex-wrap gap-2">
          {allTags.map((t) => <TagChip key={t} tag={t} cats={cats} active={has(t)} onClick={() => toggle(t)} />)}
        </div>
        <div className="mt-4 flex gap-2">
          <input value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()}
            placeholder="Nouveau tag" className="min-w-0 flex-1 rounded-xl border border-line bg-bg px-4 py-2.5 outline-none focus:border-accent" />
          <button onClick={add} className="rounded-xl bg-accent px-4 font-semibold text-black">Ajouter</button>
        </div>
        <button onClick={onClose} className="mt-4 w-full rounded-xl border border-line py-3 text-muted">Fermer</button>
      </div>
    </div>
  )
}

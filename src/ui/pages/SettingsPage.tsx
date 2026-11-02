import { useRef, useState } from 'react'
import { removeTagEverywhere, type CardTags, type Category } from '../../core/tags'
import { exportAll, importAll } from '../../db'

const PALETTE = ['#34d399', '#60a5fa', '#f87171', '#fbbf24', '#a78bfa', '#f472b6', '#fb923c', '#2dd4bf']

export function SettingsPage({ cats, setCats, tags, setTags, onImported }: {
  cats: Category[]; setCats: (c: Category[]) => void
  tags: CardTags; setTags: (t: CardTags) => void; onImported: () => void
}) {
  const [name, setName] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  const file = useRef<HTMLInputElement>(null)

  const add = () => {
    const n = name.trim()
    if (!n || cats.some((c) => c.name === n)) return
    setCats([...cats, { id: crypto.randomUUID(), name: n, color: PALETTE[cats.length % PALETTE.length] }])
    setName('')
  }
  const doExport = async () => {
    const blob = new Blob([JSON.stringify(await exportAll(), null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'mimir-sauvegarde.json'
    a.click()
    URL.revokeObjectURL(a.href)
  }
  const doImport = async (f?: File) => {
    if (!f) return
    try {
      await importAll(JSON.parse(await f.text()))
      onImported()
      setMsg('Sauvegarde importée.')
    } catch (e) {
      setMsg(`Import impossible : ${(e as Error).message}`)
    }
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">Catégories</h2>
        <ul className="space-y-2">
          {cats.map((c) => (
            <li key={c.id} className="flex items-center gap-3 rounded-xl bg-surface p-3">
              <input type="color" value={c.color} aria-label={`Couleur ${c.name}`}
                onChange={(e) => setCats(cats.map((x) => (x.id === c.id ? { ...x, color: e.target.value } : x)))}
                className="h-8 w-8 shrink-0 rounded-full border-0 bg-transparent p-0" />
              <span className="flex-1">{c.name}</span>
              <button className="px-2 text-muted" aria-label={`Supprimer ${c.name}`}
                onClick={() => { setCats(cats.filter((x) => x.id !== c.id)); setTags(removeTagEverywhere(tags, c.name)) }}>✕</button>
            </li>
          ))}
        </ul>
        <div className="mt-3 flex gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()}
            placeholder="Nouvelle catégorie" className="min-w-0 flex-1 rounded-xl border border-line bg-surface px-4 py-2.5 outline-none focus:border-accent" />
          <button onClick={add} className="rounded-xl bg-accent px-4 font-semibold text-black">Ajouter</button>
        </div>
        <p className="mt-2 text-xs text-muted">Supprimer une catégorie retire aussi ce tag de toutes les cartes.</p>
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">Sauvegarde</h2>
        <div className="flex gap-3">
          <button onClick={doExport} className="flex-1 rounded-xl border border-line bg-surface py-3">Exporter (JSON)</button>
          <button onClick={() => file.current?.click()} className="flex-1 rounded-xl border border-line bg-surface py-3">Importer</button>
          <input ref={file} type="file" accept="application/json" hidden onChange={(e) => doImport(e.target.files?.[0])} />
        </div>
        {msg && <p className="mt-2 text-sm text-muted">{msg}</p>}
        <p className="mt-2 text-xs text-muted">Les données sont stockées uniquement sur cet appareil. Exporte-les pour les transférer ou les sauvegarder.</p>
      </section>

      <p className="text-center text-xs text-muted">Mimir · données cartes © Scryfall</p>
    </div>
  )
}

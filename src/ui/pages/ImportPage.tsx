import { useLiveQuery } from 'dexie-react-hooks'
import { FORMATS, type Format } from '../../core/types'
import { db, type StoredDeck } from '../../db'

const EXAMPLE = `Deck
4 Lightning Bolt
4 Monastery Swiftspear
4 Goblin Guide
4 Eidolon of the Great Revel
4 Lightning Helix
4 Boros Charm
4 Skullcrack
4 Rift Bolt
4 Searing Blaze
4 Sacred Foundry
4 Inspiring Vantage
4 Arid Mesa
4 Wooded Foothills
4 Mountain

Sideboard
3 Smash to Smithereens
3 Path to Exile
3 Rest in Peace
3 Deflecting Palm
3 Roiling Vortex`

export function ImportPage(p: {
  name: string; setName: (s: string) => void
  format: Format; setFormat: (f: Format) => void
  text: string; setText: (s: string) => void
  loading: boolean; error: string | null
  onAnalyze: () => void
  onOpen: (d: StoredDeck) => void
}) {
  const decks = useLiveQuery(() => db.decks.orderBy('updatedAt').reverse().toArray(), [])
  return (
    <div className="space-y-4">
      <input
        value={p.name} onChange={(e) => p.setName(e.target.value)} placeholder="Nom du deck"
        className="w-full rounded-xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent"
      />
      <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
        {FORMATS.map((f) => (
          <button key={f.id} onClick={() => p.setFormat(f.id)}
            className={`shrink-0 rounded-full border px-4 py-2 text-sm ${p.format === f.id ? 'border-accent bg-accent text-black font-semibold' : 'border-line bg-surface text-muted'}`}>
            {f.label}
          </button>
        ))}
      </div>
      <textarea
        value={p.text} onChange={(e) => p.setText(e.target.value)} rows={12} spellCheck={false}
        placeholder={'Colle ta decklist ici\n4 Lightning Bolt\n20 Mountain\n\nSideboard\n2 Smash to Smithereens'}
        className="w-full resize-none rounded-xl border border-line bg-surface p-4 font-mono text-sm outline-none focus:border-accent"
      />
      {p.error && <p className="rounded-xl bg-bad/15 p-3 text-sm text-bad">{p.error}</p>}
      <div className="flex gap-3">
        <button onClick={() => { p.setText(EXAMPLE); p.setName('Boros Burn (exemple)'); p.setFormat('modern') }}
          className="rounded-xl border border-line px-4 py-3 text-sm text-muted">Exemple</button>
        <button onClick={p.onAnalyze} disabled={p.loading || !p.text.trim()}
          className="flex-1 rounded-xl bg-accent py-3 font-semibold text-black disabled:opacity-40">
          {p.loading ? 'Chargement des cartes…' : 'Analyser'}
        </button>
      </div>

      {!!decks?.length && (
        <section className="pt-2">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">Decks enregistrés</h2>
          <ul className="space-y-2">
            {decks.map((d) => (
              <li key={d.id} className="flex items-center gap-2 rounded-xl bg-surface p-3">
                <button className="flex-1 text-left" onClick={() => p.onOpen(d)}>
                  <div className="font-medium">{d.name}</div>
                  <div className="text-xs text-muted">{FORMATS.find((f) => f.id === d.format)?.label} · {d.entries.reduce((n, e) => n + e.qty, 0)} cartes</div>
                </button>
                <button aria-label="Supprimer" className="px-2 py-1 text-muted" onClick={() => db.decks.delete(d.id!)}>✕</button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { analyzeDeck } from './core/analyze'
import { parseDecklist } from './core/parser'
import { DEFAULT_CATEGORIES, type CardTags, type Category } from './core/tags'
import type { Format, ResolvedEntry } from './core/types'
import { db, getCategories, getTags, setMeta, type StoredDeck } from './db'
import { resolveEntries } from './loadDeck'
import { BottomNav, type Tab } from './ui/components/BottomNav'
import { AnalysisPage } from './ui/pages/AnalysisPage'
import { CardsPage } from './ui/pages/CardsPage'
import { ImportPage } from './ui/pages/ImportPage'
import { SettingsPage } from './ui/pages/SettingsPage'

const TITLES: Record<Tab, string> = { import: 'Mimir', analysis: 'Analyse', cards: 'Cartes', settings: 'Réglages' }

export default function App() {
  const [tab, setTab] = useState<Tab>('import')
  const [name, setName] = useState('')
  const [format, setFormat] = useState<Format>('modern')
  const [text, setText] = useState('')
  const [entries, setEntries] = useState<ResolvedEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tags, setTagsState] = useState<CardTags>({})
  const [cats, setCatsState] = useState<Category[]>(DEFAULT_CATEGORIES)

  const reload = () => { getTags().then(setTagsState); getCategories().then(setCatsState) }
  useEffect(reload, [])

  const setTags = (t: CardTags) => { setTagsState(t); setMeta('tags', t) }
  const setCats = (c: Category[]) => { setCatsState(c); setMeta('categories', c) }

  const analysis = useMemo(() => (entries.length ? analyzeDeck(entries, format) : null), [entries, format])

  const run = async (deckName: string, fmt: Format, raw: ReturnType<typeof parseDecklist>, persist: boolean) => {
    setLoading(true); setError(null)
    try {
      const resolved = await resolveEntries(raw)
      setEntries(resolved)
      if (persist) {
        const existing = await db.decks.where('name').equals(deckName).first()
        const row: StoredDeck = { id: existing?.id, name: deckName, format: fmt, entries: raw, updatedAt: Date.now() }
        await db.decks.put(row)
      }
      setTab('analysis')
    } catch (e) {
      setError(`Impossible de récupérer les cartes (${(e as Error).message}). Vérifie ta connexion.`)
    } finally { setLoading(false) }
  }

  const analyze = () => {
    const raw = parseDecklist(text)
    if (!raw.length) { setError('Aucune carte reconnue. Format attendu : « 4 Lightning Bolt ».'); return }
    run(name.trim() || 'Sans titre', format, raw, true)
  }

  const open = (d: StoredDeck) => {
    setName(d.name); setFormat(d.format)
    setText(d.entries.map((e) => `${e.zone === 'side' ? 'SB: ' : ''}${e.qty} ${e.name}`).join('\n'))
    run(d.name, d.format, d.entries, false)
  }

  return (
    <div className="mx-auto min-h-full max-w-xl pb-24">
      <header className="safe-t sticky top-0 z-10 bg-bg/90 px-4 pb-3 pt-4 backdrop-blur">
        <h1 className="text-2xl font-bold tracking-tight">{TITLES[tab]}</h1>
      </header>
      <main className="px-4">
        {tab === 'import' && (
          <ImportPage name={name} setName={setName} format={format} setFormat={setFormat} text={text} setText={setText}
            loading={loading} error={error} onAnalyze={analyze} onOpen={open} />
        )}
        {tab === 'analysis' && <AnalysisPage a={analysis} format={format} entries={entries} tags={tags} cats={cats} name={name} />}
        {tab === 'cards' && <CardsPage entries={entries} tags={tags} cats={cats} setTags={setTags} />}
        {tab === 'settings' && <SettingsPage cats={cats} setCats={setCats} tags={tags} setTags={setTags} onImported={reload} />}
      </main>
      <BottomNav tab={tab} onChange={setTab} />
    </div>
  )
}

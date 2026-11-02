export type Tab = 'import' | 'analysis' | 'cards' | 'settings'
const ITEMS: { id: Tab; label: string; icon: string }[] = [
  { id: 'import', label: 'Deck', icon: 'M4 5h16v3H4zM4 10.5h16v3H4zM4 16h10v3H4z' },
  { id: 'analysis', label: 'Analyse', icon: 'M5 20V10m7 10V4m7 16v-7' },
  { id: 'cards', label: 'Cartes', icon: 'M7 3h10a1 1 0 011 1v16a1 1 0 01-1 1H7a1 1 0 01-1-1V4a1 1 0 011-1z' },
  { id: 'settings', label: 'Réglages', icon: 'M12 8a4 4 0 100 8 4 4 0 000-8zM12 2v3m0 14v3M2 12h3m14 0h3' },
]

export function BottomNav({ tab, onChange }: { tab: Tab; onChange: (t: Tab) => void }) {
  return (
    <nav className="safe-b fixed inset-x-0 bottom-0 z-20 border-t border-line bg-surface/95 backdrop-blur">
      <div className="mx-auto flex max-w-xl">
        {ITEMS.map((it) => (
          <button
            key={it.id}
            onClick={() => onChange(it.id)}
            className={`flex flex-1 flex-col items-center gap-0.5 py-2.5 text-[11px] ${tab === it.id ? 'text-accent' : 'text-muted'}`}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d={it.icon} />
            </svg>
            {it.label}
          </button>
        ))}
      </div>
    </nav>
  )
}

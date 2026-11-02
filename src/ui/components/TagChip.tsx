import type { Category } from '../../core/tags'

export const tagColor = (tag: string, cats: Category[]) =>
  cats.find((c) => c.name === tag)?.color ?? '#94a3b8'

export function TagChip({
  tag, cats, active = true, onClick, count,
}: { tag: string; cats: Category[]; active?: boolean; onClick?: () => void; count?: number }) {
  const col = tagColor(tag, cats)
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-medium"
      style={{
        borderColor: col,
        background: active ? col + '33' : 'transparent',
        color: active ? '#fff' : col,
        opacity: active ? 1 : 0.7,
      }}
    >
      {tag}
      {count !== undefined && <span className="opacity-70">{count}</span>}
    </button>
  )
}

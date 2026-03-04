/**
 * QuickChips — Horizontal suggested reply chips.
 * @module components/discovery/QuickChips
 */

interface QuickChipsProps {
  chips: string[]
  onSelect: (chip: string) => void
  disabled?: boolean
}

export function QuickChips({ chips, onSelect, disabled }: QuickChipsProps) {
  if (!chips.length) return null

  return (
    <div className="flex flex-wrap gap-2 px-6 py-2">
      {chips.map((chip, i) => (
        <button
          key={i}
          onClick={() => onSelect(chip)}
          disabled={disabled}
          className="px-3 py-1.5 rounded-full text-xs font-medium bg-accent/10 text-accent border border-accent/20 hover:bg-accent/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {chip}
        </button>
      ))}
    </div>
  )
}

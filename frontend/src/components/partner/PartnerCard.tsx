/**
 * PartnerCard — A single partner option in the selector grid.
 * Shows icon, name, description, best-for examples, and trait tags.
 * @module components/partner/PartnerCard
 */
import type { PartnerStyleMeta } from '../../types/project'

interface Props {
  partner: PartnerStyleMeta
  selected: boolean
  onSelect: (id: string) => void
}

export function PartnerCard({ partner, selected, onSelect }: Props) {
  return (
    <button
      type="button"
      onClick={() => onSelect(partner.id)}
      className={`
        group relative w-full text-left rounded-xl p-3.5 transition-all duration-200
        border backdrop-blur-md
        ${selected
          ? 'border-accent bg-accent/10 shadow-[0_0_16px_rgba(0,229,255,0.12)]'
          : 'border-white/8 bg-surface/60 hover:border-white/15 hover:bg-white/5'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-2">
        <span className="text-xl leading-none">{partner.icon}</span>
        <span className="text-sm font-semibold text-text-primary">{partner.name}</span>
        {selected && (
          <span className="ml-auto text-[10px] font-medium uppercase tracking-wider text-accent">
            Active
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-xs text-text-muted leading-relaxed mb-2.5">
        {partner.description}
      </p>

      {/* Best for */}
      <p className="text-[10px] text-text-muted/70 mb-2">
        Best for: {partner.best_for.slice(0, 3).join(', ')}
      </p>

      {/* Traits */}
      <div className="flex flex-wrap gap-1">
        {partner.traits.map((trait) => (
          <span
            key={trait}
            className="px-1.5 py-0.5 rounded text-[10px] bg-white/5 text-text-muted"
          >
            {trait}
          </span>
        ))}
      </div>

      {/* Selection ring */}
      {selected && (
        <div
          className="absolute inset-0 rounded-xl ring-1 ring-accent/40 pointer-events-none"
          aria-hidden
        />
      )}
    </button>
  )
}

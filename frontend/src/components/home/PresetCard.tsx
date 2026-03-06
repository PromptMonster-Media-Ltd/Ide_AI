/**
 * PresetCard -- Glassmorphism card for design scheme presets on the Home page.
 * Displays an icon, name, and description with a selected/hover glow state.
 * @module components/home/PresetCard
 */

interface PresetCardProps {
  icon: string
  name: string
  description: string
  selected: boolean
  onClick: () => void
}

export function PresetCard({ icon, name, description, selected, onClick }: PresetCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        flex flex-col items-start text-left rounded-xl p-4 cursor-pointer
        transition-all duration-200 ease-out
        ${
          selected
            ? 'bg-accent/5 border border-accent shadow-[0_0_20px_rgba(0,229,255,0.1)]'
            : 'bg-white/5 border border-border hover:border-white/15 hover:scale-[1.02]'
        }
      `}
    >
      <span className="text-3xl md:text-4xl leading-none">{icon}</span>
      <span className="text-sm font-semibold text-white mt-2">{name}</span>
      <span className="text-xs text-text-muted mt-1 line-clamp-2">{description}</span>
    </button>
  )
}

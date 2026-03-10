/**
 * ActivePartnerBadge — Compact pill showing the current AI partner.
 * Clicking opens the partner selector for mid-session switching.
 * @module components/partner/ActivePartnerBadge
 */
import type { PartnerStyleMeta } from '../../types/project'

interface Props {
  partner: PartnerStyleMeta | null
  onClick?: () => void
}

export function ActivePartnerBadge({ partner, onClick }: Props) {
  if (!partner) return null

  return (
    <button
      type="button"
      onClick={onClick}
      title="Change AI Partner"
      className="
        inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
        bg-white/5 border border-white/8 text-xs text-text-muted
        hover:bg-white/10 hover:border-white/15 transition-all cursor-pointer
      "
    >
      <span className="text-sm leading-none">{partner.icon}</span>
      <span className="font-medium text-text-primary">{partner.name}</span>
      <svg
        width="10"
        height="10"
        viewBox="0 0 10 10"
        fill="none"
        className="opacity-40"
      >
        <path
          d="M2.5 4L5 6.5L7.5 4"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  )
}

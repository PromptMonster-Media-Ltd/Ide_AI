/**
 * Badge — Small label/tag for effort sizes and status indicators.
 * @module components/ui/Badge
 */

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'accent' | 'success' | 'warning'
  className?: string
}

const badgeVariants = {
  default: 'bg-white/10 text-text-muted',
  accent: 'bg-accent-dim text-accent',
  success: 'bg-emerald-500/15 text-emerald-400',
  warning: 'bg-amber-500/15 text-amber-400',
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${badgeVariants[variant]} ${className}`}>
      {children}
    </span>
  )
}

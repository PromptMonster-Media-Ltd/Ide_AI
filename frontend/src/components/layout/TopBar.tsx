/**
 * TopBar — Horizontal header with page title, optional controls,
 * and a mobile-only profile avatar badge (top-right).
 * @module components/layout/TopBar
 */
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

interface TopBarProps {
  title?: string
  subtitle?: string
  children?: React.ReactNode
}

export function TopBar({ title, subtitle, children }: TopBarProps) {
  const { user, initials } = useAuthStore()

  return (
    <header className="h-14 border-b border-border bg-surface/80 backdrop-blur-sm flex items-center justify-between px-3 md:px-6 gap-3 shrink-0">
      <div className="min-w-0 flex-1">
        {title && <h1 className="text-sm font-semibold text-white truncate">{title}</h1>}
        {subtitle && <p className="text-xs text-text-muted truncate">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        {children}
        {/* Mobile-only profile badge */}
        {user && (
          <Link
            to="/profile"
            className="md:hidden w-8 h-8 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center text-xs text-accent font-bold shrink-0 overflow-hidden"
            aria-label="Profile"
          >
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="" className="w-full h-full object-cover" />
            ) : (
              initials()
            )}
          </Link>
        )}
      </div>
    </header>
  )
}

/**
 * TopBar — Horizontal header with project name and controls.
 * @module components/layout/TopBar
 */

interface TopBarProps {
  title?: string
  subtitle?: string
  children?: React.ReactNode
}

export function TopBar({ title, subtitle, children }: TopBarProps) {
  return (
    <header className="h-14 border-b border-border bg-surface/80 backdrop-blur-sm flex items-center justify-between px-3 md:px-6 gap-3 shrink-0">
      <div className="min-w-0 flex-1">
        {title && <h1 className="text-sm font-semibold text-white truncate">{title}</h1>}
        {subtitle && <p className="text-xs text-text-muted truncate">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        {children}
      </div>
    </header>
  )
}

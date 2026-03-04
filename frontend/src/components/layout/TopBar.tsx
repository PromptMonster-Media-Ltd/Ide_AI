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
    <header className="h-14 border-b border-border bg-surface/80 backdrop-blur-sm flex items-center justify-between px-6">
      <div>
        {title && <h1 className="text-sm font-semibold text-white">{title}</h1>}
        {subtitle && <p className="text-xs text-text-muted">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {children}
      </div>
    </header>
  )
}

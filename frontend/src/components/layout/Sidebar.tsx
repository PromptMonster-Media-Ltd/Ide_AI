/**
 * Sidebar — Vertical nav with icon+label items and project switcher.
 * @module components/layout/Sidebar
 */
import { Link, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: 'Home', icon: '✦' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
]

const PROJECT_ITEMS = [
  { path: '/discovery', label: 'Discovery', icon: '🔍' },
  { path: '/blocks', label: 'Blocks', icon: '◫' },
  { path: '/pipeline', label: 'Pipeline', icon: '⟡' },
  { path: '/exports', label: 'Exports', icon: '↗' },
  { path: '/pitch', label: 'Pitch', icon: '📄' },
]

export function Sidebar({ projectId }: { projectId?: string }) {
  const location = useLocation()

  return (
    <aside className="fixed left-0 top-0 h-screen w-[232px] transition-all duration-300 bg-surface border-r border-border z-50 flex flex-col overflow-hidden group">
      <div className="px-4 py-3 flex items-center border-b border-border">
        <img src="/logo.png" alt="Ide/AI" className="w-[200px] object-contain" />
      </div>

      <nav className="flex-1 py-4 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
              location.pathname === item.path
                ? 'text-accent bg-accent-dim'
                : 'text-text-muted hover:text-white hover:bg-white/5'
            }`}
          >
            <span className="shrink-0 text-base">{item.icon}</span>
            <span className="whitespace-nowrap">{item.label}</span>
          </Link>
        ))}

        {projectId && (
          <>
            <div className="mx-4 my-2 border-t border-border" />
            {PROJECT_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={`${item.path}/${projectId}`}
                className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  location.pathname.startsWith(`${item.path}/`)
                    ? 'text-accent bg-accent-dim'
                    : 'text-text-muted hover:text-white hover:bg-white/5'
                }`}
              >
                <span className="shrink-0 text-base">{item.icon}</span>
                <span className="whitespace-nowrap">{item.label}</span>
              </Link>
            ))}
          </>
        )}
      </nav>
    </aside>
  )
}

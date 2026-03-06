/**
 * Sidebar — Responsive navigation.
 * Desktop: Fixed left sidebar (232px) with logo + labels.
 * Mobile: Fixed bottom nav bar with icons only + hamburger for overflow.
 * @module components/layout/Sidebar
 */
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: 'Home', icon: '✦' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
]

const PROJECT_ITEMS = [
  { path: '/discovery', label: 'Discovery', icon: '🔍' },
  { path: '/blocks', label: 'Blocks', icon: '◫' },
  { path: '/pipeline', label: 'Pipeline', icon: '⟡' },
  { path: '/market', label: 'Market', icon: '📊' },
  { path: '/exports', label: 'Exports', icon: '↗' },
  { path: '/pitch', label: 'Pitch', icon: '📄' },
]

export function Sidebar({ projectId }: { projectId?: string }) {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const allItems = projectId
    ? [...NAV_ITEMS, ...PROJECT_ITEMS]
    : NAV_ITEMS

  // On mobile bottom bar, show first 4 items + "more" button
  const mobileBarItems = allItems.slice(0, 4)
  const mobileOverflowItems = allItems.slice(4)

  const isActive = (item: { path: string }) =>
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(`${item.path}/`) || location.pathname === item.path

  const buildTo = (item: { path: string }) =>
    projectId && PROJECT_ITEMS.some((p) => p.path === item.path)
      ? `${item.path}/${projectId}`
      : item.path

  return (
    <>
      {/* ── Desktop sidebar ── */}
      <aside className="hidden md:flex fixed left-0 top-0 h-screen w-[232px] bg-surface border-r border-border z-50 flex-col overflow-hidden">
        <Link to="/" className="px-4 py-3 flex items-center border-b border-border">
          <img src="/logo.png" alt="Ide/AI — Home" className="w-[200px] object-contain" />
        </Link>

        <nav className="flex-1 py-4 flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive(item)
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
                    isActive(item)
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

      {/* ── Mobile bottom nav ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-14 bg-surface border-t border-border z-50 flex items-center justify-around px-2">
        {mobileBarItems.map((item) => (
          <Link
            key={item.path}
            to={buildTo(item)}
            className={`flex flex-col items-center justify-center gap-0.5 py-1 px-2 rounded-lg text-xs transition-colors ${
              isActive(item)
                ? 'text-accent'
                : 'text-text-muted'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-[10px] leading-tight">{item.label}</span>
          </Link>
        ))}

        {mobileOverflowItems.length > 0 && (
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className={`flex flex-col items-center justify-center gap-0.5 py-1 px-2 rounded-lg text-xs transition-colors ${
              mobileMenuOpen ? 'text-accent' : 'text-text-muted'
            }`}
          >
            <span className="text-lg">•••</span>
            <span className="text-[10px] leading-tight">More</span>
          </button>
        )}
      </nav>

      {/* ── Mobile overflow menu ── */}
      {mobileMenuOpen && mobileOverflowItems.length > 0 && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="md:hidden fixed bottom-14 left-0 right-0 bg-surface border-t border-border z-50 py-2">
            <div className="px-4 py-2 flex items-center border-b border-border mb-2">
              <img src="/logo.png" alt="Ide/AI" className="w-[120px] object-contain" />
            </div>
            {mobileOverflowItems.map((item) => (
              <Link
                key={item.path}
                to={buildTo(item)}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 text-sm transition-colors ${
                  isActive(item)
                    ? 'text-accent bg-accent-dim'
                    : 'text-text-muted hover:text-white hover:bg-white/5'
                }`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
        </>
      )}
    </>
  )
}

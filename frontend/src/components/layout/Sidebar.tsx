/**
 * Sidebar — Responsive navigation.
 * Desktop: Fixed left sidebar (232px) with logo + labels.
 * Mobile: Fixed bottom nav bar with icons only + hamburger for overflow.
 * Shows "Back to Project" when user navigates to Home with an active project.
 * Project module items are driven by the active pathway from pathwayStore.
 * @module components/layout/Sidebar
 */
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { usePathwayStore } from '../../stores/pathwayStore'

const NAV_ITEMS = [
  { path: '/', label: 'Home', icon: '\u2726' },
  { path: '/library', label: 'Library', icon: '\u{1F4DA}' },
  { path: '/settings', label: 'Settings', icon: '\u2699' },
]

/** Hardcoded fallback project items — used when pathway hasn't loaded yet. */
const FALLBACK_PROJECT_ITEMS = [
  { path: '/discovery', label: 'Discovery', icon: '\u{1F50D}' },
  { path: '/blocks', label: 'Blocks', icon: '\u25EB' },
  { path: '/pipeline', label: 'Pipeline', icon: '\u27E1' },
  { path: '/market', label: 'Market', icon: '\u{1F4CA}' },
  { path: '/sprints', label: 'Sprints', icon: '\u{1F3C3}' },
  { path: '/exports', label: 'Exports', icon: '\u2197' },
  { path: '/pitch', label: 'Pitch', icon: '\u{1F4C4}' },
]

const ACTIVE_PROJECT_KEY = 'ideai_active_project'
const ACTIVE_PROJECT_PATH_KEY = 'ideai_active_path'

export function Sidebar({ projectId }: { projectId?: string }) {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [savedProjectId, setSavedProjectId] = useState<string | null>(null)
  const [savedPath, setSavedPath] = useState<string | null>(null)

  const { active: activePathway, fetchPathways } = usePathwayStore()

  // Fetch pathways on mount (deduped inside the store)
  useEffect(() => { fetchPathways() }, [fetchPathways])

  // Build project items from active pathway's modules (or fallback)
  const projectItems = activePathway?.modules
    ? [...activePathway.modules]
        .sort((a, b) => a.order - b.order)
        .map(m => ({ path: `/${m.route_suffix}`, label: m.label, icon: m.icon }))
    : FALLBACK_PROJECT_ITEMS

  // Persist active project when user is inside a project
  useEffect(() => {
    if (projectId) {
      localStorage.setItem(ACTIVE_PROJECT_KEY, projectId)
      localStorage.setItem(ACTIVE_PROJECT_PATH_KEY, location.pathname)
      setSavedProjectId(projectId)
      setSavedPath(location.pathname)
    }
  }, [projectId, location.pathname])

  // Load saved project on mount
  useEffect(() => {
    setSavedProjectId(localStorage.getItem(ACTIVE_PROJECT_KEY))
    setSavedPath(localStorage.getItem(ACTIVE_PROJECT_PATH_KEY))
  }, [])

  // Show "Back to Project" when on Home/Settings but there's a saved project
  const isOnHomePage = location.pathname === '/' || location.pathname === '/settings'
  const showBackToProject = isOnHomePage && savedProjectId && !projectId

  const allItems = projectId
    ? [...NAV_ITEMS, ...projectItems]
    : NAV_ITEMS

  const mobileBarItems = allItems.slice(0, 4)
  const mobileOverflowItems = allItems.slice(4)

  const isActive = (item: { path: string }) =>
    item.path === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(`${item.path}/`) || location.pathname === item.path

  const buildTo = (item: { path: string }) =>
    projectId && projectItems.some((p) => p.path === item.path)
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

          {/* Back to Project button — shown when user leaves a project */}
          {showBackToProject && (
            <>
              <div className="mx-4 my-2 border-t border-border" />
              <Link
                to={savedPath || `/discovery/${savedProjectId}`}
                className="flex items-center gap-3 px-4 py-2.5 text-sm text-accent bg-accent/5 border border-accent/20 mx-2 rounded-lg hover:bg-accent/10 transition-colors"
              >
                <span className="shrink-0 text-base">\u21A9</span>
                <span className="whitespace-nowrap">Back to Project</span>
              </Link>
            </>
          )}

          {projectId && (
            <>
              <div className="mx-4 my-2 border-t border-border" />
              {projectItems.map((item) => (
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
        {showBackToProject && (
          <Link
            to={savedPath || `/discovery/${savedProjectId}`}
            className="flex flex-col items-center justify-center gap-0.5 py-1 px-2 rounded-lg text-xs text-accent"
          >
            <span className="text-lg">\u21A9</span>
            <span className="text-[10px] leading-tight">Project</span>
          </Link>
        )}

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
            <span className="text-lg">\u2022\u2022\u2022</span>
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

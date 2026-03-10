/**
 * App.tsx — Root router. Public auth routes + protected application routes.
 * Uses a dynamic ModuleRouter for project-scoped pages resolved from the
 * concept pathway's module registry.
 */
import { lazy, Suspense } from 'react'
import { Routes, Route, useParams } from 'react-router-dom'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { OAuthCallback } from './pages/OAuthCallback'
import { Home } from './pages/Home'
import { Settings } from './pages/Settings'
import { Library } from './pages/Library'
import { SharedProject } from './pages/SharedProject'

/* ── Lazy-loaded module components ─────────────────────────────── */
const Discovery = lazy(() => import('./pages/Discovery').then(m => ({ default: m.Discovery })))
const Blocks = lazy(() => import('./pages/Blocks').then(m => ({ default: m.Blocks })))
const Pipeline = lazy(() => import('./pages/Pipeline').then(m => ({ default: m.Pipeline })))
const Exports = lazy(() => import('./pages/Exports').then(m => ({ default: m.Exports })))
const MarketAnalysis = lazy(() => import('./pages/MarketAnalysis').then(m => ({ default: m.MarketAnalysis })))
const PitchMode = lazy(() => import('./pages/PitchMode').then(m => ({ default: m.PitchMode })))
const SprintPlanner = lazy(() => import('./pages/SprintPlanner').then(m => ({ default: m.SprintPlanner })))

/**
 * Component registry — maps component_key (from pathway modules) to lazy components.
 * New pathways register their module components here.
 */
const MODULE_COMPONENTS: Record<string, React.LazyExoticComponent<React.ComponentType>> = {
  Discovery,
  Blocks,
  Pipeline,
  Exports,
  MarketAnalysis,
  PitchMode,
  SprintPlanner,
  // Phase 6 will add: MoodBoard, ChannelMix, WorldBuilder, etc.
}

/** Loading fallback for lazy-loaded modules. */
function ModuleLoading() {
  return (
    <div className="h-screen bg-background flex items-center justify-center">
      <div className="text-text-muted text-sm animate-pulse">Loading module...</div>
    </div>
  )
}

/**
 * ModuleRouter — Resolves the current route's moduleSlug to a component
 * from the MODULE_COMPONENTS registry via the pathway's route_suffix → component_key mapping.
 *
 * Route pattern: /:moduleSlug/:projectId
 *
 * Resolution order:
 * 1. Look up moduleSlug directly as a component_key (covers most cases)
 * 2. Check the ROUTE_SUFFIX_MAP for known suffix → component_key mappings
 * 3. Fallback to Discovery for unknown modules
 */
const ROUTE_SUFFIX_MAP: Record<string, string> = {
  discovery: 'Discovery',
  blocks: 'Blocks',
  pipeline: 'Pipeline',
  exports: 'Exports',
  market: 'MarketAnalysis',
  pitch: 'PitchMode',
  sprints: 'SprintPlanner',
}

function ModuleRouter() {
  const { moduleSlug } = useParams<{ moduleSlug: string; projectId: string }>()

  const componentKey = ROUTE_SUFFIX_MAP[moduleSlug ?? ''] ?? moduleSlug ?? ''
  const Component = MODULE_COMPONENTS[componentKey]

  if (!Component) {
    return (
      <div className="h-screen bg-background flex items-center justify-center">
        <div className="text-text-muted text-sm">Module not found: {moduleSlug}</div>
      </div>
    )
  }

  return (
    <Suspense fallback={<ModuleLoading />}>
      <Component />
    </Suspense>
  )
}

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/auth/callback/:provider" element={<OAuthCallback />} />

      {/* Public shared project view (no auth required) */}
      <Route path="/shared/:token" element={<SharedProject />} />

      {/* Protected non-project routes */}
      <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

      {/* Dynamic project-scoped module route */}
      <Route
        path="/:moduleSlug/:projectId"
        element={<ProtectedRoute><ModuleRouter /></ProtectedRoute>}
      />
    </Routes>
  )
}

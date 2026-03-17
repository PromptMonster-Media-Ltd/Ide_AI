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
import { ForgotPassword } from './pages/ForgotPassword'
import { ResetPassword } from './pages/ResetPassword'
import { VerifyEmail } from './pages/VerifyEmail'
import { OAuthCallback } from './pages/OAuthCallback'
import { Home } from './pages/Home'
import { Landing } from './pages/Landing'
import { Settings } from './pages/Settings'
import { Profile } from './pages/Profile'
import { Library } from './pages/Library'
import { Inbox } from './pages/Inbox'
import { SharedProject } from './pages/SharedProject'

/* ── Lazy-loaded module components ─────────────────────────────── */
const Discovery = lazy(() => import('./pages/Discovery').then(m => ({ default: m.Discovery })))
const Blocks = lazy(() => import('./pages/Blocks').then(m => ({ default: m.Blocks })))
const Pipeline = lazy(() => import('./pages/Pipeline').then(m => ({ default: m.Pipeline })))
const Exports = lazy(() => import('./pages/Exports').then(m => ({ default: m.Exports })))
const MarketAnalysis = lazy(() => import('./pages/MarketAnalysis').then(m => ({ default: m.MarketAnalysis })))
const PitchMode = lazy(() => import('./pages/PitchMode').then(m => ({ default: m.PitchMode })))
const SprintPlanner = lazy(() => import('./pages/SprintPlanner').then(m => ({ default: m.SprintPlanner })))
const ChannelMix = lazy(() => import('./pages/modules/ChannelMix').then(m => ({ default: m.ChannelMix })))
const MoodBoard = lazy(() => import('./pages/modules/MoodBoard').then(m => ({ default: m.MoodBoard })))
const WorldBuilder = lazy(() => import('./pages/modules/WorldBuilder').then(m => ({ default: m.WorldBuilder })))
const PathwayReview = lazy(() => import('./pages/PathwayReview').then(m => ({ default: m.PathwayReview })))
const PathwayExecute = lazy(() => import('./pages/PathwayExecute').then(m => ({ default: m.PathwayExecute })))
const ModuleSessionPage = lazy(() => import('./pages/ModuleSession').then(m => ({ default: m.ModuleSession })))

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
  ChannelMix,
  MoodBoard,
  WorldBuilder,
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
  'channel-mix': 'ChannelMix',
  'mood-board': 'MoodBoard',
  'world-builder': 'WorldBuilder',
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

/**
 * RootRoute — Shows Landing for visitors, redirects authenticated users to /home.
 */
function RootRoute() {
  const token = localStorage.getItem('token')
  if (token) {
    return <ProtectedRoute><Home /></ProtectedRoute>
  }
  return <Landing />
}

export default function App() {
  return (
    <Routes>
      {/* Public landing page (visitors) / protected Home (authenticated) */}
      <Route path="/" element={<RootRoute />} />

      {/* Public auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/auth/callback/:provider" element={<OAuthCallback />} />

      {/* Email verification (protected but exempt from verification check) */}
      <Route path="/verify-email" element={<ProtectedRoute><VerifyEmail /></ProtectedRoute>} />

      {/* Public shared project view (no auth required) */}
      <Route path="/shared/:token" element={<SharedProject />} />

      {/* Protected non-project routes */}
      <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/inbox" element={<ProtectedRoute><Inbox /></ProtectedRoute>} />

      {/* Modular pathway routes */}
      <Route
        path="/pathway-review/:projectId"
        element={<ProtectedRoute><Suspense fallback={<ModuleLoading />}><PathwayReview /></Suspense></ProtectedRoute>}
      />
      <Route
        path="/pathway-execute/:projectId"
        element={<ProtectedRoute><Suspense fallback={<ModuleLoading />}><PathwayExecute /></Suspense></ProtectedRoute>}
      />
      <Route
        path="/module-session/:projectId/:moduleId"
        element={<ProtectedRoute><Suspense fallback={<ModuleLoading />}><ModuleSessionPage /></Suspense></ProtectedRoute>}
      />

      {/* Dynamic project-scoped module route */}
      <Route
        path="/:moduleSlug/:projectId"
        element={<ProtectedRoute><ModuleRouter /></ProtectedRoute>}
      />
    </Routes>
  )
}

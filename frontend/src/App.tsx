/**
 * App.tsx — Root router. Public auth routes + protected application routes.
 */
import { Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { OAuthCallback } from './pages/OAuthCallback'
import { Home } from './pages/Home'
import { Discovery } from './pages/Discovery'
import { Blocks } from './pages/Blocks'
import { Pipeline } from './pages/Pipeline'
import { Exports } from './pages/Exports'
import { Settings } from './pages/Settings'
import { PitchMode } from './pages/PitchMode'
import { MarketAnalysis } from './pages/MarketAnalysis'
import { Library } from './pages/Library'
import { SharedProject } from './pages/SharedProject'
import { SprintPlanner } from './pages/SprintPlanner'

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/auth/callback/:provider" element={<OAuthCallback />} />

      {/* Public shared project view (no auth required) */}
      <Route path="/shared/:token" element={<SharedProject />} />

      {/* Protected application routes */}
      <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/discovery/:projectId" element={<ProtectedRoute><Discovery /></ProtectedRoute>} />
      <Route path="/blocks/:projectId" element={<ProtectedRoute><Blocks /></ProtectedRoute>} />
      <Route path="/pipeline/:projectId" element={<ProtectedRoute><Pipeline /></ProtectedRoute>} />
      <Route path="/exports/:projectId" element={<ProtectedRoute><Exports /></ProtectedRoute>} />
      <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/market/:projectId" element={<ProtectedRoute><MarketAnalysis /></ProtectedRoute>} />
      <Route path="/pitch/:projectId" element={<ProtectedRoute><PitchMode /></ProtectedRoute>} />
      <Route path="/sprints/:projectId" element={<ProtectedRoute><SprintPlanner /></ProtectedRoute>} />
    </Routes>
  )
}

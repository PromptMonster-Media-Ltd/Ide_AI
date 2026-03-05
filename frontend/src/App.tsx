/**
 * App.tsx — Root router. Public auth routes + protected application routes.
 */
import { Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Home } from './pages/Home'
import { Discovery } from './pages/Discovery'
import { Blocks } from './pages/Blocks'
import { Pipeline } from './pages/Pipeline'
import { Exports } from './pages/Exports'
import { Settings } from './pages/Settings'
import { PitchMode } from './pages/PitchMode'

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected application routes */}
      <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/discovery/:projectId" element={<ProtectedRoute><Discovery /></ProtectedRoute>} />
      <Route path="/blocks/:projectId" element={<ProtectedRoute><Blocks /></ProtectedRoute>} />
      <Route path="/pipeline/:projectId" element={<ProtectedRoute><Pipeline /></ProtectedRoute>} />
      <Route path="/exports/:projectId" element={<ProtectedRoute><Exports /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/pitch/:projectId" element={<ProtectedRoute><PitchMode /></ProtectedRoute>} />
    </Routes>
  )
}

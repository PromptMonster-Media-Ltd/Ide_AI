/**
 * App.tsx — Root router. Defines all application routes.
 */
import { Routes, Route } from 'react-router-dom'
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
      <Route path="/" element={<Home />} />
      <Route path="/discovery/:projectId" element={<Discovery />} />
      <Route path="/blocks/:projectId" element={<Blocks />} />
      <Route path="/pipeline/:projectId" element={<Pipeline />} />
      <Route path="/exports/:projectId" element={<Exports />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/pitch/:projectId" element={<PitchMode />} />
    </Routes>
  )
}

/**
 * Home — Idea input landing page with nebula canvas background.
 * @module pages/Home
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Sidebar } from '../components/layout/Sidebar'
import { IdeaNebulaCanvas } from '../components/nebula/IdeaNebulaCanvas'
import apiClient from '../lib/apiClient'

const PLATFORMS = ['Bubble', 'Webflow', 'FlutterFlow', 'Bolt', 'Lovable', 'Claude Code', 'Cursor', 'Replit', 'n8n', 'Custom']
const AUDIENCES = ['Consumers', 'Businesses', 'Internal Team', 'Developers']
const COMPLEXITIES = ['Simple (1-5 screens)', 'Medium (5-15)', 'Complex (15+)']
const TONES = ['Formal', 'Casual', 'Technical', 'Startup-style']

export function Home() {
  const navigate = useNavigate()
  const [idea, setIdea] = useState('')
  const [platform, setPlatform] = useState('Custom')
  const [audience, setAudience] = useState('Consumers')
  const [complexity, setComplexity] = useState('Medium (5-15)')
  const [tone, setTone] = useState('Casual')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!idea.trim()) return
    setLoading(true)
    try {
      const { data } = await apiClient.post('/projects', {
        name: idea.slice(0, 100),
        description: idea,
        platform: platform.toLowerCase().replace(/\s+/g, '-'),
        audience: audience.toLowerCase().replace(/\s+/g, '-'),
        complexity: complexity.split(' ')[0].toLowerCase(),
        tone: tone.toLowerCase().replace(/-/g, '_'),
      })
      navigate(`/discovery/${data.id}`)
    } catch {
      // TODO: toast error
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="ml-[232px] flex flex-col items-center justify-center min-h-screen px-6">
        <IdeaNebulaCanvas />

        {/* Hero */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-white mb-3">
            What do you want to <span className="text-accent">build</span>?
          </h1>
          <p className="text-text-muted text-lg">Describe your idea and let AI forge it into a complete design kit.</p>
        </motion.div>

        {/* Input */}
        <motion.div
          className="w-full max-w-2xl mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your product in one sentence..."
            className="w-full bg-surface border border-border rounded-xl px-6 py-4 text-white text-lg placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors resize-none h-28"
          />
        </motion.div>

        {/* Selector Chips */}
        <motion.div
          className="w-full max-w-2xl space-y-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <ChipRow label="Platform" options={PLATFORMS} value={platform} onChange={setPlatform} />
          <ChipRow label="Audience" options={AUDIENCES} value={audience} onChange={setAudience} />
          <ChipRow label="Complexity" options={COMPLEXITIES} value={complexity} onChange={setComplexity} />
          <ChipRow label="Tone" options={TONES} value={tone} onChange={setTone} />
        </motion.div>

        {/* Submit */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Button size="lg" onClick={handleSubmit} disabled={!idea.trim() || loading}>
            {loading ? 'Creating...' : 'Start Discovery →'}
          </Button>
        </motion.div>
      </main>
    </div>
  )
}

function ChipRow({ label, options, value, onChange }: {
  label: string
  options: string[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div>
      <label className="text-xs text-text-muted font-medium mb-2 block">{label}</label>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              value === opt
                ? 'bg-accent text-background'
                : 'bg-white/5 text-text-muted hover:text-white hover:bg-white/10 border border-border'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

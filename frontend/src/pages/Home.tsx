/**
 * Home -- Idea input landing page with nebula canvas background
 * and design scheme preset cards.
 * @module pages/Home
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Sidebar } from '../components/layout/Sidebar'
import { IdeaNebulaCanvas } from '../components/nebula/IdeaNebulaCanvas'
import { PresetCard } from '../components/home/PresetCard'
import { DESIGN_PRESETS } from '../components/home/designPresets'
import type { DesignPresetDefaults } from '../components/home/designPresets'
import apiClient from '../lib/apiClient'

/* ── Option lists for the Customize section ─────────────────────── */
const PLATFORMS = [
  'Mobile', 'Web', 'Desktop', 'Browser Extension',
  'Bubble', 'Webflow', 'FlutterFlow', 'Bolt', 'Lovable',
  'Claude Code', 'Cursor', 'Replit', 'n8n', 'Custom',
]
const AUDIENCES = ['Consumers', 'Businesses', 'Internal Team', 'Developers']
const COMPLEXITIES = ['Simple (1-5 screens)', 'Medium (5-15)', 'Complex (15+)']
const TONES = ['Formal', 'Casual', 'Technical', 'Startup-style']

/* ── Helpers to map preset defaults <-> display values ───────────── */
const COMPLEXITY_MAP: Record<string, string> = {
  simple: 'Simple (1-5 screens)',
  medium: 'Medium (5-15)',
  complex: 'Complex (15+)',
}

const AUDIENCE_MAP: Record<string, string> = {
  consumers: 'Consumers',
  businesses: 'Businesses',
  'internal-team': 'Internal Team',
  developers: 'Developers',
}

const TONE_MAP: Record<string, string> = {
  formal: 'Formal',
  casual: 'Casual',
  technical: 'Technical',
  startup: 'Startup-style',
}

/** Convert lowercase preset defaults into the display strings used by ChipRows. */
function presetDefaultsToDisplay(defaults: DesignPresetDefaults) {
  return {
    platform: defaults.platform,
    complexity: COMPLEXITY_MAP[defaults.complexity] ?? defaults.complexity,
    audience: AUDIENCE_MAP[defaults.audience] ?? defaults.audience,
    tone: TONE_MAP[defaults.tone] ?? defaults.tone,
  }
}

/* ── Page ─────────────────────────────────────────────────────────── */
export function Home() {
  const navigate = useNavigate()
  const [idea, setIdea] = useState('')
  const [platform, setPlatform] = useState('Custom')
  const [audience, setAudience] = useState('Consumers')
  const [complexity, setComplexity] = useState('Medium (5-15)')
  const [tone, setTone] = useState('Casual')
  const [loading, setLoading] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [showCustomize, setShowCustomize] = useState(false)
  const [displayName, setDisplayName] = useState<string | null>(null)

  /* Fetch user profile for greeting */
  useEffect(() => {
    apiClient.get('/auth/me')
      .then(({ data }) => {
        setDisplayName(data.display_name || data.name || data.email?.split('@')[0] || null)
      })
      .catch(() => { /* Silently ignore — greeting just won't show */ })
  }, [])

  /* Apply a preset -- fills all four fields at once */
  const handlePresetSelect = (presetId: string) => {
    if (selectedPreset === presetId) {
      // Deselect
      setSelectedPreset(null)
      return
    }
    const preset = DESIGN_PRESETS.find((p) => p.id === presetId)
    if (!preset) return
    const display = presetDefaultsToDisplay(preset.defaults)
    setPlatform(display.platform)
    setComplexity(display.complexity)
    setAudience(display.audience)
    setTone(display.tone)
    setSelectedPreset(presetId)
    setShowCustomize(false)
  }

  /* Submit -- unchanged; normalizes values before POST */
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
      <main className="ml-0 md:ml-[232px] flex flex-col items-center justify-center min-h-screen px-4 md:px-6 pb-20 md:pb-0">
        <IdeaNebulaCanvas />

        {/* Greeting */}
        {displayName && (
          <motion.div
            className="text-center"
            style={{ paddingTop: 50 }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-lg md:text-2xl font-semibold text-white/80">
              Hi <span className="text-accent">{displayName}</span>
            </h2>
          </motion.div>
        )}

        {/* Hero */}
        <motion.div
          className="text-center mb-8 md:mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-2xl md:text-4xl font-bold text-white mb-3">
            What do you want to <span className="text-accent">build</span>?
          </h1>
          <p className="text-text-muted text-sm md:text-lg">
            Describe your idea and let AI forge it into a complete design kit.
          </p>
        </motion.div>

        {/* Idea textarea */}
        <motion.div
          className="w-full max-w-2xl mb-6 md:mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your product in one sentence..."
            className="w-full bg-surface border border-border rounded-xl px-4 md:px-6 py-3 md:py-4 text-white text-base md:text-lg placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors resize-none h-24 md:h-28"
          />
        </motion.div>

        {/* Design Scheme Presets */}
        <motion.div
          className="w-full max-w-2xl mb-4 md:mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <label className="text-xs text-text-muted font-medium mb-3 block">
            Design Scheme
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {DESIGN_PRESETS.map((preset) => (
              <PresetCard
                key={preset.id}
                icon={preset.icon}
                name={preset.name}
                description={preset.description}
                selected={selectedPreset === preset.id}
                onClick={() => handlePresetSelect(preset.id)}
              />
            ))}
          </div>
        </motion.div>

        {/* Customize toggle */}
        <motion.div
          className="w-full max-w-2xl mb-6 md:mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.35 }}
        >
          <button
            type="button"
            onClick={() => setShowCustomize((prev) => !prev)}
            className="flex items-center gap-2 text-xs text-text-muted hover:text-white transition-colors font-medium"
          >
            <svg
              className={`w-3.5 h-3.5 transition-transform duration-200 ${showCustomize ? 'rotate-90' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            {showCustomize ? 'Hide options' : 'Customize options'}
            {selectedPreset && !showCustomize && (
              <span className="text-accent/70 ml-1">
                -- {platform} / {complexity.split(' ')[0]} / {audience} / {tone}
              </span>
            )}
          </button>

          <AnimatePresence>
            {(showCustomize || !selectedPreset) && (
              <motion.div
                className="space-y-3 md:space-y-4 mt-4"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
              >
                <ChipRow
                  label="Platform"
                  options={PLATFORMS}
                  value={platform}
                  onChange={(v) => { setPlatform(v); setSelectedPreset(null) }}
                />
                <ChipRow
                  label="Audience"
                  options={AUDIENCES}
                  value={audience}
                  onChange={(v) => { setAudience(v); setSelectedPreset(null) }}
                />
                <ChipRow
                  label="Complexity"
                  options={COMPLEXITIES}
                  value={complexity}
                  onChange={(v) => { setComplexity(v); setSelectedPreset(null) }}
                />
                <ChipRow
                  label="Tone"
                  options={TONES}
                  value={tone}
                  onChange={(v) => { setTone(v); setSelectedPreset(null) }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Submit */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Button size="lg" onClick={handleSubmit} disabled={!idea.trim() || loading}>
            {loading ? 'Creating...' : 'Start Discovery \u2192'}
          </Button>
        </motion.div>
      </main>
    </div>
  )
}

/* ── ChipRow (unchanged from original) ────────────────────────────── */
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
            className={`px-2.5 md:px-3 py-1 md:py-1.5 rounded-lg text-[11px] md:text-xs font-medium transition-all ${
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

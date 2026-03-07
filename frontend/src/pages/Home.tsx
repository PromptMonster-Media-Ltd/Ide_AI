/**
 * Home -- Idea input landing page with nebula canvas background
 * and design scheme preset cards.
 * @module pages/Home
 */
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
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

        {/* Idea textarea with inline pill dropdowns */}
        <motion.div
          className="w-full max-w-2xl mb-6 md:mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="bg-surface border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent/30 transition-colors overflow-visible">
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your product in one sentence..."
              className="w-full bg-transparent px-4 md:px-6 pt-3 md:pt-4 pb-2 text-white text-base md:text-lg placeholder:text-text-muted focus:outline-none resize-none h-20 md:h-24"
            />
            <div className="flex flex-wrap gap-1.5 px-3 md:px-5 pb-3">
              <PillDropdown label="Platform" value={platform} options={PLATFORMS} onChange={(v) => { setPlatform(v); setSelectedPreset(null) }} />
              <PillDropdown label="Audience" value={audience} options={AUDIENCES} onChange={(v) => { setAudience(v); setSelectedPreset(null) }} />
              <PillDropdown label="Complexity" value={complexity} options={COMPLEXITIES} onChange={(v) => { setComplexity(v); setSelectedPreset(null) }} />
              <PillDropdown label="Tone" value={tone} options={TONES} onChange={(v) => { setTone(v); setSelectedPreset(null) }} />
            </div>
          </div>
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

        {/* Spacer between presets and submit */}
        <div className="mb-2" />

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

/* ── PillDropdown — inline pill with floating option list ───────────── */
function PillDropdown({ label, value, options, onChange }: {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  // Shorten display value for compact pills
  const display = value.length > 14 ? value.split(' ')[0] : value

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((p) => !p)}
        className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all border ${
          open
            ? 'border-accent bg-accent/15 text-accent'
            : 'border-border bg-white/5 text-text-muted hover:text-white hover:bg-white/10'
        }`}
      >
        <span className="opacity-50 mr-0.5">{label}:</span>
        {display}
        <svg className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute bottom-full left-0 mb-1.5 z-50 bg-surface border border-border rounded-lg shadow-xl py-1 min-w-[160px] max-h-52 overflow-y-auto">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => { onChange(opt); setOpen(false) }}
              className={`w-full text-left px-3 py-1.5 text-xs transition-colors ${
                value === opt
                  ? 'bg-accent/15 text-accent font-medium'
                  : 'text-text-muted hover:text-white hover:bg-white/5'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Home -- Idea input landing page with nebula canvas background,
 * pathway picker, and AI-powered hybrid pathway detection.
 *
 * Flow (when multiple pathways exist):
 * 1. User types idea + optional field tweaks
 * 2. Clicks "Start Discovery"
 * 3. AI detects pathway → confirmation step shown
 * 4. User confirms or overrides → project created
 *
 * When only one pathway exists, step 3-4 are skipped.
 * @module pages/Home
 */
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Sidebar } from '../components/layout/Sidebar'
import { IdeaNebulaCanvas } from '../components/nebula/IdeaNebulaCanvas'
import { PresetCard } from '../components/home/PresetCard'
import { usePathwayStore } from '../stores/pathwayStore'
import type { PathwayDefinition, CreationPreset, CreationField } from '../types/pathway'
import apiClient from '../lib/apiClient'

/* ── Helpers ──────────────────────────────────────────────────── */

function resolvePresetValue(_fieldId: string, rawValue: string, options: string[]): string {
  const exact = options.find(o => o.toLowerCase() === rawValue.toLowerCase())
  if (exact) return exact
  const partial = options.find(o => o.toLowerCase().startsWith(rawValue.toLowerCase()))
  if (partial) return partial
  return rawValue
}

/* ── Page ─────────────────────────────────────────────────────── */
export function Home() {
  const navigate = useNavigate()
  const { pathways, active: activePathway, fetchPathways, setActive } = usePathwayStore()

  const [idea, setIdea] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [displayName, setDisplayName] = useState<string | null>(null)
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({})

  // Pathway confirmation state (hybrid detection UX)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [detectedPathwayId, setDetectedPathwayId] = useState<string | null>(null)
  const [detectionReasoning, setDetectionReasoning] = useState('')
  const [detecting, setDetecting] = useState(false)

  // Fetch pathways + user profile on mount
  useEffect(() => { fetchPathways() }, [fetchPathways])
  useEffect(() => {
    apiClient.get('/auth/me')
      .then(({ data }) => {
        setDisplayName(data.display_name || data.name || data.email?.split('@')[0] || null)
      })
      .catch(() => {})
  }, [])

  // Initialize field defaults when pathway changes
  const creationFields: CreationField[] = activePathway?.creation_fields ?? []
  const creationPresets: CreationPreset[] = activePathway?.creation_presets ?? []

  useEffect(() => {
    if (creationFields.length === 0) return
    setFieldValues(prev => {
      const next: Record<string, string> = {}
      for (const f of creationFields) {
        next[f.id] = prev[f.id] ?? f.options[0] ?? ''
      }
      return next
    })
  }, [activePathway?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const handlePresetSelect = (presetId: string) => {
    if (selectedPreset === presetId) { setSelectedPreset(null); return }
    const preset = creationPresets.find(p => p.id === presetId)
    if (!preset) return
    const newValues: Record<string, string> = {}
    for (const field of creationFields) {
      const raw = preset.defaults[field.id]
      newValues[field.id] = raw
        ? resolvePresetValue(field.id, raw, field.options)
        : fieldValues[field.id] ?? field.options[0] ?? ''
    }
    setFieldValues(newValues)
    setSelectedPreset(presetId)
  }

  const handlePathwaySelect = (pw: PathwayDefinition) => {
    setActive(pw.id)
    setSelectedPreset(null)
  }

  /** Create the project and navigate to discovery. */
  const createProject = async (pathwayId: string) => {
    const normalized: Record<string, string> = {}
    for (const [key, val] of Object.entries(fieldValues)) {
      normalized[key] = val.split(' ')[0].toLowerCase().replace(/\s+/g, '-')
    }
    const { data } = await apiClient.post('/projects', {
      name: idea.slice(0, 100),
      description: idea,
      pathway_id: pathwayId,
      ...normalized,
    })
    navigate(`/discovery/${data.id}`)
  }

  /** Main submit handler — detect pathway first if multiple exist. */
  const handleSubmit = async () => {
    if (!idea.trim()) return
    setLoading(true)

    try {
      // If only one pathway, skip detection
      if (pathways.length <= 1) {
        await createProject(activePathway?.id ?? 'software_product')
        return
      }

      // AI-detect pathway
      setDetecting(true)
      const { data } = await apiClient.post('/pathways/detect', {
        description: idea,
      })
      setDetecting(false)

      const detectedId = data.pathway_id ?? 'software_product'
      setDetectedPathwayId(detectedId)
      setDetectionReasoning(data.reasoning ?? '')
      setActive(detectedId)
      setShowConfirmation(true)
      setLoading(false)
    } catch {
      // On error, just create with current pathway
      setDetecting(false)
      try {
        await createProject(activePathway?.id ?? 'software_product')
      } catch {
        setLoading(false)
      }
    }
  }

  /** Confirm the detected pathway and create project. */
  const handleConfirm = async () => {
    setLoading(true)
    setShowConfirmation(false)
    try {
      await createProject(activePathway?.id ?? detectedPathwayId ?? 'software_product')
    } catch {
      setLoading(false)
    }
  }

  /** Override with a different pathway in the confirmation step. */
  const handleOverride = (pw: PathwayDefinition) => {
    setActive(pw.id)
    setDetectedPathwayId(pw.id)
  }

  const showPathwayPicker = pathways.length > 1

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
            What do you want to <span className="text-accent">create</span>?
          </h1>
          <p className="text-text-muted text-sm md:text-lg">
            Describe your idea and let AI forge it into a complete design kit.
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          {!showConfirmation ? (
            <motion.div
              key="input"
              className="w-full flex flex-col items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Pathway Picker — shown when multiple pathways exist */}
              {showPathwayPicker && (
                <div className="w-full max-w-2xl mb-4 md:mb-6">
                  <label className="text-xs text-text-muted font-medium mb-3 block">
                    Project Type
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {pathways.map(pw => (
                      <button
                        key={pw.id}
                        type="button"
                        onClick={() => handlePathwaySelect(pw)}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all border ${
                          activePathway?.id === pw.id
                            ? 'border-accent bg-accent/10 text-accent shadow-[0_0_12px_rgba(0,229,255,0.08)]'
                            : 'border-border bg-white/5 text-text-muted hover:text-white hover:bg-white/10'
                        }`}
                      >
                        <span className="text-lg">{pw.icon}</span>
                        <span className="font-medium">{pw.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Idea textarea with inline pill dropdowns */}
              <div className="w-full max-w-2xl mb-6 md:mb-8">
                <div className="bg-surface border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent/30 transition-colors overflow-visible">
                  <textarea
                    value={idea}
                    onChange={(e) => setIdea(e.target.value)}
                    placeholder="Describe your idea in one sentence..."
                    className="w-full bg-transparent px-4 md:px-6 pt-3 md:pt-4 pb-2 text-white text-base md:text-lg placeholder:text-text-muted focus:outline-none resize-none h-20 md:h-24"
                  />
                  <div className="flex flex-wrap gap-1.5 px-3 md:px-5 pb-3">
                    {creationFields.map(field => (
                      <PillDropdown
                        key={field.id}
                        label={field.label}
                        value={fieldValues[field.id] ?? field.options[0] ?? ''}
                        options={field.options}
                        onChange={(v) => {
                          setFieldValues(prev => ({ ...prev, [field.id]: v }))
                          setSelectedPreset(null)
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Quick Start Presets */}
              {creationPresets.length > 0 && (
                <div className="w-full max-w-2xl mb-4 md:mb-6">
                  <label className="text-xs text-text-muted font-medium mb-3 block">
                    Quick Start
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                    {creationPresets.map((preset) => (
                      <PresetCard
                        key={preset.id}
                        icon={preset.icon}
                        name={preset.name}
                        description=""
                        selected={selectedPreset === preset.id}
                        onClick={() => handlePresetSelect(preset.id)}
                      />
                    ))}
                  </div>
                </div>
              )}

              <div className="mb-2" />

              {/* Submit */}
              <Button size="lg" onClick={handleSubmit} disabled={!idea.trim() || loading}>
                {detecting ? 'Analyzing idea...' : loading ? 'Creating...' : 'Start Discovery \u2192'}
              </Button>
            </motion.div>
          ) : (
            /* ── Pathway Confirmation Step ── */
            <motion.div
              key="confirm"
              className="w-full max-w-2xl flex flex-col items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="bg-surface border border-border rounded-xl p-6 md:p-8 w-full mb-6">
                <div className="text-center mb-6">
                  <span className="text-4xl mb-3 block">{activePathway?.icon}</span>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    I think this is a <span className="text-accent">{activePathway?.name}</span> project
                  </h3>
                  {detectionReasoning && (
                    <p className="text-sm text-text-muted">{detectionReasoning}</p>
                  )}
                </div>

                <p className="text-xs text-text-muted text-center mb-4">Is that right? Or pick a different type:</p>

                <div className="flex flex-wrap justify-center gap-2 mb-6">
                  {pathways.map(pw => (
                    <button
                      key={pw.id}
                      type="button"
                      onClick={() => handleOverride(pw)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all border ${
                        activePathway?.id === pw.id
                          ? 'border-accent bg-accent/10 text-accent'
                          : 'border-border bg-white/5 text-text-muted hover:text-white hover:bg-white/10'
                      }`}
                    >
                      <span>{pw.icon}</span>
                      <span className="font-medium">{pw.name}</span>
                    </button>
                  ))}
                </div>

                <div className="flex gap-3 justify-center">
                  <Button
                    variant="ghost"
                    onClick={() => { setShowConfirmation(false); setLoading(false) }}
                  >
                    Back
                  </Button>
                  <Button size="lg" onClick={handleConfirm} disabled={loading}>
                    {loading ? 'Creating...' : `Yes, let's go! \u2192`}
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

/* ── PillDropdown — inline pill with floating option list ───────── */
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

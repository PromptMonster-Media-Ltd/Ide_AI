/**
 * TemplateGrid — Displays system project templates grouped by category.
 * Inline pill dropdown lets users switch categories.
 * @module components/home/TemplateGrid
 */
import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '../ui/Card'
import apiClient from '../../lib/apiClient'

export interface Template {
  id: string
  name: string
  description: string
  icon: string
  category: string
}

interface Props {
  onSelect: (template: Template) => void
  selectedId?: string | null
  /** Pre-set category from CategorySelect — hides the dropdown when provided */
  category?: string
}

/** Display labels for each concept category */
const CATEGORY_LABELS: Record<string, string> = {
  software_tech: 'Software & Tech',
  physical_product: 'Physical Product',
  built_environment: 'Built Environment',
  business_startup: 'Business & Startup',
  creative_writing: 'Creative Writing',
  research_academic: 'Research & Academic',
  art_visual: 'Art & Visual',
  music_audio: 'Music & Audio',
  film_video: 'Film & Video',
  food_hospitality: 'Food & Hospitality',
  fashion_apparel: 'Fashion & Apparel',
  education_training: 'Education & Training',
  event_experience: 'Event & Experience',
  health_wellness: 'Health & Wellness',
  social_impact: 'Social Impact',
  finance_investment: 'Finance & Investment',
}

const DEFAULT_CATEGORY = 'software_tech'

/** Module-level cache so templates survive component remounts */
let _templateCache: Template[] | null = null

export function TemplateGrid({ onSelect, selectedId, category }: Props) {
  const [templates, setTemplates] = useState<Template[]>(_templateCache ?? [])
  const [loading, setLoading] = useState(!_templateCache)
  const [activeCategory, setActiveCategory] = useState(category || DEFAULT_CATEGORY)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (_templateCache) { setTemplates(_templateCache); setLoading(false); return }
    apiClient.get('/templates').then(({ data }) => {
      _templateCache = data
      setTemplates(data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  // Sync activeCategory when category prop changes
  useEffect(() => {
    if (category) setActiveCategory(category)
  }, [category])

  // Close dropdown on outside click
  useEffect(() => {
    if (!dropdownOpen) return
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setDropdownOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [dropdownOpen])

  if (loading || templates.length === 0) return null

  // Derive available categories from data
  const categories = [...new Set(templates.map(t => t.category))].filter(c => CATEGORY_LABELS[c])
  const filtered = templates.filter(t => t.category === activeCategory)
  const label = CATEGORY_LABELS[activeCategory] || activeCategory

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 pb-[50px] md:pb-24">
      {/* Header with inline category pill */}
      <div className="flex items-center gap-1.5 text-xs font-medium text-text-muted uppercase tracking-wider mb-3">
        <span>Or start from a</span>
        <div className="relative" ref={dropdownRef}>
          {category ? (
            /* Category pre-set from CategorySelect — show as static label */
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold border border-accent/30 bg-accent/10 text-accent normal-case tracking-normal">
              {label}
            </span>
          ) : (
            /* Standalone mode — show dropdown */
            <button
              type="button"
              onClick={() => setDropdownOpen(o => !o)}
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold transition-all border normal-case tracking-normal ${
                dropdownOpen
                  ? 'border-accent bg-accent/15 text-accent'
                  : 'border-accent/30 bg-accent/10 text-accent hover:bg-accent/15'
              }`}
            >
              {label}
              <svg className={`w-3 h-3 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}
          {!category && dropdownOpen && (
            <div className="absolute top-full left-0 mt-1.5 z-50 bg-surface border border-border rounded-lg shadow-xl py-1 min-w-[140px] max-h-64 overflow-y-auto">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => { setActiveCategory(cat); setDropdownOpen(false) }}
                  className={`w-full text-left px-3 py-1.5 text-xs transition-colors ${
                    activeCategory === cat
                      ? 'bg-accent/15 text-accent font-medium'
                      : 'text-text-muted hover:text-white hover:bg-white/5'
                  }`}
                >
                  {CATEGORY_LABELS[cat] || cat}
                </button>
              ))}
            </div>
          )}
        </div>
        <span>template</span>
      </div>

      {/* Template cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        {filtered.map((t, i) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
          >
            <button
              type="button"
              onClick={() => onSelect(t)}
              className={`w-full text-left group rounded-xl transition-all ${
                selectedId === t.id
                  ? 'ring-1 ring-accent/40'
                  : ''
              }`}
            >
              <Card>
                <div className={`text-center py-1 transition-all ${
                  selectedId === t.id ? 'bg-accent/5' : ''
                }`}>
                  <span className="text-2xl block mb-1">{t.icon}</span>
                  <p className={`text-xs font-medium transition-colors truncate ${
                    selectedId === t.id ? 'text-accent' : 'text-white group-hover:text-accent'
                  }`}>
                    {t.name}
                  </p>
                  <p className="text-[10px] text-text-muted mt-0.5 line-clamp-2 leading-tight">
                    {t.description}
                  </p>
                </div>
              </Card>
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

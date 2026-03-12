/**
 * TemplateGrid — Displays system project templates as clickable cards.
 * When selected, notifies parent to populate the idea input.
 * @module components/home/TemplateGrid
 */
import { useEffect, useState } from 'react'
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
}

export function TemplateGrid({ onSelect, selectedId }: Props) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient.get('/templates').then(({ data }) => {
      setTemplates(data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading || templates.length === 0) return null

  return (
    <div className="w-full max-w-2xl mx-auto mt-6">
      <h3 className="text-xs font-medium text-text-muted uppercase tracking-wider mb-3">
        Or start from a template
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        {templates.map((t, i) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
          >
            <button
              type="button"
              onClick={() => onSelect(t)}
              className="w-full text-left group"
            >
              <Card>
                <div className={`text-center py-1 rounded-lg transition-all ${
                  selectedId === t.id
                    ? 'ring-1 ring-accent/40 bg-accent/5'
                    : ''
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

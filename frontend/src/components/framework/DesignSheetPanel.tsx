/**
 * DesignSheetPanel — Live-updating sidebar with extracted design fields.
 * Accepts pathway field configs for dynamic rendering across pathways.
 * Falls back to software-product fields when none provided.
 * @module components/framework/DesignSheetPanel
 */
import { Badge } from '../ui/Badge'
import type { SheetFieldConfig } from '../../types/pathway'

interface SheetData {
  problem?: string
  audience?: string
  mvp?: string
  features?: Array<{ name: string; description?: string; priority?: string }>
  tone?: string
  platform?: string
  tech_constraints?: string
  success_metric?: string
  confidence_score: number
  fields_data?: Record<string, unknown>
}

const DEFAULT_FIELDS: SheetFieldConfig[] = [
  { key: 'problem', label: 'Problem', field_type: 'textarea' },
  { key: 'audience', label: 'Audience', field_type: 'text' },
  { key: 'mvp', label: 'MVP Scope', field_type: 'textarea' },
  { key: 'platform', label: 'Platform', field_type: 'text' },
  { key: 'tone', label: 'Tone', field_type: 'text' },
  { key: 'tech_constraints', label: 'Constraints', field_type: 'textarea' },
  { key: 'success_metric', label: 'Success Metric', field_type: 'text' },
]

/** Named columns on the DesignSheet model (software pathway). */
const NAMED_COLUMNS = new Set([
  'problem', 'audience', 'mvp', 'tone', 'platform',
  'tech_constraints', 'success_metric', 'features',
])

interface Props {
  sheet: SheetData
  fieldConfigs?: SheetFieldConfig[]
}

/** Resolve a field value — checks named columns first, then fields_data. */
function getFieldValue(sheet: SheetData, key: string): unknown {
  if (NAMED_COLUMNS.has(key)) {
    return (sheet as Record<string, unknown>)[key]
  }
  return sheet.fields_data?.[key]
}

export function DesignSheetPanel({ sheet, fieldConfigs }: Props) {
  const configs = fieldConfigs && fieldConfigs.length > 0 ? fieldConfigs : DEFAULT_FIELDS

  // Separate "features" (list type) from scalar fields
  const scalarFields = configs.filter(f => f.field_type !== 'list')
  const listFields = configs.filter(f => f.field_type === 'list')

  return (
    <div className="h-full overflow-y-auto p-3 md:p-4 space-y-4">
      {/* Confidence */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-text-muted font-medium">Confidence</span>
          <span className="text-sm font-bold text-accent">{sheet.confidence_score}%</span>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-500"
            style={{ width: `${sheet.confidence_score}%` }}
          />
        </div>
      </div>

      {/* Scalar Fields */}
      {scalarFields.map(({ key, label }) => {
        const value = getFieldValue(sheet, key)
        const display = typeof value === 'string' ? value : value ? String(value) : null
        return (
          <div key={key}>
            <span className="text-xs text-text-muted font-medium block mb-1">{label}</span>
            {display ? (
              <p className="text-sm text-white break-words">{display}</p>
            ) : (
              <p className="text-xs text-text-muted italic">Awaiting discovery...</p>
            )}
          </div>
        )
      })}

      {/* List Fields (features, etc.) */}
      {listFields.map(({ key, label }) => {
        const value = getFieldValue(sheet, key)
        const items = Array.isArray(value) ? value : []
        if (items.length === 0) return null
        return (
          <div key={key}>
            <span className="text-xs text-text-muted font-medium block mb-2">{label}</span>
            <div className="space-y-1.5">
              {items.map((item, i) => {
                const name = typeof item === 'string' ? item : item?.name ?? String(item)
                const priority = typeof item === 'object' ? item?.priority : null
                return (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-xs text-white">{name}</span>
                    {priority && (
                      <Badge variant={priority === 'mvp' ? 'accent' : 'default'}>
                        {String(priority).toUpperCase()}
                      </Badge>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

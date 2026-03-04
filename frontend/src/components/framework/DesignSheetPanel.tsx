/**
 * DesignSheetPanel — Live-updating sidebar with extracted design fields.
 * @module components/framework/DesignSheetPanel
 */
import { Badge } from '../ui/Badge'

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
}

export function DesignSheetPanel({ sheet }: { sheet: SheetData }) {
  const fields = [
    { label: 'Problem', value: sheet.problem },
    { label: 'Audience', value: sheet.audience },
    { label: 'MVP Scope', value: sheet.mvp },
    { label: 'Platform', value: sheet.platform },
    { label: 'Tone', value: sheet.tone },
    { label: 'Constraints', value: sheet.tech_constraints },
    { label: 'Success Metric', value: sheet.success_metric },
  ]

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
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

      {/* Fields */}
      {fields.map(({ label, value }) => (
        <div key={label}>
          <span className="text-xs text-text-muted font-medium block mb-1">{label}</span>
          {value ? (
            <p className="text-sm text-white">{value}</p>
          ) : (
            <p className="text-xs text-text-muted italic">Awaiting discovery...</p>
          )}
        </div>
      ))}

      {/* Features */}
      {sheet.features && sheet.features.length > 0 && (
        <div>
          <span className="text-xs text-text-muted font-medium block mb-2">Features</span>
          <div className="space-y-1.5">
            {sheet.features.map((f, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-white">{f.name}</span>
                {f.priority && (
                  <Badge variant={f.priority === 'mvp' ? 'accent' : 'default'}>
                    {f.priority.toUpperCase()}
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

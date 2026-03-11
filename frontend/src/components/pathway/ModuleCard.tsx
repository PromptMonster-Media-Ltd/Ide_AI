/**
 * ModuleCard — Card UI for a module in the pathway review or progress display.
 * Shows module name, purpose, estimated time, mode toggle, and AI reasoning.
 */
import type { PathwayModuleEntry } from '../../types/modulePathway'

interface ModuleCardProps {
  module: PathwayModuleEntry
  index: number
  status?: 'pending' | 'active' | 'complete' | 'skipped'
  onToggleMode?: (moduleId: string, mode: 'lite' | 'deep') => void
  onRemove?: (moduleId: string) => void
  onStart?: (moduleId: string) => void
  isEditable?: boolean
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'border-white/10',
  active: 'border-accent/60 shadow-accent/20 shadow-lg',
  complete: 'border-green-500/40',
  skipped: 'border-yellow-500/30 opacity-60',
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  active: 'In Progress',
  complete: 'Complete',
  skipped: 'Skipped',
}

export function ModuleCard({
  module,
  index,
  status = 'pending',
  onToggleMode,
  onRemove,
  onStart,
  isEditable = false,
}: ModuleCardProps) {
  const borderColor = STATUS_COLORS[status] ?? STATUS_COLORS.pending

  return (
    <div
      className={`relative rounded-xl border ${borderColor} bg-white/[0.03] backdrop-blur-sm p-4 transition-all hover:bg-white/[0.06]`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <span className="flex-shrink-0 w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-xs font-medium text-text-muted">
            {index + 1}
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-white truncate">{module.label}</h3>
            <p className="text-xs text-text-muted mt-0.5">{module.group}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-text-muted">{module.estimated_time}</span>
          {status !== 'pending' && (
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                status === 'complete'
                  ? 'bg-green-500/20 text-green-400'
                  : status === 'active'
                  ? 'bg-accent/20 text-accent'
                  : status === 'skipped'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-white/10 text-text-muted'
              }`}
            >
              {STATUS_LABELS[status]}
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-text-muted mt-2 line-clamp-2">{module.description}</p>

      {/* AI Reasoning */}
      {module.reason && (
        <p className="text-[11px] text-accent/70 mt-2 italic">
          {module.reason}
        </p>
      )}

      {/* Controls row */}
      <div className="flex items-center justify-between mt-3 pt-2 border-t border-white/5">
        {/* Mode toggle */}
        {isEditable && onToggleMode ? (
          <div className="flex items-center gap-1 bg-white/5 rounded-lg p-0.5">
            <button
              type="button"
              onClick={() => onToggleMode(module.module_id, 'lite')}
              className={`text-[11px] px-2.5 py-1 rounded-md transition-colors ${
                module.mode === 'lite'
                  ? 'bg-accent/20 text-accent font-medium'
                  : 'text-text-muted hover:text-white'
              }`}
            >
              Lite
            </button>
            <button
              type="button"
              onClick={() => onToggleMode(module.module_id, 'deep')}
              className={`text-[11px] px-2.5 py-1 rounded-md transition-colors ${
                module.mode === 'deep'
                  ? 'bg-accent/20 text-accent font-medium'
                  : 'text-text-muted hover:text-white'
              }`}
            >
              Deep
            </button>
          </div>
        ) : (
          <span className="text-[11px] text-text-muted capitalize">{module.mode} mode</span>
        )}

        <div className="flex items-center gap-2">
          {isEditable && onRemove && (
            <button
              type="button"
              onClick={() => onRemove(module.module_id)}
              className="text-[11px] text-red-400/70 hover:text-red-400 transition-colors"
            >
              Remove
            </button>
          )}
          {status === 'pending' && onStart && (
            <button
              type="button"
              onClick={() => onStart(module.module_id)}
              className="text-[11px] px-3 py-1 rounded-md bg-accent/20 text-accent hover:bg-accent/30 transition-colors font-medium"
            >
              Start
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

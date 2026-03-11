/**
 * PathwayProgress — Visual progress indicator showing all modules,
 * current position, and completion status.
 */
import type { PathwayModuleEntry, ModuleResponseRecord } from '../../types/modulePathway'

interface PathwayProgressProps {
  modules: PathwayModuleEntry[]
  responses: ModuleResponseRecord[]
  activeModuleId: string | null
  onModuleClick?: (moduleId: string) => void
}

function getModuleStatus(
  moduleId: string,
  responses: ModuleResponseRecord[],
  activeModuleId: string | null,
): 'pending' | 'active' | 'complete' | 'skipped' {
  if (moduleId === activeModuleId) return 'active'
  const resp = responses.find(r => r.module_id === moduleId)
  if (!resp) return 'pending'
  return resp.status as 'pending' | 'active' | 'complete' | 'skipped'
}

const STATUS_DOT: Record<string, string> = {
  pending: 'bg-white/20',
  active: 'bg-accent animate-pulse',
  complete: 'bg-green-500',
  skipped: 'bg-yellow-500/60',
}

export function PathwayProgress({ modules, responses, activeModuleId, onModuleClick }: PathwayProgressProps) {
  const completedCount = responses.filter(r => r.status === 'complete' || r.status === 'skipped').length
  const progress = modules.length > 0 ? Math.round((completedCount / modules.length) * 100) : 0

  return (
    <div className="w-full">
      {/* Progress bar */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-text-muted font-medium">
          {completedCount}/{modules.length} modules
        </span>
        <span className="text-xs text-accent font-medium">{progress}%</span>
      </div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-accent to-accent/60 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Module list */}
      <div className="space-y-1">
        {modules.map((mod, i) => {
          const status = getModuleStatus(mod.module_id, responses, activeModuleId)
          return (
            <button
              key={mod.module_id}
              type="button"
              onClick={() => onModuleClick?.(mod.module_id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                status === 'active'
                  ? 'bg-accent/10 border border-accent/30'
                  : 'hover:bg-white/[0.04]'
              }`}
            >
              <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${STATUS_DOT[status]}`} />
              <span className="text-xs text-text-muted flex-shrink-0 w-5">{i + 1}.</span>
              <span
                className={`text-sm truncate ${
                  status === 'active' ? 'text-accent font-medium' :
                  status === 'complete' ? 'text-green-400' :
                  status === 'skipped' ? 'text-yellow-400/70 line-through' :
                  'text-white/70'
                }`}
              >
                {mod.label}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

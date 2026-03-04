/**
 * StagesStepper — Vertical 5-stage progress indicator.
 * @module components/discovery/StagesStepper
 */

const STAGES = [
  { id: 'greeting', label: 'Welcome', icon: '👋' },
  { id: 'problem', label: 'Problem', icon: '🎯' },
  { id: 'audience', label: 'Audience', icon: '👥' },
  { id: 'features', label: 'Features', icon: '◫' },
  { id: 'constraints', label: 'Constraints', icon: '⚙' },
  { id: 'confirm', label: 'Confirm', icon: '✓' },
]

const STAGE_ORDER = STAGES.map(s => s.id)

export function StagesStepper({ currentStage }: { currentStage: string }) {
  const currentIndex = STAGE_ORDER.indexOf(currentStage)

  return (
    <div className="flex flex-col gap-1 py-4">
      {STAGES.map((stage, i) => {
        const isComplete = i < currentIndex
        const isCurrent = i === currentIndex

        return (
          <div key={stage.id} className="flex items-center gap-3 px-4 py-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs shrink-0 transition-all ${
              isComplete ? 'bg-accent text-background' :
              isCurrent ? 'bg-accent/20 text-accent border border-accent' :
              'bg-white/5 text-text-muted border border-border'
            }`}>
              {isComplete ? '✓' : stage.icon}
            </div>
            <span className={`text-xs font-medium transition-colors ${
              isCurrent ? 'text-accent' : isComplete ? 'text-white' : 'text-text-muted'
            }`}>
              {stage.label}
            </span>
          </div>
        )
      })}
    </div>
  )
}

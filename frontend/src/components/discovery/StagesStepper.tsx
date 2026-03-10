/**
 * StagesStepper — Vertical stage progress indicator.
 * Accepts pathway stages as props for dynamic discovery flows.
 * Falls back to software-product stages when none provided.
 * @module components/discovery/StagesStepper
 */
import type { StageConfig } from '../../types/pathway'

const DEFAULT_STAGES: StageConfig[] = [
  { id: 'greeting', label: 'Welcome', icon: '\u{1F44B}' },
  { id: 'problem', label: 'Problem', icon: '\u{1F3AF}' },
  { id: 'audience', label: 'Audience', icon: '\u{1F465}' },
  { id: 'features', label: 'Features', icon: '\u25EB' },
  { id: 'constraints', label: 'Constraints', icon: '\u2699' },
  { id: 'confirm', label: 'Confirm', icon: '\u2713' },
]

interface Props {
  currentStage: string
  stages?: StageConfig[]
}

export function StagesStepper({ currentStage, stages }: Props) {
  const stageList = stages && stages.length > 0 ? stages : DEFAULT_STAGES
  const stageIds = stageList.map(s => s.id)
  const currentIndex = stageIds.indexOf(currentStage)

  return (
    <div className="flex flex-col gap-1 py-4">
      {stageList.map((stage, i) => {
        const isComplete = i < currentIndex
        const isCurrent = i === currentIndex

        return (
          <div key={stage.id} className="flex items-center gap-3 px-4 py-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs shrink-0 transition-all ${
              isComplete ? 'bg-accent text-background' :
              isCurrent ? 'bg-accent/20 text-accent border border-accent' :
              'bg-white/5 text-text-muted border border-border'
            }`}>
              {isComplete ? '\u2713' : stage.icon}
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

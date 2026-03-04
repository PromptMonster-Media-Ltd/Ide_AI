/**
 * ReadinessScores — Four circular readiness gauges showing project completeness.
 * @module components/framework/ReadinessScores
 */
import { motion } from 'framer-motion'

interface Score {
  label: string
  value: number
  max: number
}

interface ReadinessScoresProps {
  scores: Score[]
}

function CircularGauge({ label, value, max }: Score) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0
  const circumference = 2 * Math.PI * 18
  const filled = (percentage / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-12 h-12">
        <svg className="w-12 h-12 -rotate-90" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="18" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
          <motion.circle
            cx="20" cy="20" r="18" fill="none"
            stroke="rgb(0, 229, 255)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - filled }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
          {percentage}
        </span>
      </div>
      <span className="text-[10px] text-text-muted font-medium text-center">{label}</span>
    </div>
  )
}

export function ReadinessScores({ scores }: ReadinessScoresProps) {
  return (
    <div className="flex items-center justify-around gap-4 py-3">
      {scores.map((score) => (
        <CircularGauge key={score.label} {...score} />
      ))}
    </div>
  )
}

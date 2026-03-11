/**
 * Whisper — Subtle hint text below an element, dismissed on interaction.
 */
import type { ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useTutorialStore } from '../../stores/tutorialStore'

interface WhisperProps {
  id: string
  text: string
  children: ReactNode
}

export function Whisper({ id, text, children }: WhisperProps) {
  const show = useTutorialStore((s) => !s.dismissedWhispers.includes(id))
  const dismiss = useTutorialStore((s) => s.dismissWhisper)

  if (!show) return <>{children}</>

  const handleDismiss = () => dismiss(id)

  return (
    <div onClick={handleDismiss} onFocusCapture={handleDismiss}>
      {children}
      <AnimatePresence>
        {show && (
          <motion.p
            className="text-xs italic text-text-muted/70 mt-1 pl-1"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {text}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}

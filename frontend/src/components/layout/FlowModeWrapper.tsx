/**
 * FlowModeWrapper — Full-screen distraction-free wrapper with fade transition.
 * @module components/layout/FlowModeWrapper
 */
import { motion, AnimatePresence } from 'framer-motion'

interface FlowModeWrapperProps {
  active: boolean
  onExit: () => void
  children: React.ReactNode
}

export function FlowModeWrapper({ active, onExit, children }: FlowModeWrapperProps) {
  return (
    <AnimatePresence>
      {active && (
        <motion.div
          className="fixed inset-0 z-[100] bg-background"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Exit button */}
          <button
            onClick={onExit}
            className="fixed top-4 right-4 z-[101] text-text-muted hover:text-white text-xs bg-surface/80 backdrop-blur-sm border border-border rounded-lg px-3 py-1.5 transition-colors"
          >
            Exit Flow Mode (Esc)
          </button>

          <div className="h-full overflow-auto">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * VoiceMicButton — Animated microphone button for voice discovery input.
 * Shows a pulsing ring when listening, with transcript overlay.
 * @module components/voice/VoiceMicButton
 */
import { motion } from 'framer-motion'
import { useVoiceInput } from '../../hooks/useVoiceInput'

interface VoiceMicButtonProps {
  /** Called when voice transcript updates (partial + final) */
  onTranscript: (text: string) => void
  /** Called when a final sentence is recognized */
  onFinalResult?: (text: string) => void
  /** Additional CSS class */
  className?: string
}

export function VoiceMicButton({ onTranscript, onFinalResult, className = '' }: VoiceMicButtonProps) {
  const {
    isSupported,
    isListening,
    interimText,
    toggleListening,
    error,
  } = useVoiceInput({ onTranscript, onFinalResult })

  if (!isSupported) return null

  return (
    <div className={`relative inline-flex items-center ${className}`}>
      <button
        type="button"
        onClick={toggleListening}
        className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          isListening
            ? 'bg-accent text-background'
            : 'bg-white/5 border border-border text-text-muted hover:text-accent hover:border-accent/30'
        }`}
        title={isListening ? 'Stop voice input' : 'Start voice input'}
        aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
      >
        {/* Pulsing ring when listening */}
        {isListening && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-accent"
              animate={{ scale: [1, 1.5, 1], opacity: [0.6, 0, 0.6] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border border-accent"
              animate={{ scale: [1, 1.8, 1], opacity: [0.3, 0, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
            />
          </>
        )}

        {/* Microphone icon */}
        <svg className="w-5 h-5 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          {isListening ? (
            // Stop icon (square)
            <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />
          ) : (
            // Microphone icon
            <>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
            </>
          )}
        </svg>
      </button>

      {/* Interim text indicator */}
      {isListening && interimText && (
        <motion.div
          className="absolute left-full ml-2 whitespace-nowrap bg-surface border border-border rounded-lg px-3 py-1.5 text-xs text-text-muted max-w-[200px] truncate"
          initial={{ opacity: 0, x: -4 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {interimText}...
        </motion.div>
      )}

      {/* Error tooltip */}
      {error && (
        <div className="absolute top-full mt-1 left-1/2 -translate-x-1/2 bg-red-500/10 border border-red-500/20 rounded-lg px-2 py-1 text-[10px] text-red-400 whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  )
}

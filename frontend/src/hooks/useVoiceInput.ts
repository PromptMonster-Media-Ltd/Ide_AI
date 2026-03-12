/**
 * useVoiceInput — Web Speech API hook for voice-to-text input.
 * Zero backend cost — all processing happens in the browser.
 * @module hooks/useVoiceInput
 */
import { useState, useRef, useCallback, useEffect } from 'react'

// Web Speech API types
interface SpeechRecognitionEvent {
  resultIndex: number
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionErrorEvent {
  error: string
  message?: string
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
  onstart: (() => void) | null
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

interface UseVoiceInputOptions {
  /** Called with the latest transcript (partial + final combined) */
  onTranscript?: (text: string) => void
  /** Called when a final result is available */
  onFinalResult?: (text: string) => void
  /** Language code (default: 'en-US') */
  lang?: string
  /** Whether to use continuous recognition (default: true) */
  continuous?: boolean
}

interface UseVoiceInputReturn {
  /** Whether the browser supports the Web Speech API */
  isSupported: boolean
  /** Whether voice recognition is currently active */
  isListening: boolean
  /** Current transcript text */
  transcript: string
  /** Interim (not yet finalized) text */
  interimText: string
  /** Start listening */
  startListening: () => void
  /** Stop listening */
  stopListening: () => void
  /** Toggle listening on/off */
  toggleListening: () => void
  /** Any error message */
  error: string | null
}

export function useVoiceInput(options: UseVoiceInputOptions = {}): UseVoiceInputReturn {
  const {
    onTranscript,
    onFinalResult,
    lang = 'en-US',
    continuous = true,
  } = options

  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimText, setInterimText] = useState('')
  const [error, setError] = useState<string | null>(null)

  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const transcriptRef = useRef('')

  const isSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition is not supported in this browser.')
      return
    }

    setError(null)

    const SpeechRecognitionConstructor = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognitionConstructor()
    recognition.continuous = continuous
    recognition.interimResults = true
    recognition.lang = lang

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          final += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }

      if (final) {
        const newTranscript = transcriptRef.current
          ? `${transcriptRef.current} ${final}`
          : final
        transcriptRef.current = newTranscript
        setTranscript(newTranscript)
        onTranscript?.(newTranscript)
        onFinalResult?.(final)
      }

      setInterimText(interim)
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === 'no-speech') return // Silence is fine
      if (event.error === 'aborted') return // Manual stop
      setError(`Speech recognition error: ${event.error}`)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
      setInterimText('')
    }

    recognitionRef.current = recognition
    recognition.start()
  }, [isSupported, continuous, lang, onTranscript, onFinalResult])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }
    setIsListening(false)
    setInterimText('')
  }, [])

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }, [isListening, startListening, stopListening])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [])

  return {
    isSupported,
    isListening,
    transcript,
    interimText,
    startListening,
    stopListening,
    toggleListening,
    error,
  }
}

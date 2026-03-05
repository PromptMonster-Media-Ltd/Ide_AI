/**
 * useSSE — EventSource-like hook using fetch for SSE with POST support.
 * @module hooks/useSSE
 */
import { useCallback, useRef, useState } from 'react'

interface SSEMessage {
  type: string
  content?: string
  stage?: string
  chips?: string[]
  sheet?: Record<string, unknown>
}

interface UseSSEOptions {
  onToken?: (token: string) => void
  onDone?: (data: { stage: string; chips: string[] }) => void
  onSheetUpdate?: (sheet: Record<string, unknown>) => void
  onError?: (error: Error) => void
}

export function useSSE(options: UseSSEOptions) {
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const optionsRef = useRef(options)
  optionsRef.current = options

  const send = useCallback(async (url: string, body: Record<string, unknown>) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setIsStreaming(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data: SSEMessage = JSON.parse(line.slice(6))
            if (data.type === 'token' && data.content) {
              optionsRef.current.onToken?.(data.content)
            } else if (data.type === 'done') {
              optionsRef.current.onDone?.({ stage: data.stage || '', chips: data.chips || [] })
            } else if (data.type === 'sheet_update' && data.sheet) {
              optionsRef.current.onSheetUpdate?.(data.sheet)
            }
          } catch { /* skip malformed lines */ }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        optionsRef.current.onError?.(err as Error)
      }
    } finally {
      setIsStreaming(false)
    }
  }, [])

  const abort = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { send, abort, isStreaming }
}

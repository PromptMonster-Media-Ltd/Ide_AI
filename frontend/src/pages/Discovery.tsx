/**
 * Discovery — SSE-powered AI conversation with live design sheet extraction.
 * @module pages/Discovery
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { ChatThread } from '../components/discovery/ChatThread'
import { StagesStepper } from '../components/discovery/StagesStepper'
import { QuickChips } from '../components/discovery/QuickChips'
import { DesignSheetPanel } from '../components/framework/DesignSheetPanel'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { useSSE } from '../hooks/useSSE'
import apiClient from '../lib/apiClient'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface SheetData {
  problem?: string
  audience?: string
  mvp?: string
  features?: Array<{ name: string; description?: string; priority?: string }>
  tone?: string
  platform?: string
  tech_constraints?: string
  success_metric?: string
  confidence_score: number
}

const INITIAL_CHIPS = [
  "It's a web app",
  "It's a mobile app",
  "It's an SDK or API",
  "It's a browser extension",
  "It's an internal tool",
  "I'm not sure yet — help me explore",
]

export function Discovery() {
  const { projectId } = useParams<{ projectId: string }>()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingContent, setStreamingContent] = useState('')
  const [stage, setStage] = useState('greeting')
  const [chips, setChips] = useState<string[]>(INITIAL_CHIPS)
  const [sheet, setSheet] = useState<SheetData>({ confidence_score: 0 })
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const [showSheet, setShowSheet] = useState(false)

  const { send, isStreaming } = useSSE({
    onToken: (token) => setStreamingContent((prev) => prev + token),
    onDone: (data) => {
      setStreamingContent((prev) => {
        if (prev) {
          setMessages((msgs) => [...msgs, { role: 'assistant', content: prev }])
        }
        return ''
      })
      setStage(data.stage)
      if (data.chips?.length) setChips(data.chips)
    },
    onSheetUpdate: (sheetData) => {
      setSheet((prev) => ({ ...prev, ...sheetData } as SheetData))
    },
    onError: (err) => console.error('SSE error:', err),
  })

  // Start session and trigger AI greeting on mount
  useEffect(() => {
    if (!projectId) return
    let cancelled = false

    const init = async () => {
      try {
        const { data } = await apiClient.post('/discovery/start', { project_id: projectId })
        if (cancelled) return
        setSessionId(data.id)

        if (data.messages?.length) {
          setMessages(data.messages)
          if (data.stage) setStage(data.stage)
          return // session already has messages — skip auto-greeting
        }

        if (data.stage) setStage(data.stage)

        // Auto-trigger AI greeting for fresh sessions
        const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
        if (!cancelled) {
          await send(`${baseUrl}/discovery/${data.id}/init`, {})
        }
      } catch (err) {
        console.error('Failed to start session:', err)
      }
    }

    init()
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId || !content.trim() || isStreaming) return

    setMessages((prev) => [...prev, { role: 'user', content }])
    setInput('')
    setChips([])
    setStreamingContent('')

    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    await send(`${baseUrl}/discovery/${sessionId}/message`, { content })
  }, [sessionId, isStreaming, send])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div className="h-screen bg-background flex overflow-hidden">
      <Sidebar projectId={projectId} />

      <div className="ml-0 md:ml-[232px] flex-1 flex flex-col min-h-0">
        <TopBar title="Discovery" subtitle={`Stage: ${stage}`}>
          {/* Mobile toggle for design sheet */}
          <button
            onClick={() => setShowSheet(!showSheet)}
            className="md:hidden px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/10 text-accent border border-accent/20"
          >
            {showSheet ? 'Chat' : 'Sheet'}
            {sheet.confidence_score > 0 && (
              <Badge variant="accent" className="ml-1.5">{sheet.confidence_score}%</Badge>
            )}
          </button>
        </TopBar>

        <div className="flex-1 flex min-h-0">
          {/* Left: Stepper — hidden on mobile */}
          <div className="hidden md:block w-48 border-r border-border bg-surface/30 shrink-0 overflow-y-auto">
            <StagesStepper currentStage={stage} />
          </div>

          {/* Center: Chat — hidden on mobile when sheet is shown */}
          <div className={`flex-1 flex flex-col min-h-0 ${showSheet ? 'hidden md:flex' : 'flex'}`}>
            {/* Mobile stage indicator (replaces stepper) */}
            <div className="md:hidden flex items-center gap-2 px-4 py-2 border-b border-border bg-surface/30 overflow-x-auto">
              <span className="text-[10px] text-text-muted font-medium shrink-0">Stage:</span>
              <span className="text-[10px] text-accent font-semibold shrink-0">{stage}</span>
            </div>

            <ChatThread messages={messages} streamingContent={streamingContent} />
            <QuickChips chips={chips} onSelect={sendMessage} disabled={isStreaming} />

            {/* Input */}
            <div className="border-t border-border p-3 md:p-4 shrink-0">
              <div className="flex gap-2 md:gap-3 items-end">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your response..."
                  className="flex-1 bg-surface border border-border rounded-xl px-3 md:px-4 py-2.5 md:py-3 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent resize-none h-11 md:h-12 max-h-32"
                  rows={1}
                />
                <Button onClick={() => sendMessage(input)} disabled={!input.trim() || isStreaming}>
                  Send
                </Button>
              </div>
            </div>
          </div>

          {/* Right: Design Sheet — full width on mobile when toggled, side panel on desktop */}
          <div className={`${showSheet ? 'flex' : 'hidden'} md:flex w-full md:w-72 border-l-0 md:border-l border-border bg-surface/30 shrink-0 flex-col min-h-0`}>
            <div className="px-4 py-3 border-b border-border shrink-0">
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Design Sheet</h3>
            </div>
            <div className="flex-1 overflow-y-auto">
              <DesignSheetPanel sheet={sheet} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

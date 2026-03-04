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

export function Discovery() {
  const { projectId } = useParams<{ projectId: string }>()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingContent, setStreamingContent] = useState('')
  const [stage, setStage] = useState('greeting')
  const [chips, setChips] = useState<string[]>([])
  const [sheet, setSheet] = useState<SheetData>({ confidence_score: 0 })
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

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
      setChips(data.chips)
    },
    onSheetUpdate: (sheetData) => {
      setSheet((prev) => ({ ...prev, ...sheetData } as SheetData))
    },
    onError: (err) => console.error('SSE error:', err),
  })

  // Start session on mount
  useEffect(() => {
    if (!projectId) return
    const startSession = async () => {
      try {
        const { data } = await apiClient.post('/discovery/start', { project_id: projectId })
        setSessionId(data.id)
        if (data.messages?.length) {
          setMessages(data.messages)
        }
        if (data.stage) setStage(data.stage)
      } catch (err) {
        console.error('Failed to start session:', err)
      }
    }
    startSession()
  }, [projectId])

  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId || !content.trim() || isStreaming) return

    setMessages((prev) => [...prev, { role: 'user', content }])
    setInput('')
    setChips([])
    setStreamingContent('')

    await send(`/api/v1/discovery/${sessionId}/message`, { content })
  }, [sessionId, isStreaming, send])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar projectId={projectId} />

      <div className="ml-16 flex-1 flex flex-col h-screen">
        <TopBar title="Discovery" subtitle={`Stage: ${stage}`} />

        <div className="flex-1 flex overflow-hidden">
          {/* Left: Stepper */}
          <div className="w-48 border-r border-border bg-surface/30 shrink-0">
            <StagesStepper currentStage={stage} />
          </div>

          {/* Center: Chat */}
          <div className="flex-1 flex flex-col">
            <ChatThread messages={messages} streamingContent={streamingContent} />
            <QuickChips chips={chips} onSelect={sendMessage} disabled={isStreaming} />

            {/* Input */}
            <div className="border-t border-border p-4">
              <div className="flex gap-3 items-end">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your response..."
                  className="flex-1 bg-surface border border-border rounded-xl px-4 py-3 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent resize-none h-12 max-h-32"
                  rows={1}
                />
                <Button onClick={() => sendMessage(input)} disabled={!input.trim() || isStreaming}>
                  Send
                </Button>
              </div>
            </div>
          </div>

          {/* Right: Design Sheet */}
          <div className="w-72 border-l border-border bg-surface/30 shrink-0">
            <div className="px-4 py-3 border-b border-border">
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Design Sheet</h3>
            </div>
            <DesignSheetPanel sheet={sheet} />
          </div>
        </div>
      </div>
    </div>
  )
}

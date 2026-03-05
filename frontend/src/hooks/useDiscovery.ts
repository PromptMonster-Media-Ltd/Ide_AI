/**
 * useDiscovery — Discovery session management and message handling.
 * Wraps API calls for session creation and message sending with SSE streaming.
 * @module hooks/useDiscovery
 */
import { useCallback, useEffect } from 'react'
import { useDiscoveryStore } from '../stores/discoveryStore'
import { useSSE } from './useSSE'
import apiClient from '../lib/apiClient'

export function useDiscovery(projectId: string | undefined) {
  const store = useDiscoveryStore()

  const { send, isStreaming } = useSSE({
    onToken: (token) => store.appendStreamingContent(token),
    onDone: (data) => {
      store.finalizeAssistantMessage()
      if (data.stage) store.setStage(data.stage)
      if (data.chips) store.setChips(data.chips)
    },
    onSheetUpdate: (sheetData) => store.updateSheet(sheetData),
    onError: (err) => console.error('SSE error:', err),
  })

  useEffect(() => {
    store.setIsStreaming(isStreaming)
  }, [isStreaming])

  // Start or resume session on mount
  useEffect(() => {
    if (!projectId) return
    const startSession = async () => {
      try {
        const { data } = await apiClient.post('/discovery/start', { project_id: projectId })
        store.setSessionId(data.id)
        if (data.messages?.length) store.setMessages(data.messages)
        if (data.stage) store.setStage(data.stage)
      } catch (err) {
        console.error('Failed to start discovery session:', err)
      }
    }
    startSession()

    return () => { store.reset() }
  }, [projectId])

  const sendMessage = useCallback(async (content: string) => {
    if (!store.sessionId || !content.trim() || isStreaming) return
    store.addMessage({ role: 'user', content })
    store.setChips([])
    store.setStreamingContent('')
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    await send(`${baseUrl}/discovery/${store.sessionId}/message`, { content })
  }, [store.sessionId, isStreaming, send])

  return {
    sessionId: store.sessionId,
    messages: store.messages,
    streamingContent: store.streamingContent,
    stage: store.stage,
    chips: store.chips,
    sheet: store.sheet,
    isStreaming,
    sendMessage,
  }
}

/**
 * discoveryStore — Session state, messages, stage, design sheet, and confidence.
 * @module stores/discoveryStore
 */
import { create } from 'zustand'
import type { Message, DesignSheet, Stage } from '../types/discovery'

interface DiscoveryStoreState {
  sessionId: string | null
  messages: Message[]
  streamingContent: string
  stage: Stage | string
  chips: string[]
  sheet: Partial<DesignSheet> & { confidence_score: number }
  isStreaming: boolean

  setSessionId: (id: string | null) => void
  addMessage: (message: Message) => void
  setMessages: (messages: Message[]) => void
  setStreamingContent: (content: string) => void
  appendStreamingContent: (token: string) => void
  finalizeAssistantMessage: () => void
  setStage: (stage: Stage | string) => void
  setChips: (chips: string[]) => void
  updateSheet: (data: Partial<DesignSheet>) => void
  setIsStreaming: (streaming: boolean) => void
  reset: () => void
}

const initialState = {
  sessionId: null,
  messages: [],
  streamingContent: '',
  stage: 'greeting' as Stage | string,
  chips: [],
  sheet: { confidence_score: 0 },
  isStreaming: false,
}

export const useDiscoveryStore = create<DiscoveryStoreState>()((set, get) => ({
  ...initialState,

  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setMessages: (messages) => set({ messages }),
  setStreamingContent: (content) => set({ streamingContent: content }),
  appendStreamingContent: (token) => set((state) => ({ streamingContent: state.streamingContent + token })),

  finalizeAssistantMessage: () => {
    const { streamingContent } = get()
    if (streamingContent) {
      set((state) => ({
        messages: [...state.messages, { role: 'assistant', content: streamingContent }],
        streamingContent: '',
      }))
    }
  },

  setStage: (stage) => set({ stage }),
  setChips: (chips) => set({ chips }),
  updateSheet: (data) => set((state) => ({ sheet: { ...state.sheet, ...data } })),
  setIsStreaming: (streaming) => set({ isStreaming: streaming }),
  reset: () => set(initialState),
}))

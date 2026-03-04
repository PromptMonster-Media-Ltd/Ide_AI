/**
 * uiStore — Sidebar state, flow mode toggle, active page tracking.
 * @module stores/uiStore
 */
import { create } from 'zustand'

interface UIStoreState {
  sidebarExpanded: boolean
  flowMode: boolean
  activePage: string
  toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>

  toggleSidebar: () => void
  setSidebarExpanded: (expanded: boolean) => void
  setFlowMode: (enabled: boolean) => void
  setActivePage: (page: string) => void
  addToast: (message: string, type?: 'success' | 'error' | 'info') => void
  removeToast: (id: string) => void
}

export const useUIStore = create<UIStoreState>()((set) => ({
  sidebarExpanded: false,
  flowMode: false,
  activePage: 'home',
  toasts: [],

  toggleSidebar: () => set((state) => ({ sidebarExpanded: !state.sidebarExpanded })),
  setSidebarExpanded: (expanded) => set({ sidebarExpanded: expanded }),
  setFlowMode: (enabled) => set({ flowMode: enabled }),
  setActivePage: (page) => set({ activePage: page }),

  addToast: (message, type = 'info') => {
    const id = crypto.randomUUID()
    set((state) => ({ toasts: [...state.toasts, { id, message, type }] }))
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
    }, 4000)
  },

  removeToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}))

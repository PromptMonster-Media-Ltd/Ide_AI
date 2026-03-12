/**
 * authStore — Zustand store for authenticated user state.
 * Replaces ad-hoc localStorage.token + /auth/me calls with a single source of truth.
 * @module stores/authStore
 */
import { create } from 'zustand'
import apiClient from '../lib/apiClient'

export interface AuthUser {
  id: string
  email: string
  name: string | null
  display_name: string | null
  avatar_url: string | null
  oauth_provider: string | null
  email_verified: boolean
  account_type: string
  bio: string | null
  preferences: Record<string, unknown> | null
  created_at: string
}

interface AuthState {
  user: AuthUser | null
  loading: boolean
  /** Fetch /auth/me and populate user. Returns the user or null. */
  fetchUser: () => Promise<AuthUser | null>
  /** Update local user state (after PATCH /auth/me or avatar upload). */
  setUser: (user: AuthUser) => void
  /** Clear user + token. */
  logout: () => void
  /** Get initials for avatar fallback (first letter of name or email). */
  initials: () => string
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  loading: false,

  fetchUser: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      set({ user: null, loading: false })
      return null
    }
    set({ loading: true })
    try {
      const { data } = await apiClient.get('/auth/me')
      set({ user: data, loading: false })
      return data
    } catch {
      localStorage.removeItem('token')
      set({ user: null, loading: false })
      return null
    }
  },

  setUser: (user) => set({ user }),

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null })
    window.location.href = '/'
  },

  initials: () => {
    const u = get().user
    if (!u) return '?'
    const source = u.display_name || u.name || u.email
    return source.charAt(0).toUpperCase()
  },
}))

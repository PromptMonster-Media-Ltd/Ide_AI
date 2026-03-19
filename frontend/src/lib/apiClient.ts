/**
 * apiClient — Axios instance with base URL and Clerk auth interceptor.
 * Uses Clerk's session token instead of localStorage JWT.
 * @module lib/apiClient
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
})

/**
 * Clerk instance reference — set once from App.tsx via useClerk().
 * Used to get session tokens for API requests.
 */
let clerkInstance: { session: { getToken: () => Promise<string | null> } | null } | null = null

export function setClerkInstance(clerk: unknown) {
  clerkInstance = clerk as typeof clerkInstance
}

apiClient.interceptors.request.use(async (config) => {
  try {
    const token = await clerkInstance?.session?.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch {
    // Session not available — request will be sent without auth
  }
  return config
})

/**
 * Get the current Clerk session token for use in raw fetch calls (e.g. SSE).
 * Returns null if no session is available.
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    return (await clerkInstance?.session?.getToken()) ?? null
  } catch {
    return null
  }
}

export default apiClient

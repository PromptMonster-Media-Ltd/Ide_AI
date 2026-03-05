/**
 * extractError — Extracts a human-readable error message from an Axios error.
 * Handles FastAPI string details, Pydantic 422 validation arrays, and generic 500s.
 * @module lib/extractError
 */

interface ValidationItem {
  msg?: string
  loc?: (string | number)[]
}

export function extractError(err: unknown, fallback: string): string {
  const resp = (err as { response?: { data?: { detail?: unknown }; status?: number } })?.response
  if (!resp) return fallback

  const detail = resp.data?.detail

  // FastAPI string detail (e.g. "Email already registered")
  if (typeof detail === 'string') return detail

  // Pydantic 422 validation errors (detail is an array)
  if (Array.isArray(detail) && detail.length > 0) {
    return (detail as ValidationItem[])
      .map((d) => d.msg || 'Validation error')
      .join('. ')
  }

  // 500 Internal Server Error with no detail
  if (resp.status && resp.status >= 500) return 'Server error. Please try again later.'

  return fallback
}

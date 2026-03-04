/**
 * sseClient — EventSource factory for SSE connections.
 * @module lib/sseClient
 */

export function createSSEConnection(url: string, token?: string): EventSource {
  const fullUrl = token ? `${url}?token=${token}` : url
  return new EventSource(fullUrl)
}

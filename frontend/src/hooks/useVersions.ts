/**
 * useVersions — Version history fetch and snapshot restore.
 * @module hooks/useVersions
 */
import { useState, useCallback, useEffect } from 'react'
import apiClient from '../lib/apiClient'

interface Version {
  id: string
  project_id: string
  snapshot: Record<string, unknown>
  label: string | null
  created_at: string
}

export function useVersions(projectId: string | undefined) {
  const [versions, setVersions] = useState<Version[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchVersions = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get(`/versions/${projectId}`)
      setVersions(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch versions')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  const createSnapshot = useCallback(async (label?: string) => {
    if (!projectId) return
    try {
      const { data } = await apiClient.post(`/versions/${projectId}`, { label })
      setVersions((prev) => [data, ...prev])
      return data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create snapshot')
    }
  }, [projectId])

  useEffect(() => {
    fetchVersions()
  }, [fetchVersions])

  return { versions, loading, error, fetchVersions, createSnapshot }
}

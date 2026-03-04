/**
 * useExport — Export triggering, format selection, and file download.
 * @module hooks/useExport
 */
import { useState, useCallback } from 'react'
import apiClient from '../lib/apiClient'
import { downloadBlob, formatFilename } from '../lib/exportUtils'

type ExportFormat = 'md' | 'txt' | 'pdf' | 'docx' | 'zip'

const MIME_TYPES: Record<ExportFormat, string> = {
  md: 'text/markdown',
  txt: 'text/plain',
  pdf: 'application/pdf',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  zip: 'application/zip',
}

export function useExport(projectId: string | undefined) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeFormat, setActiveFormat] = useState<ExportFormat | null>(null)

  const exportProject = useCallback(async (format: ExportFormat) => {
    if (!projectId || loading) return
    setLoading(true)
    setActiveFormat(format)
    setError(null)

    try {
      const { data } = await apiClient.get(`/exports/${projectId}`, {
        params: { format },
        responseType: format === 'md' || format === 'txt' ? 'text' : 'blob',
      })

      if (format === 'md' || format === 'txt') {
        const blob = new Blob([data], { type: MIME_TYPES[format] })
        downloadBlob(blob, formatFilename(projectId, format))
      } else {
        downloadBlob(data, formatFilename(projectId, format))
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to export as ${format}`)
    } finally {
      setLoading(false)
      setActiveFormat(null)
    }
  }, [projectId, loading])

  return { exportProject, loading, activeFormat, error }
}

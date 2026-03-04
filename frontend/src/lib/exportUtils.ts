/**
 * exportUtils — Utility functions for file export and download.
 * @module lib/exportUtils
 */

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function formatFilename(projectName: string, format: string): string {
  const slug = projectName.toLowerCase().replace(/\s+/g, '-')
  const date = new Date().toISOString().split('T')[0]
  return `${slug}-design-kit-${date}.${format}`
}

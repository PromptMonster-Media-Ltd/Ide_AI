/**
 * Exports — Export format selector and download page.
 * @module pages/Exports
 */
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { downloadBlob, formatFilename } from '../lib/exportUtils'

const FORMATS = [
  { id: 'md', label: 'Markdown', icon: '\u{1F4DD}', desc: 'Clean markdown document' },
  { id: 'txt', label: 'Plain Text', icon: '\u{1F4C4}', desc: 'Simple text format' },
  { id: 'pdf', label: 'PDF', icon: '\u{1F4D5}', desc: 'Professional PDF document' },
  { id: 'docx', label: 'Word', icon: '\u{1F4D8}', desc: 'Microsoft Word format' },
  { id: 'zip', label: 'ZIP Bundle', icon: '\u{1F4E6}', desc: 'All formats in one download' },
]

export function Exports() {
  const { projectId } = useParams<{ projectId: string }>()
  const [selectedFormat, setSelectedFormat] = useState('md')
  const [downloading, setDownloading] = useState(false)

  const handleExport = async () => {
    if (!projectId) return
    setDownloading(true)
    try {
      const response = await apiClient.get(`/projects/${projectId}/export`, {
        params: { format: selectedFormat },
        responseType: 'blob',
      })
      const filename = formatFilename('design-kit', selectedFormat)
      downloadBlob(response.data, filename)
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setDownloading(false)
    }
  }

  const handleSnapshot = async () => {
    if (!projectId) return
    try {
      await apiClient.post(`/projects/${projectId}/versions/auto`)
    } catch (err) {
      console.error('Snapshot failed:', err)
    }
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar projectId={projectId} />
      <div className="ml-[232px] flex-1 flex flex-col h-screen">
        <TopBar title="Export Design Kit" subtitle="Download your project artifacts">
          <Button variant="ghost" onClick={handleSnapshot}>Save Snapshot</Button>
        </TopBar>

        <div className="flex-1 p-6 flex flex-col items-center justify-center">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8 w-full max-w-3xl">
            {FORMATS.map(fmt => (
              <button
                key={fmt.id}
                onClick={() => setSelectedFormat(fmt.id)}
                className="text-left"
              >
                <Card className={`transition-all cursor-pointer ${
                  selectedFormat === fmt.id ? 'border-accent shadow-[0_0_20px_rgba(0,229,255,0.1)]' : 'hover:border-white/15'
                }`}>
                  <div className="text-2xl mb-2">{fmt.icon}</div>
                  <h3 className="text-sm font-semibold text-white">{fmt.label}</h3>
                  <p className="text-xs text-text-muted mt-1">{fmt.desc}</p>
                </Card>
              </button>
            ))}
          </div>

          <Button size="lg" onClick={handleExport} disabled={downloading}>
            {downloading ? 'Downloading...' : `Download ${FORMATS.find(f => f.id === selectedFormat)?.label || selectedFormat}`}
          </Button>
        </div>
      </div>
    </div>
  )
}

/**
 * Library — Project library with .ideai file export/import and snapshot version management.
 * @module pages/Library
 */
import { useEffect, useRef, useState } from 'react'
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { downloadBlob } from '../lib/exportUtils'

interface LibraryProject {
  id: string
  name: string
  description: string | null
  platform: string
  audience: string
  complexity: string
  tone: string
  accent_color: string
  created_at: string
  updated_at: string
  snapshot_count: number
}

interface Snapshot {
  id: string
  project_id: string
  name: string
  description: string | null
  version: number
  created_at: string
}

export function Library() {
  const [projects, setProjects] = useState<LibraryProject[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])
  const [snapshotsLoading, setSnapshotsLoading] = useState(false)
  const [exporting, setExporting] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const [restoring, setRestoring] = useState<string | null>(null)

  // Snapshot creation form
  const [showSnapshotForm, setShowSnapshotForm] = useState(false)
  const [snapshotName, setSnapshotName] = useState('')
  const [snapshotDesc, setSnapshotDesc] = useState('')
  const [creatingSnapshot, setCreatingSnapshot] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch projects on mount
  useEffect(() => {
    fetchProjects()
  }, [])

  // Fetch snapshots when a project is selected
  useEffect(() => {
    if (selectedProjectId) {
      fetchSnapshots(selectedProjectId)
    } else {
      setSnapshots([])
    }
  }, [selectedProjectId])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get('/library/projects')
      setProjects(data)
    } catch (err) {
      console.error('Failed to fetch library projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSnapshots = async (projectId: string) => {
    setSnapshotsLoading(true)
    try {
      const { data } = await apiClient.get(`/library/${projectId}/snapshots`)
      setSnapshots(data)
    } catch (err) {
      console.error('Failed to fetch snapshots:', err)
    } finally {
      setSnapshotsLoading(false)
    }
  }

  const handleExport = async (projectId: string, projectName: string) => {
    setExporting(projectId)
    try {
      const response = await apiClient.post(`/library/${projectId}/export`, null, {
        responseType: 'blob',
      })
      const slug = projectName.toLowerCase().replace(/\s+/g, '-').slice(0, 30)
      downloadBlob(response.data, `${slug}.ideai`)
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setExporting(null)
    }
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      await apiClient.post('/library/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await fetchProjects()
    } catch (err) {
      console.error('Import failed:', err)
    } finally {
      setImporting(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleCreateSnapshot = async () => {
    if (!selectedProjectId || !snapshotName.trim()) return
    setCreatingSnapshot(true)
    try {
      await apiClient.post(`/library/${selectedProjectId}/snapshots`, {
        name: snapshotName.trim(),
        description: snapshotDesc.trim() || null,
      })
      setSnapshotName('')
      setSnapshotDesc('')
      setShowSnapshotForm(false)
      await fetchSnapshots(selectedProjectId)
      await fetchProjects()
    } catch (err) {
      console.error('Snapshot creation failed:', err)
    } finally {
      setCreatingSnapshot(false)
    }
  }

  const handleRestore = async (snapshotId: string) => {
    setRestoring(snapshotId)
    try {
      await apiClient.post(`/library/snapshots/${snapshotId}/restore`)
      await fetchProjects()
    } catch (err) {
      console.error('Restore failed:', err)
    } finally {
      setRestoring(null)
    }
  }

  const selectedProject = projects.find((p) => p.id === selectedProjectId)

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatDateTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <div className="ml-0 md:ml-[232px] flex-1 flex flex-col h-screen">
        <TopBar title="Library" subtitle="Manage projects, snapshots, and .ideai files">
          <input
            ref={fileInputRef}
            type="file"
            accept=".ideai"
            onChange={handleImport}
            className="hidden"
          />
          <Button
            variant="secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
          >
            {importing ? 'Importing...' : 'Import .ideai'}
          </Button>
        </TopBar>

        <div className="flex-1 p-4 md:p-6 overflow-y-auto pb-20 md:pb-6">
          <div className="max-w-5xl mx-auto">
            {/* --- Project List --- */}
            <h2 className="text-lg font-semibold text-white mb-1">Your Projects</h2>
            <p className="text-sm text-text-muted mb-5">
              Select a project to manage snapshots, or export as a .ideai file.
            </p>

            {loading ? (
              <div className="text-center py-12 text-text-muted text-sm">Loading projects...</div>
            ) : projects.length === 0 ? (
              <Card className="text-center py-12">
                <p className="text-text-muted text-sm mb-3">No projects yet. Create one from the Home page.</p>
                <p className="text-text-muted text-xs">Or import a .ideai file using the button above.</p>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 mb-8">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => setSelectedProjectId(
                      selectedProjectId === project.id ? null : project.id
                    )}
                    className="text-left"
                  >
                    <Card
                      className={`transition-all cursor-pointer h-full ${
                        selectedProjectId === project.id
                          ? 'border-accent shadow-[0_0_20px_rgba(0,229,255,0.1)]'
                          : 'hover:border-white/15'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="text-sm font-semibold text-white truncate flex-1">
                          {project.name}
                        </h3>
                        <span
                          className="shrink-0 w-3 h-3 rounded-full mt-0.5"
                          style={{ backgroundColor: project.accent_color }}
                        />
                      </div>
                      {project.description && (
                        <p className="text-xs text-text-muted mb-3 line-clamp-2">
                          {project.description}
                        </p>
                      )}
                      <div className="flex items-center gap-3 text-[10px] text-text-muted">
                        <span className="bg-white/5 px-2 py-0.5 rounded">{project.platform}</span>
                        <span>{project.snapshot_count} snapshot{project.snapshot_count !== 1 ? 's' : ''}</span>
                        <span className="ml-auto">{formatDate(project.updated_at)}</span>
                      </div>
                    </Card>
                  </button>
                ))}
              </div>
            )}

            {/* --- Selected Project Actions --- */}
            {selectedProject && (
              <>
                <div className="border-t border-border mb-8" />

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-white mb-1">
                      {selectedProject.name}
                    </h2>
                    <p className="text-sm text-text-muted">
                      Manage snapshots and exports for this project.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleExport(selectedProject.id, selectedProject.name)}
                      disabled={exporting === selectedProject.id}
                    >
                      {exporting === selectedProject.id ? 'Exporting...' : 'Export .ideai'}
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => setShowSnapshotForm(!showSnapshotForm)}
                    >
                      Create Snapshot
                    </Button>
                  </div>
                </div>

                {/* --- Create Snapshot Form --- */}
                {showSnapshotForm && (
                  <Card className="mb-6">
                    <h3 className="text-sm font-semibold text-white mb-3">New Snapshot</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs font-medium text-text-muted mb-1">
                          Name *
                        </label>
                        <input
                          type="text"
                          value={snapshotName}
                          onChange={(e) => setSnapshotName(e.target.value)}
                          placeholder="e.g., v1.0 - MVP scope finalized"
                          className="w-full bg-white/5 border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                          maxLength={200}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-text-muted mb-1">
                          Description (optional)
                        </label>
                        <textarea
                          value={snapshotDesc}
                          onChange={(e) => setSnapshotDesc(e.target.value)}
                          placeholder="Brief notes about what changed..."
                          className="w-full bg-white/5 border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors resize-none h-20"
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          onClick={handleCreateSnapshot}
                          disabled={!snapshotName.trim() || creatingSnapshot}
                        >
                          {creatingSnapshot ? 'Saving...' : 'Save Snapshot'}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setShowSnapshotForm(false)
                            setSnapshotName('')
                            setSnapshotDesc('')
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </Card>
                )}

                {/* --- Snapshots List --- */}
                <h3 className="text-sm font-semibold text-white mb-3">Version History</h3>

                {snapshotsLoading ? (
                  <div className="text-center py-8 text-text-muted text-sm">Loading snapshots...</div>
                ) : snapshots.length === 0 ? (
                  <Card className="text-center py-8">
                    <p className="text-text-muted text-sm">
                      No snapshots yet. Create one to save the current project state.
                    </p>
                  </Card>
                ) : (
                  <div className="space-y-2">
                    {snapshots.map((snap) => (
                      <Card key={snap.id} className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-mono text-accent bg-accent/10 px-1.5 py-0.5 rounded">
                              v{snap.version}
                            </span>
                            <h4 className="text-sm font-medium text-white truncate">
                              {snap.name}
                            </h4>
                          </div>
                          {snap.description && (
                            <p className="text-xs text-text-muted truncate">{snap.description}</p>
                          )}
                          <p className="text-[10px] text-text-muted mt-1">
                            {formatDateTime(snap.created_at)}
                          </p>
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleRestore(snap.id)}
                          disabled={restoring === snap.id}
                        >
                          {restoring === snap.id ? 'Restoring...' : 'Restore'}
                        </Button>
                      </Card>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

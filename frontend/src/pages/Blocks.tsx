/**
 * Blocks — Drag-and-drop feature blocks board with scope slider.
 * @module pages/Blocks
 */
import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import apiClient from '../lib/apiClient'

interface Block {
  id: string
  name: string
  description: string
  category: string
  priority: 'mvp' | 'v2'
  effort: 'S' | 'M' | 'L'
  order: number
  is_mvp: boolean
}

type Scope = 'lean' | 'balanced' | 'full'

export function Blocks() {
  const { projectId } = useParams<{ projectId: string }>()
  const [blocks, setBlocks] = useState<Block[]>([])
  const [scope, setScope] = useState<Scope>('balanced')
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  const fetchBlocks = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const { data } = await apiClient.get(`/projects/${projectId}/blocks`)
      setBlocks(data)
    } catch (err) {
      console.error('Failed to fetch blocks:', err)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { fetchBlocks() }, [fetchBlocks])

  const generateBlocks = async () => {
    if (!projectId) return
    setGenerating(true)
    try {
      const { data } = await apiClient.post(`/projects/${projectId}/blocks/generate`)
      setBlocks(data)
    } catch (err) {
      console.error('Failed to generate blocks:', err)
    } finally {
      setGenerating(false)
    }
  }

  const togglePriority = async (block: Block) => {
    const newPriority = block.priority === 'mvp' ? 'v2' : 'mvp'
    try {
      await apiClient.patch(`/projects/${projectId}/blocks/${block.id}`, {
        priority: newPriority,
        is_mvp: newPriority === 'mvp',
      })
      setBlocks(prev => prev.map(b => b.id === block.id ? { ...b, priority: newPriority, is_mvp: newPriority === 'mvp' } : b))
    } catch (err) {
      console.error('Failed to update block:', err)
    }
  }

  const deleteBlock = async (blockId: string) => {
    try {
      await apiClient.delete(`/projects/${projectId}/blocks/${blockId}`)
      setBlocks(prev => prev.filter(b => b.id !== blockId))
    } catch (err) {
      console.error('Failed to delete block:', err)
    }
  }

  const filteredBlocks = blocks.filter(b => {
    if (scope === 'lean') return b.priority === 'mvp' && b.effort !== 'L'
    if (scope === 'balanced') return b.priority === 'mvp'
    return true // full
  })

  const effortVariant = (e: string) => e === 'S' ? 'success' : e === 'M' ? 'warning' : 'default'

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar projectId={projectId} />
      <div className="ml-[232px] flex-1 flex flex-col h-screen">
        <TopBar title="Design Blocks" subtitle={`${filteredBlocks.length} blocks shown`}>
          <Button variant="secondary" onClick={generateBlocks} disabled={generating}>
            {generating ? 'Generating...' : 'AI Generate'}
          </Button>
        </TopBar>

        <div className="p-6 flex-1 overflow-y-auto">
          {/* Scope Slider */}
          <div className="flex items-center gap-4 mb-6">
            <span className="text-xs text-text-muted font-medium">Scope:</span>
            {(['lean', 'balanced', 'full'] as Scope[]).map(s => (
              <button
                key={s}
                onClick={() => setScope(s)}
                className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  scope === s ? 'bg-accent text-background' : 'bg-white/5 text-text-muted hover:text-white border border-border'
                }`}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>

          {/* Blocks Grid */}
          {loading ? (
            <div className="text-text-muted text-sm">Loading blocks...</div>
          ) : filteredBlocks.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-text-muted mb-4">No blocks yet. Generate them from your design sheet.</p>
              <Button onClick={generateBlocks} disabled={generating}>Generate Blocks</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredBlocks.map(block => (
                <Card key={block.id} className="flex flex-col gap-3">
                  <div className="flex items-start justify-between">
                    <h3 className="text-sm font-semibold text-white">{block.name}</h3>
                    <button onClick={() => deleteBlock(block.id)} className="text-text-muted hover:text-red-400 text-xs">&#x2715;</button>
                  </div>
                  <p className="text-xs text-text-muted leading-relaxed">{block.description}</p>
                  <div className="flex items-center gap-2 mt-auto">
                    <button onClick={() => togglePriority(block)}>
                      <Badge variant={block.priority === 'mvp' ? 'accent' : 'default'}>
                        {block.priority.toUpperCase()}
                      </Badge>
                    </button>
                    <Badge variant={effortVariant(block.effort)}>{block.effort}</Badge>
                    <Badge>{block.category}</Badge>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

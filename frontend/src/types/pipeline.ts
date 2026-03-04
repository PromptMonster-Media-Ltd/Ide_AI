/**
 * pipeline.ts — Pipeline node and layer type definitions.
 * @module types/pipeline
 */

export const Layer = {
  Frontend: 'frontend',
  Backend: 'backend',
  Database: 'database',
  Auth: 'auth',
  Hosting: 'hosting',
  AI: 'ai',
} as const

export type Layer = (typeof Layer)[keyof typeof Layer]

export interface PipelineNode {
  id: string
  project_id: string
  layer: Layer
  selected_tool: string
  config?: Record<string, unknown>
  created_at: string
  updated_at: string
}

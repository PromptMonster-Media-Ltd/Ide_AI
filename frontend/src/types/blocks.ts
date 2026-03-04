/**
 * blocks.ts — Feature block type definitions.
 * @module types/blocks
 */

export const Priority = {
  MVP: 'mvp',
  V2: 'v2',
} as const

export type Priority = (typeof Priority)[keyof typeof Priority]

export const Effort = {
  Small: 'S',
  Medium: 'M',
  Large: 'L',
} as const

export type Effort = (typeof Effort)[keyof typeof Effort]

export interface Block {
  id: string
  project_id: string
  name: string
  description: string
  category: string
  priority: Priority
  effort: Effort
  order: number
  is_mvp: boolean
  created_at: string
  updated_at: string
}

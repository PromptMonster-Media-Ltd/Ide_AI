/**
 * project.ts — Project-related type definitions.
 * @module types/project
 */

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  platform: string
  audience: string
  complexity: string
  tone: string
  accent_color: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  platform: string
  audience: string
  complexity: string
  tone: string
  description?: string
  accent_color?: string
}

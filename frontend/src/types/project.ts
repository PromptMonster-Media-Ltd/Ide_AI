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
  pathway_id: string
  ai_partner_style: string
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
  pathway_id?: string
  ai_partner_style?: string
}

/** AI Partner metadata returned by GET /meta/partner-styles */
export interface PartnerStyleMeta {
  id: string
  name: string
  icon: string
  color: string
  description: string
  best_for: string[]
  traits: string[]
}

/**
 * discovery.ts — Discovery session and design sheet type definitions.
 * @module types/discovery
 */

export const Stage = {
  Greeting: 'greeting',
  Problem: 'problem',
  Audience: 'audience',
  Features: 'features',
  Constraints: 'constraints',
  Confirm: 'confirm',
} as const

export type Stage = (typeof Stage)[keyof typeof Stage]

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface Session {
  id: string
  project_id: string
  status: 'active' | 'complete'
  stage: Stage
  ai_partner_style: string
  messages: Message[]
  created_at: string
}

export interface DesignSheet {
  id: string
  project_id: string
  problem: string
  audience: string
  mvp: string
  features: Record<string, unknown>[]
  tone: string
  platform: string
  tech_constraints?: string
  success_metric?: string
  confidence_score: number
  created_at: string
  updated_at: string
}

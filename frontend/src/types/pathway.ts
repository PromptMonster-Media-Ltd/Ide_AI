/**
 * pathway.ts — Concept Pathway type definitions.
 * Mirrors the PathwayConfig dataclass from the backend.
 * @module types/pathway
 */

export interface StageConfig {
  id: string
  label: string
  icon: string
}

export interface SheetFieldConfig {
  key: string
  label: string
  field_type: 'text' | 'textarea' | 'list' | 'tags'
}

export interface ModuleConfig {
  id: string
  label: string
  icon: string
  route_suffix: string
  component_key: string
  order: number
}

export interface BlockCategoryConfig {
  id: string
  label: string
  color: string
}

export interface CreationPreset {
  id: string
  name: string
  icon: string
  defaults: Record<string, string>
}

export interface CreationField {
  id: string
  label: string
  options: string[]
}

export interface PathwayDefinition {
  id: string
  name: string
  description: string
  icon: string
  color: string
  stages: StageConfig[]
  sheet_fields: SheetFieldConfig[]
  modules: ModuleConfig[]
  block_categories: BlockCategoryConfig[]
  block_priorities: string[]
  block_efforts: string[]
  creation_presets: CreationPreset[]
  creation_fields: CreationField[]
  schedule_label: string
  schedule_icon: string
}

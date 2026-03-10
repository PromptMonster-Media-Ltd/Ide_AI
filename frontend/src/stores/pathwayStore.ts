/**
 * pathwayStore.ts — Zustand store for Concept Pathway state.
 * Fetches pathway definitions from the API and resolves the active pathway
 * for the current project.
 * @module stores/pathwayStore
 */
import { create } from 'zustand'
import apiClient from '../lib/apiClient'
import type { PathwayDefinition } from '../types/pathway'

interface PathwayStoreState {
  /** All available pathway definitions from the backend. */
  pathways: PathwayDefinition[]
  /** The pathway active for the current project (set via setActiveByProjectId or setActive). */
  active: PathwayDefinition | null
  /** True while the initial fetch is in-flight. */
  loading: boolean

  /** Fetch all pathway definitions from /api/v1/pathways. */
  fetchPathways: () => Promise<void>

  /** Set the active pathway by its id. Falls back to software_product. */
  setActive: (pathwayId: string) => void

  /** Convenience: look up a project's pathway_id and activate it. */
  setActiveByProject: (project: { pathway_id?: string }) => void

  /** Find a pathway by id (returns undefined if not found). */
  getPathway: (id: string) => PathwayDefinition | undefined
}

export const usePathwayStore = create<PathwayStoreState>()((set, get) => ({
  pathways: [],
  active: null,
  loading: false,

  fetchPathways: async () => {
    // Avoid duplicate fetches
    if (get().pathways.length > 0 || get().loading) return
    set({ loading: true })
    try {
      const { data } = await apiClient.get<PathwayDefinition[]>('/pathways')
      const fallback = data.find(p => p.id === 'software_product') ?? data[0] ?? null
      set({ pathways: data, active: get().active ?? fallback, loading: false })
    } catch (err) {
      console.error('[pathwayStore] Failed to fetch pathways:', err)
      set({ loading: false })
    }
  },

  setActive: (pathwayId: string) => {
    const found = get().pathways.find(p => p.id === pathwayId)
    if (found) {
      set({ active: found })
    }
  },

  setActiveByProject: (project: { pathway_id?: string }) => {
    const id = project.pathway_id ?? 'software_product'
    get().setActive(id)
  },

  getPathway: (id: string) => {
    return get().pathways.find(p => p.id === id)
  },
}))

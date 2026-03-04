/**
 * projectStore — Active project, project list, and CRUD state.
 * @module stores/projectStore
 */
import { create } from 'zustand'
import apiClient from '../lib/apiClient'
import type { Project, ProjectCreate } from '../types/project'

interface ProjectStoreState {
  projects: Project[]
  activeProject: Project | null
  loading: boolean
  error: string | null

  fetchProjects: () => Promise<void>
  fetchProject: (id: string) => Promise<void>
  createProject: (data: ProjectCreate) => Promise<Project>
  updateProject: (id: string, data: Partial<ProjectCreate>) => Promise<void>
  deleteProject: (id: string) => Promise<void>
  setActiveProject: (project: Project | null) => void
  clearError: () => void
}

export const useProjectStore = create<ProjectStoreState>()((set) => ({
  projects: [],
  activeProject: null,
  loading: false,
  error: null,

  fetchProjects: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.get('/projects')
      set({ projects: data, loading: false })
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to fetch projects', loading: false })
    }
  },

  fetchProject: async (id: string) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.get(`/projects/${id}`)
      set({ activeProject: data, loading: false })
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to fetch project', loading: false })
    }
  },

  createProject: async (payload: ProjectCreate) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.post('/projects', payload)
      set((state) => ({ projects: [data, ...state.projects], activeProject: data, loading: false }))
      return data
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to create project', loading: false })
      throw err
    }
  },

  updateProject: async (id: string, payload: Partial<ProjectCreate>) => {
    set({ loading: true, error: null })
    try {
      const { data } = await apiClient.patch(`/projects/${id}`, payload)
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? data : p)),
        activeProject: state.activeProject?.id === id ? data : state.activeProject,
        loading: false,
      }))
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to update project', loading: false })
    }
  },

  deleteProject: async (id: string) => {
    set({ loading: true, error: null })
    try {
      await apiClient.delete(`/projects/${id}`)
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        activeProject: state.activeProject?.id === id ? null : state.activeProject,
        loading: false,
      }))
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to delete project', loading: false })
    }
  },

  setActiveProject: (project) => set({ activeProject: project }),
  clearError: () => set({ error: null }),
}))

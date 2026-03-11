/**
 * tutorialStore.ts — Zustand store for the Ambient Guidance tutorial system.
 * Persists seen/dismissed state to localStorage so hints only show once.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface TutorialState {
  seenInterludes: Record<string, boolean>
  dismissedBeacons: string[]
  dismissedWhispers: string[]

  markInterludeSeen: (phase: string) => void
  dismissBeacon: (id: string) => void
  dismissWhisper: (id: string) => void
  shouldShowBeacon: (id: string) => boolean
  shouldShowWhisper: (id: string) => boolean
  resetTutorial: () => void
}

const INITIAL_STATE = {
  seenInterludes: {} as Record<string, boolean>,
  dismissedBeacons: [] as string[],
  dismissedWhispers: [] as string[],
}

export const useTutorialStore = create<TutorialState>()(
  persist(
    (set, get) => ({
      ...INITIAL_STATE,

      markInterludeSeen: (phase) =>
        set((s) => ({
          seenInterludes: { ...s.seenInterludes, [phase]: true },
        })),

      dismissBeacon: (id) =>
        set((s) => ({
          dismissedBeacons: s.dismissedBeacons.includes(id)
            ? s.dismissedBeacons
            : [...s.dismissedBeacons, id],
        })),

      dismissWhisper: (id) =>
        set((s) => ({
          dismissedWhispers: s.dismissedWhispers.includes(id)
            ? s.dismissedWhispers
            : [...s.dismissedWhispers, id],
        })),

      shouldShowBeacon: (id) => !get().dismissedBeacons.includes(id),

      shouldShowWhisper: (id) => !get().dismissedWhispers.includes(id),

      resetTutorial: () => set(INITIAL_STATE),
    }),
    { name: 'ideaforge-tutorial' },
  ),
)

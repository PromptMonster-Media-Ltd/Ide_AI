/**
 * PulseBeacon — Pulsing cyan dot on key UI elements, dismissed on interaction.
 */
import type { ReactNode } from 'react'
import { useTutorialStore } from '../../stores/tutorialStore'

interface PulseBeaconProps {
  id: string
  children: ReactNode
  position?: 'top-right' | 'top-left' | 'bottom-right'
  className?: string
}

const POSITION_CLASSES: Record<string, string> = {
  'top-right': '-top-1 -right-1',
  'top-left': '-top-1 -left-1',
  'bottom-right': '-bottom-1 -right-1',
}

export function PulseBeacon({
  id,
  children,
  position = 'top-right',
  className = '',
}: PulseBeaconProps) {
  const show = useTutorialStore((s) => !s.dismissedBeacons.includes(id))
  const dismiss = useTutorialStore((s) => s.dismissBeacon)

  if (!show) return <>{children}</>

  const handleDismiss = () => dismiss(id)

  return (
    <div
      className={`relative ${className}`}
      onClick={handleDismiss}
      onPointerEnter={handleDismiss}
    >
      {children}
      <span
        className={`absolute ${POSITION_CLASSES[position]} w-3 h-3 rounded-full bg-accent/40 animate-beacon-pulse pointer-events-none z-10`}
      />
    </div>
  )
}

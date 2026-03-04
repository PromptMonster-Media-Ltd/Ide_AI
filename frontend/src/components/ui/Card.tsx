/**
 * Card — Glassmorphism card container.
 * @module components/ui/Card
 */

interface CardProps {
  children: React.ReactNode
  className?: string
  glow?: boolean
}

export function Card({ children, className = '', glow = false }: CardProps) {
  return (
    <div
      className={`rounded-[var(--radius-card)] border border-border bg-surface/60 backdrop-blur-md p-5 ${
        glow ? 'shadow-[0_0_30px_rgba(0,229,255,0.08)]' : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}

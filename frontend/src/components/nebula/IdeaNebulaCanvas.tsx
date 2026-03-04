/**
 * IdeaNebulaCanvas — Background canvas with pulsing animated nodes connected by lines.
 * @module components/nebula/IdeaNebulaCanvas
 */
import { motion } from 'framer-motion'

const NODES = [
  { x: 15, y: 25, delay: 0 },
  { x: 35, y: 15, delay: 0.5 },
  { x: 55, y: 30, delay: 1 },
  { x: 75, y: 20, delay: 0.3 },
  { x: 25, y: 60, delay: 0.8 },
  { x: 50, y: 55, delay: 1.2 },
  { x: 70, y: 65, delay: 0.6 },
  { x: 85, y: 45, delay: 0.9 },
]

const CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 6], [6, 7], [3, 7], [1, 5], [2, 6],
]

export function IdeaNebulaCanvas() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Connection lines */}
        {CONNECTIONS.map(([a, b], i) => (
          <motion.line
            key={`line-${i}`}
            x1={NODES[a].x}
            y1={NODES[a].y}
            x2={NODES[b].x}
            y2={NODES[b].y}
            stroke="rgba(0, 229, 255, 0.06)"
            strokeWidth="0.15"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: i * 0.15, ease: 'easeInOut' }}
          />
        ))}

        {/* Pulsing nodes */}
        {NODES.map((node, i) => (
          <motion.circle
            key={`node-${i}`}
            cx={node.x}
            cy={node.y}
            r="0.8"
            fill="rgba(0, 229, 255, 0.15)"
            initial={{ scale: 0, opacity: 0 }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3,
              delay: node.delay,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        ))}
      </svg>
    </div>
  )
}

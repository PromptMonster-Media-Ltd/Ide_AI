/**
 * ProtectedRoute — Redirects unauthenticated users to /sign-in using Clerk.
 * @module components/auth/ProtectedRoute
 */
import { type ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

interface Props {
  children: ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" replace />
  }

  return <>{children}</>
}

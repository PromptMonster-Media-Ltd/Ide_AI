/**
 * ProtectedRoute — Redirects unauthenticated users to /login.
 * Validates the stored JWT by calling /auth/me on mount.
 * @module components/auth/ProtectedRoute
 */
import { useEffect, useState, type ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import apiClient from '../../lib/apiClient'

interface Props {
  children: ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const [status, setStatus] = useState<'loading' | 'authenticated' | 'unauthenticated'>('loading')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setStatus('unauthenticated')
      return
    }

    apiClient
      .get('/auth/me')
      .then(() => setStatus('authenticated'))
      .catch(() => {
        localStorage.removeItem('token')
        setStatus('unauthenticated')
      })
  }, [])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

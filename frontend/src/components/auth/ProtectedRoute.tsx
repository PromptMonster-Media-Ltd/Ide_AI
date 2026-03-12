/**
 * ProtectedRoute — Redirects unauthenticated users to /login.
 * Validates the stored JWT by calling /auth/me on mount.
 * Redirects unverified email/password users to /verify-email.
 * @module components/auth/ProtectedRoute
 */
import { useEffect, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import apiClient from '../../lib/apiClient'

interface Props {
  children: ReactNode
}

/** Routes that unverified users can still access */
const VERIFICATION_EXEMPT = ['/verify-email', '/settings']

export function ProtectedRoute({ children }: Props) {
  const [status, setStatus] = useState<'loading' | 'authenticated' | 'unauthenticated' | 'unverified'>('loading')
  const location = useLocation()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setStatus('unauthenticated')
      return
    }

    apiClient
      .get('/auth/me')
      .then((res) => {
        const user = res.data
        // If email/password user and not verified, flag as unverified
        if (!user.email_verified && !user.oauth_provider) {
          setStatus('unverified')
        } else {
          setStatus('authenticated')
        }
      })
      .catch(() => {
        localStorage.removeItem('token')
        setStatus('unauthenticated')
      })
  }, [location.pathname])

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

  if (status === 'unverified' && !VERIFICATION_EXEMPT.includes(location.pathname)) {
    return <Navigate to="/verify-email" replace />
  }

  return <>{children}</>
}

/**
 * OAuthCallback — Handles OAuth provider redirects.
 * Extracts the authorization code from URL params and exchanges it for a JWT.
 * @module pages/OAuthCallback
 */
import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate, Link } from 'react-router-dom'
import apiClient from '../lib/apiClient'

export function OAuthCallback() {
  const { provider } = useParams<{ provider: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = searchParams.get('code')
    if (!code || !provider) {
      setError('Missing authorization code or provider.')
      return
    }

    const exchangeCode = async () => {
      try {
        const { data } = await apiClient.post(`/auth/${provider}/callback`, { code })
        if (data.access_token) {
          localStorage.setItem('token', data.access_token)
          navigate('/', { replace: true })
        } else {
          setError('Authentication failed. No token received.')
        }
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } }
        setError(axiosErr.response?.data?.detail || 'Authentication failed. Please try again.')
      }
    }

    exchangeCode()
  }, [provider, searchParams, navigate])

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="bg-surface border border-border rounded-2xl p-8 max-w-md w-full text-center">
          <div className="text-4xl mb-4">:(</div>
          <h1 className="text-lg font-semibold text-white mb-2">Authentication Failed</h1>
          <p className="text-sm text-text-muted mb-6">{error}</p>
          <Link
            to="/login"
            className="inline-block px-6 py-2.5 rounded-lg bg-accent text-black font-medium text-sm hover:bg-accent/90 transition-colors"
          >
            Back to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-text-muted">Signing you in...</p>
      </div>
    </div>
  )
}

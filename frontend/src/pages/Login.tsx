/**
 * Login — Email/password sign-in page with OAuth provider buttons.
 * @module pages/Login
 */
import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { extractError } from '../lib/extractError'

const OAUTH_PROVIDERS = [
  {
    key: 'google',
    label: 'Continue with Google',
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
      </svg>
    ),
  },
  {
    key: 'microsoft',
    label: 'Continue with Microsoft',
    icon: (
      <svg viewBox="0 0 23 23" className="w-4 h-4">
        <rect x="0" y="0" width="11" height="11" fill="#F25022" />
        <rect x="12" y="0" width="11" height="11" fill="#7FBA00" />
        <rect x="0" y="12" width="11" height="11" fill="#00A4EF" />
        <rect x="12" y="12" width="11" height="11" fill="#FFB900" />
      </svg>
    ),
  },
  {
    key: 'github',
    label: 'Continue with GitHub',
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4 fill-white">
        <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
      </svg>
    ),
  },
]

export function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [oauthLoading, setOauthLoading] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data } = await apiClient.post('/auth/login', { email, password })
      localStorage.setItem('token', data.access_token)
      navigate('/home')
    } catch (err: unknown) {
      setError(extractError(err, 'Login failed. Please check your credentials.'))
    } finally {
      setLoading(false)
    }
  }

  const handleOAuth = async (provider: string) => {
    setError('')
    setOauthLoading(provider)
    try {
      const { data } = await apiClient.get(`/auth/${provider}`)
      window.location.href = data.auth_url
    } catch (err: unknown) {
      setError(extractError(err, `${provider} login is not configured yet.`))
      setOauthLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <motion.div
        className="w-full max-w-sm"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Brand */}
        <div className="text-center mb-8">
          <img src="/logo.png" alt="Ide/AI" className="w-[160px] md:w-[200px] mx-auto mb-3" />
          <p className="text-text-muted text-sm">Sign in to your workspace</p>
        </div>

        <Card glow>
          {/* OAuth buttons */}
          <div className="space-y-2 mb-4">
            {OAUTH_PROVIDERS.map((provider) => (
              <button
                key={provider.key}
                onClick={() => handleOAuth(provider.key)}
                disabled={oauthLoading !== null || loading}
                className="w-full flex items-center justify-center gap-2.5 px-4 py-2.5 text-sm font-medium rounded-lg border border-border bg-white/5 text-white hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {provider.icon}
                <span>{oauthLoading === provider.key ? 'Redirecting...' : provider.label}</span>
              </button>
            ))}
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-[10px] text-text-muted uppercase tracking-wider">or</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="text-red-400 text-xs bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-xs text-text-muted font-medium mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs text-text-muted font-medium mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
                placeholder="••••••••"
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading || oauthLoading !== null}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>

            <div className="text-center">
              <Link to="/forgot-password" className="text-xs text-text-muted hover:text-accent transition-colors">
                Forgot your password?
              </Link>
            </div>
          </form>
        </Card>

        <p className="text-center text-text-muted text-xs mt-5">
          Don't have an account?{' '}
          <Link to="/register" className="text-accent hover:underline">
            Create one
          </Link>
        </p>
      </motion.div>
    </div>
  )
}

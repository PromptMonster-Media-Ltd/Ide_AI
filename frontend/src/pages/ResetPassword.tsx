/**
 * ResetPassword — Set a new password using a reset token from email.
 * @module pages/ResetPassword
 */
import { useState, type FormEvent } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { extractError } from '../lib/extractError'

export function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)

    try {
      await apiClient.post('/auth/reset-password', {
        token,
        new_password: password,
      })
      setSuccess(true)
      // Redirect to login after 3 seconds
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: unknown) {
      setError(extractError(err, 'Something went wrong. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <motion.div
          className="w-full max-w-sm"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-8">
            <img src="/logo.png" alt="Ide/AI" className="w-[160px] md:w-[200px] mx-auto mb-3" />
          </div>
          <Card glow>
            <div className="text-center py-4">
              <p className="text-red-400 text-sm mb-4">Invalid reset link. No token provided.</p>
              <Link to="/forgot-password" className="text-accent hover:underline text-sm">
                Request a new reset link
              </Link>
            </div>
          </Card>
        </motion.div>
      </div>
    )
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
          <p className="text-text-muted text-sm">Choose a new password</p>
        </div>

        <Card glow>
          {success ? (
            <div className="text-center py-4">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-green-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-white font-semibold text-lg mb-2">Password updated!</h2>
              <p className="text-text-muted text-sm">
                Redirecting you to sign in...
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="text-red-400 text-xs bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="password" className="block text-xs text-text-muted font-medium mb-1.5">
                  New Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="new-password"
                  autoFocus
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-xs text-text-muted font-medium mb-1.5">
                  Confirm New Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  required
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
                  placeholder="••••••••"
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Resetting...' : 'Reset Password'}
              </Button>
            </form>
          )}
        </Card>

        <p className="text-center text-text-muted text-xs mt-5">
          Remember your password?{' '}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  )
}

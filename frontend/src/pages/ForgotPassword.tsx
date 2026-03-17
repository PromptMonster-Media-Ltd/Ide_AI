/**
 * ForgotPassword — Request a password reset link via email.
 * @module pages/ForgotPassword
 */
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { extractError } from '../lib/extractError'

export function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await apiClient.post('/auth/forgot-password', { email })
      setSent(true)
    } catch (err: unknown) {
      setError(extractError(err, 'Something went wrong. Please try again.'))
    } finally {
      setLoading(false)
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
          <p className="text-text-muted text-sm">Reset your password</p>
        </div>

        <Card glow>
          {sent ? (
            <div className="text-center py-4">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-white font-semibold text-lg mb-2">Check your email</h2>
              <p className="text-text-muted text-sm mb-1">
                If an account exists for <span className="text-white">{email}</span>, we've sent a password reset link.
              </p>
              <p className="text-text-muted text-xs">
                The link expires in 15 minutes.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <p className="text-text-muted text-sm">
                Enter your email and we'll send you a link to reset your password.
              </p>

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

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Link'}
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

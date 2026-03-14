/**
 * VerifyEmail — 6-digit code input page for email verification.
 * Shown after registration for email/password users.
 *
 * Auto-submit is driven by a useEffect on `digits` state to avoid race
 * conditions with React 18 batching and mobile keyboard/autofill events.
 * @module pages/VerifyEmail
 */
import { useState, useRef, useEffect, useCallback, type KeyboardEvent, type ClipboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { extractError } from '../lib/extractError'

const CODE_LENGTH = 6
const EMPTY_CODE = Array<string>(CODE_LENGTH).fill('')

export function VerifyEmail() {
  const navigate = useNavigate()
  const [digits, setDigits] = useState<string[]>([...EMPTY_CODE])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const submittingRef = useRef(false) // guard against double-submit

  // Start with a 60s cooldown (code was just sent on register)
  useEffect(() => {
    setResendCooldown(60)
  }, [])

  // Countdown timer for resend cooldown
  useEffect(() => {
    if (resendCooldown <= 0) return
    const timer = setInterval(() => {
      setResendCooldown(prev => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(timer)
  }, [resendCooldown])

  // ── Submit handler ──
  const handleSubmit = useCallback(async (code?: string) => {
    const finalCode = code ?? digits.join('')
    if (finalCode.length !== CODE_LENGTH || /\D/.test(finalCode)) {
      setError('Please enter all 6 digits.')
      return
    }
    if (submittingRef.current) return
    submittingRef.current = true
    setLoading(true)
    setError('')
    try {
      await apiClient.post('/auth/verify-email', { code: finalCode })
      navigate('/home')
    } catch (err: unknown) {
      setError(extractError(err, 'Invalid or expired code. Please try again.'))
      setDigits([...EMPTY_CODE])
      inputRefs.current[0]?.focus()
    } finally {
      setLoading(false)
      submittingRef.current = false
    }
  }, [digits, navigate])

  // ── Auto-submit when all 6 digits are filled (driven by state, not events) ──
  useEffect(() => {
    if (loading || submittingRef.current) return
    const code = digits.join('')
    if (code.length === CODE_LENGTH && digits.every(d => /^\d$/.test(d))) {
      handleSubmit(code)
    }
  }, [digits]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Digit input handler ──
  const handleChange = (index: number, value: string) => {
    // Strip non-digits
    const cleaned = value.replace(/\D/g, '')
    if (cleaned.length === 0) {
      // User cleared the field
      const next = [...digits]
      next[index] = ''
      setDigits(next)
      setError('')
      return
    }

    // If the browser dumped the entire code into one field (mobile autofill),
    // distribute across all inputs
    if (cleaned.length > 1) {
      const chars = cleaned.slice(0, CODE_LENGTH).split('')
      const next = [...EMPTY_CODE]
      chars.forEach((ch, i) => { next[i] = ch })
      setDigits(next)
      setError('')
      const focusIdx = Math.min(chars.length, CODE_LENGTH - 1)
      inputRefs.current[focusIdx]?.focus()
      return
    }

    // Normal single-digit entry
    const next = [...digits]
    next[index] = cleaned
    setDigits(next)
    setError('')

    // Auto-advance to next input
    if (index < CODE_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      // Clear previous digit and move focus back
      const next = [...digits]
      next[index - 1] = ''
      setDigits(next)
      inputRefs.current[index - 1]?.focus()
      e.preventDefault()
    }
  }

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, CODE_LENGTH)
    if (pasted.length === 0) return

    const next = [...EMPTY_CODE]
    for (let i = 0; i < pasted.length; i++) {
      next[i] = pasted[i]
    }
    setDigits(next)
    setError('')

    // Focus last filled or next empty
    const focusIndex = Math.min(pasted.length, CODE_LENGTH - 1)
    inputRefs.current[focusIndex]?.focus()
    // Auto-submit is handled by the useEffect on digits
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    try {
      await apiClient.post('/auth/resend-verification')
      setResendCooldown(60)
      setError('')
    } catch (err: unknown) {
      setError(extractError(err, 'Failed to resend code.'))
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
          <p className="text-text-muted text-sm">Verify your email</p>
        </div>

        <Card glow>
          <div className="text-center mb-6">
            <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-accent/10 flex items-center justify-center">
              <svg className="w-7 h-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
              </svg>
            </div>
            <p className="text-sm text-text-muted">
              We sent a 6-digit code to your email.
              <br />Enter it below to verify your account.
            </p>
          </div>

          {error && (
            <div className="mb-4 text-red-400 text-xs bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2 text-center">
              {error}
            </div>
          )}

          {/* 6-digit code input */}
          <div className="flex justify-center gap-2 mb-6">
            {digits.map((digit, i) => (
              <input
                key={i}
                ref={el => { inputRefs.current[i] = el }}
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                autoComplete={i === 0 ? 'one-time-code' : 'off'}
                maxLength={CODE_LENGTH}
                value={digit}
                onChange={e => handleChange(i, e.target.value)}
                onKeyDown={e => handleKeyDown(i, e)}
                onPaste={handlePaste}
                autoFocus={i === 0}
                className="w-11 h-13 text-center text-xl font-bold bg-background border border-border rounded-lg text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-colors"
              />
            ))}
          </div>

          <Button
            onClick={() => handleSubmit()}
            disabled={loading || digits.some(d => !d)}
            className="w-full mb-4"
          >
            {loading ? 'Verifying...' : 'Verify Email'}
          </Button>

          {/* Resend */}
          <div className="text-center">
            <button
              type="button"
              onClick={handleResend}
              disabled={resendCooldown > 0}
              className="text-xs text-text-muted hover:text-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resendCooldown > 0
                ? `Resend code in ${resendCooldown}s`
                : 'Resend verification code'}
            </button>
          </div>
        </Card>

        <p className="text-center text-text-muted text-xs mt-5">
          Wrong email?{' '}
          <button
            type="button"
            onClick={() => {
              localStorage.removeItem('token')
              navigate('/register')
            }}
            className="text-accent hover:underline"
          >
            Start over
          </button>
        </p>
      </motion.div>
    </div>
  )
}

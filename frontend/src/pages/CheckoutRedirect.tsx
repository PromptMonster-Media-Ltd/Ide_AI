/**
 * CheckoutRedirect — Processes pending plan selection after sign-up.
 * Reads the saved plan from sessionStorage, creates a Stripe checkout session,
 * and redirects the user to Stripe. Falls back to /home if anything goes wrong.
 * @module pages/CheckoutRedirect
 */
import { useEffect, useRef } from 'react'
import apiClient from '../lib/apiClient'

export function CheckoutRedirect() {
  const called = useRef(false)

  useEffect(() => {
    if (called.current) return
    called.current = true

    const go = async () => {
      const raw = sessionStorage.getItem('pending_plan')
      sessionStorage.removeItem('pending_plan')

      if (!raw) {
        window.location.href = '/home'
        return
      }

      try {
        const { priceId, cycle } = JSON.parse(raw)
        const { data } = await apiClient.post('/billing/checkout', {
          price_id: priceId,
          cycle,
        })
        window.location.href = data.checkout_url
      } catch {
        // If checkout fails, just send them home
        window.location.href = '/home'
      }
    }

    go()
  }, [])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white text-sm">Setting up your subscription...</p>
      </div>
    </div>
  )
}

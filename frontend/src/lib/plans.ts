/**
 * Shared pricing plan data used by Landing page and UpgradeModal.
 * @module lib/plans
 */

export type Cycle = 'monthly' | 'yearly'

export interface Plan {
  id: string
  name: string
  tagline: string
  monthly: number
  yearly: number
  features: string[]
  excluded?: string[]
  cta: string
  popular?: boolean
  stripePriceMonthly?: string
  stripePriceYearly?: string
}

export const PLANS: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    tagline: 'Get a feel for the platform',
    monthly: 0,
    yearly: 0,
    features: [
      'Up to 3 projects',
      'AI discovery engine',
      'Concept sheet generation',
      'Design blocks builder',
      'Basic export (PDF)',
    ],
    excluded: [
      'Market analysis module',
      'AI partner style selector',
      'Advanced exports',
      'Priority support',
    ],
    cta: 'Start Free',
  },
  {
    id: 'basic',
    name: 'Basic',
    tagline: 'For serious creators',
    monthly: 12,
    yearly: 9,
    features: [
      'Unlimited projects',
      'AI discovery engine',
      'Concept sheet generation',
      'Design blocks builder',
      'Market analysis module',
      'Basic export (PDF, Markdown)',
    ],
    excluded: [
      'AI partner style selector',
      'Advanced exports (JSON, API)',
      'Priority support',
    ],
    cta: 'Get Basic',
    stripePriceMonthly: 'price_basic_monthly',
    stripePriceYearly: 'price_basic_yearly',
  },
  {
    id: 'pro',
    name: 'Pro',
    tagline: 'The full Ide/AI experience',
    monthly: 17,
    yearly: 14,
    features: [
      'Unlimited projects',
      'AI discovery engine',
      'Concept sheet generation',
      'Design blocks builder',
      'Market analysis module',
      'AI partner style selector',
      'All export formats',
      'Sprint planner & pitch mode',
      'Priority support',
      'Early access to new modules',
    ],
    cta: 'Go Pro',
    popular: true,
    stripePriceMonthly: 'price_pro_monthly',
    stripePriceYearly: 'price_pro_yearly',
  },
]

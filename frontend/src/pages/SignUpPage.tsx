/**
 * SignUpPage — Clerk-managed sign-up with dark glassmorphism styling.
 * @module pages/SignUpPage
 */
import { SignUp } from '@clerk/clerk-react'

export function SignUpPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <SignUp
        routing="path"
        path="/sign-up"
        signInUrl="/sign-in"
        forceRedirectUrl="/home"
      />
    </div>
  )
}

/**
 * SignInPage — Clerk-managed sign-in with dark glassmorphism styling.
 * @module pages/SignInPage
 */
import { SignIn } from '@clerk/clerk-react'

export function SignInPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <SignIn
        routing="path"
        path="/sign-in"
        signUpUrl="/sign-up"
        forceRedirectUrl="/home"
      />
    </div>
  )
}

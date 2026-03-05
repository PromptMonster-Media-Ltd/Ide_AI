/**
 * Settings — Application settings and preferences.
 * @module pages/Settings
 */
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'

export function Settings() {
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <div className="ml-16 flex-1 flex flex-col h-screen">
        <TopBar title="Settings" subtitle="Configure your workspace" />

        <div className="flex-1 p-6 overflow-y-auto max-w-2xl">
          <Card className="mb-6">
            <h3 className="text-sm font-semibold text-white mb-4">Account</h3>
            <Button variant="ghost" onClick={handleLogout}>
              Sign Out
            </Button>
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-white mb-2">About</h3>
            <p className="text-xs text-text-muted">
              Ide/AI v0.1.0 — Transform rough ideas into structured design kits.
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}

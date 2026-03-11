/**
 * Settings — User profile, account management, and preferences.
 * @module pages/Settings
 */
import { useEffect, useState } from 'react'
import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import apiClient from '../lib/apiClient'
import { useTutorialStore } from '../stores/tutorialStore'

interface UserProfile {
  id: string
  email: string
  name: string | null
  display_name: string | null
  avatar_url: string | null
  oauth_provider: string | null
  preferences: Record<string, unknown> | null
  created_at: string
}

export function Settings() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  // Profile form
  const [name, setName] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  // Tutorial reset
  const [tutorialReset, setTutorialReset] = useState(false)

  // Password form
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [pwSaving, setPwSaving] = useState(false)
  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState(false)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get('/auth/me')
      setProfile(data)
      setName(data.name || '')
      setDisplayName(data.display_name || '')
    } catch (err) {
      console.error('Failed to fetch profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProfile = async () => {
    setSaving(true)
    setSaved(false)
    try {
      const { data } = await apiClient.patch('/auth/me', {
        name: name.trim() || null,
        display_name: displayName.trim() || null,
      })
      setProfile(data)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      console.error('Failed to save profile:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async () => {
    setPwError('')
    setPwSuccess(false)

    if (newPw.length < 8) {
      setPwError('New password must be at least 8 characters.')
      return
    }
    if (newPw !== confirmPw) {
      setPwError('New passwords do not match.')
      return
    }

    setPwSaving(true)
    try {
      await apiClient.post('/auth/me/password', {
        current_password: currentPw,
        new_password: newPw,
      })
      setPwSuccess(true)
      setCurrentPw('')
      setNewPw('')
      setConfirmPw('')
      setTimeout(() => setPwSuccess(false), 3000)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to change password.'
      setPwError(msg)
    } finally {
      setPwSaving(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  const isOAuth = !!profile?.oauth_provider

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <div className="ml-0 md:ml-[232px] pb-14 md:pb-0 flex-1 flex flex-col h-screen">
        <TopBar title="Settings" subtitle="Manage your profile and preferences" />

        <div className="flex-1 p-4 md:p-6 overflow-y-auto pb-20 md:pb-6">
          <div className="max-w-2xl space-y-6">
            {loading ? (
              <div className="text-center py-12 text-text-muted text-sm">Loading profile...</div>
            ) : (
              <>
                {/* ── Profile section ── */}
                <Card>
                  <h3 className="text-sm font-semibold text-white mb-4">Profile</h3>

                  {/* Avatar + email badge */}
                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-12 h-12 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center text-lg text-accent font-bold shrink-0">
                      {profile?.avatar_url ? (
                        <img
                          src={profile.avatar_url}
                          alt=""
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        (profile?.name || profile?.email || '?')[0].toUpperCase()
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-white font-medium truncate">
                        {profile?.email}
                      </p>
                      {isOAuth && (
                        <span className="text-[10px] bg-white/5 border border-border px-2 py-0.5 rounded text-text-muted capitalize">
                          {profile.oauth_provider} account
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Name fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-xs text-text-muted font-medium mb-1.5">
                        Name
                      </label>
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your name"
                        className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-text-muted font-medium mb-1.5">
                        Display Name
                      </label>
                      <input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        placeholder="How AI greets you"
                        className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button size="sm" onClick={handleSaveProfile} disabled={saving}>
                      {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Profile'}
                    </Button>
                  </div>
                </Card>

                {/* ── Password section (email/password users only) ── */}
                {!isOAuth && (
                  <Card>
                    <h3 className="text-sm font-semibold text-white mb-4">Change Password</h3>

                    {pwError && (
                      <div className="text-red-400 text-xs bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2 mb-4">
                        {pwError}
                      </div>
                    )}
                    {pwSuccess && (
                      <div className="text-green-400 text-xs bg-green-400/10 border border-green-400/20 rounded-lg px-3 py-2 mb-4">
                        Password updated successfully.
                      </div>
                    )}

                    <div className="space-y-3 mb-4">
                      <div>
                        <label className="block text-xs text-text-muted font-medium mb-1.5">
                          Current Password
                        </label>
                        <input
                          type="password"
                          value={currentPw}
                          onChange={(e) => setCurrentPw(e.target.value)}
                          className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                        />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs text-text-muted font-medium mb-1.5">
                            New Password
                          </label>
                          <input
                            type="password"
                            value={newPw}
                            onChange={(e) => setNewPw(e.target.value)}
                            placeholder="Min. 8 characters"
                            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-text-muted font-medium mb-1.5">
                            Confirm New Password
                          </label>
                          <input
                            type="password"
                            value={confirmPw}
                            onChange={(e) => setConfirmPw(e.target.value)}
                            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
                          />
                        </div>
                      </div>
                    </div>

                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={handleChangePassword}
                      disabled={pwSaving || !currentPw || !newPw}
                    >
                      {pwSaving ? 'Updating...' : 'Update Password'}
                    </Button>
                  </Card>
                )}

                {/* ── Account section ── */}
                <Card>
                  <h3 className="text-sm font-semibold text-white mb-3">Account</h3>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-text-muted">
                      Member since {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : '...'}
                    </p>
                    <Button variant="ghost" size="sm" onClick={handleLogout}>
                      Sign Out
                    </Button>
                  </div>
                </Card>

                {/* ── Tutorial ── */}
                <Card>
                  <h3 className="text-sm font-semibold text-white mb-3">Tutorial</h3>
                  <p className="text-xs text-text-muted mb-3">
                    Reset all tutorial hints, beacons, and stage interludes so they appear again.
                  </p>
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        useTutorialStore.getState().resetTutorial()
                        setTutorialReset(true)
                        setTimeout(() => setTutorialReset(false), 2000)
                      }}
                    >
                      Reset Tutorial
                    </Button>
                    {tutorialReset && (
                      <span className="text-xs text-green-400">Tutorial hints reset!</span>
                    )}
                  </div>
                </Card>

                {/* ── About ── */}
                <Card>
                  <h3 className="text-sm font-semibold text-white mb-2">About</h3>
                  <p className="text-xs text-text-muted">
                    Ide/AI v0.1.0 — Transform rough ideas into structured design kits.
                  </p>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

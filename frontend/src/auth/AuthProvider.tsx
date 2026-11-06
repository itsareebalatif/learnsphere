import { useEffect, useMemo, useState, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'
import { supabase } from '../supabaseClient'
import { apiFetch, type Profile } from '../lib/api'
import { AuthContext, type AuthState } from './context'

interface Tokens {
  access_token: string
  refresh_token: string
}

interface SignupResponse {
  confirm_email: boolean
  session: Tokens | null
}

const RENEW_BEFORE_EXPIRY_MS = 60_000
const RETRY_MS = 30_000

/** Hand backend-issued tokens to supabase-js so apiFetch, sign-out and the listener keep working. */
async function adoptSession(tokens: Tokens) {
  const { error } = await supabase.auth.setSession({
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
  })
  if (error) throw error
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Whenever Supabase says we are logged in, make sure our own users row exists.
    const load = async (hasSession: boolean) => {
      if (!hasSession) {
        setProfile(null)
        setError(null)
        setLoading(false)
        return
      }
      try {
        setProfile(await apiFetch<Profile>('/api/auth/sync', { method: 'POST' }))
        setError(null)
      } catch (e) {
        setProfile(null)
        setError(e instanceof Error ? e.message : 'Could not reach the server')
      } finally {
        setLoading(false)
      }
    }

    // Renewals go through our backend, so supabase-js's own refresh timer is switched off
    // (two refreshers racing would fight over the one-time-use refresh token).
    void supabase.auth.stopAutoRefresh()

    let timer: ReturnType<typeof setTimeout> | undefined
    const scheduleRenewal = (session: Session | null, delay?: number) => {
      clearTimeout(timer)
      if (!session?.expires_at) return
      const expiresAt = session.expires_at * 1000
      timer = setTimeout(
        async () => {
          try {
            const tokens = await apiFetch<Tokens>('/api/auth/refresh', {
              method: 'POST',
              body: JSON.stringify({ refresh_token: session.refresh_token }),
            })
            await adoptSession(tokens) // fires the listener below, which schedules the next renewal
          } catch {
            // Give up (log out) only once the token has really expired; otherwise retry soon.
            if (Date.now() >= expiresAt) await supabase.auth.signOut({ scope: 'local' })
            else scheduleRenewal(session, RETRY_MS)
          }
        },
        delay ?? Math.max(expiresAt - Date.now() - RENEW_BEFORE_EXPIRY_MS, 5_000),
      )
    }

    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      // Defer: calling Supabase inside this callback can deadlock.
      setTimeout(() => scheduleRenewal(session), 0)
      if (event === 'TOKEN_REFRESHED') return
      setTimeout(() => void load(!!session), 0)
    })
    return () => {
      clearTimeout(timer)
      data.subscription.unsubscribe()
    }
  }, [])

  const value = useMemo<AuthState>(
    () => ({
      profile,
      loading,
      error,
      async signInWithPassword(email, password) {
        // The backend checks the password with Supabase and returns the session tokens.
        const tokens = await apiFetch<Tokens>('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        })
        await adoptSession(tokens)
      },
      async signUp(name, email, password) {
        const res = await apiFetch<SignupResponse>('/api/auth/signup', {
          method: 'POST',
          body: JSON.stringify({ email, password, full_name: name }),
        })
        if (!res.session) return 'confirm-email'
        await adoptSession(res.session)
        return 'signed-in'
      },
      async signInWithGoogle() {
        const { error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: { redirectTo: window.location.origin },
        })
        if (error) throw error
      },
      async sendPasswordReset(email) {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`,
        })
        if (error) throw error
      },
      async updatePassword(password) {
        const { error } = await supabase.auth.updateUser({ password })
        if (error) throw error
      },
      async refreshProfile() {
        setProfile(await apiFetch<Profile>('/api/auth/sync', { method: 'POST' }))
      },
      async signOut() {
        try {
          await apiFetch('/api/auth/logout', { method: 'POST' }) // revokes the session at Supabase
        } catch {
          /* offline or already expired: still clear this browser below */
        }
        await supabase.auth.signOut({ scope: 'local' }) // removes the tokens and fires SIGNED_OUT
      },
    }),
    [profile, loading, error],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

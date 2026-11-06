import { createContext, useContext } from 'react'
import type { Profile } from '../lib/api'

export interface AuthState {
  profile: Profile | null
  loading: boolean
  error: string | null
  signInWithPassword: (email: string, password: string) => Promise<void>
  signUp: (name: string, email: string, password: string) => Promise<'signed-in' | 'confirm-email'>
  signInWithGoogle: () => Promise<void>
  sendPasswordReset: (email: string) => Promise<void>
  updatePassword: (password: string) => Promise<void>
  refreshProfile: () => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}

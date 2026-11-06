import { Navigate, Outlet } from 'react-router-dom'
import type { Role } from '../lib/api'
import { useAuth } from './context'

/** Not logged in -> /login. Wrong role -> bounced to the user's own dashboard. */
export function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { profile, loading, error } = useAuth()
  if (loading) return <p className="center-msg">Loading…</p>
  if (error) return <p className="center-msg">Server error: {error}</p>
  if (!profile) return <Navigate to="/login" replace />
  if (roles && !roles.includes(profile.role)) return <Navigate to={`/${profile.role}`} replace />
  return <Outlet />
}

/** Login/signup pages: already logged in -> straight to your dashboard. */
export function PublicOnlyRoute() {
  const { profile, loading } = useAuth()
  if (loading) return <p className="center-msg">Loading…</p>
  if (profile) return <Navigate to={`/${profile.role}`} replace />
  return <Outlet />
}

import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { LogoMark } from '../auth/AuthLayout'
import { useAuth } from '../auth/context'

/** Header + page container used by every role dashboard. */
export function DashboardShell({ title, subtitle, actions, children }: {
  title: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
}) {
  const { profile, signOut } = useAuth()
  if (!profile) return null
  return (
    <div className="dashboard">
      <header>
        <Link to="/" className="logo"><LogoMark /> LearnSphere</Link>
        {profile.role === 'teacher' && (
          <nav className="top-nav">
            <NavLink to="/teacher" end>Classes</NavLink>
            <NavLink to="/teacher/courses">Courses</NavLink>
          </nav>
        )}
        <div className="user-chip">
          <span>{profile.full_name}</span>
          <span className="role-badge">{profile.role}</span>
          <button className="btn btn-outline" onClick={() => void signOut()}>Log out</button>
        </div>
      </header>
      <main>
        <div className="page-head">
          <div>
            <h1>{title}</h1>
            {subtitle && <p>{subtitle}</p>}
          </div>
          {actions}
        </div>
        {children}
      </main>
    </div>
  )
}

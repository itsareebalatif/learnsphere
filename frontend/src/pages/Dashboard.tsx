import { useAuth } from '../auth/context'
import { DashboardShell } from '../layout/DashboardShell'

/** Placeholder for roles whose real dashboard is built in a later week (parent). */
export default function Dashboard() {
  const { profile } = useAuth()
  if (!profile) return null
  return (
    <DashboardShell title={`Welcome, ${profile.full_name}`} subtitle="Your child's progress will appear here soon." >
      <div className="empty"><h2>Coming soon</h2><p>This dashboard is being built.</p></div>
    </DashboardShell>
  )
}

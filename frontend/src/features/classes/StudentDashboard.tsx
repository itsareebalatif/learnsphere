import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import { listClasses } from './api'

export default function StudentDashboard() {
  const { data: classes, error, loading } = useLoad(listClasses)

  return (
    <DashboardShell title="My classes" subtitle="The classes your teachers have added you to.">
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="alert alert-error">{error}</p>}
      {classes && classes.length === 0 && (
        <div className="empty">
          <h2>You are not in any class yet</h2>
          <p>Ask your teacher to add you using this email address.</p>
        </div>
      )}
      {classes && classes.length > 0 && (
        <div className="card-grid">
          {classes.map((c) => (
            <div key={c.class_id} className="class-card">
              <h2>{c.name}</h2>
              <p>{c.term || 'No term set'}</p>
              <span className="pill">Teacher: {c.teacher_name}</span>
            </div>
          ))}
        </div>
      )}
    </DashboardShell>
  )
}

import { useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import { addStudent, getClass, listStudents } from './api'

export default function ClassDetail() {
  const { classId = '' } = useParams()
  const cls = useLoad(() => getClass(classId))
  const students = useLoad(() => listStudents(classId))
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await addStudent(classId, email, name)
      setEmail('')
      setName('')
      await Promise.all([students.reload(), cls.reload()])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add the student')
    } finally {
      setBusy(false)
    }
  }

  if (cls.error) {
    return (
      <DashboardShell title="Class not found">
        <p className="alert alert-error">{cls.error}</p>
        <p><Link to="/teacher">← Back to my classes</Link></p>
      </DashboardShell>
    )
  }

  return (
    <DashboardShell
      title={cls.data?.name ?? 'Class'}
      subtitle={cls.data ? `${cls.data.term || 'No term set'} · ${cls.data.student_count} students` : undefined}
    >
      <p><Link to="/teacher">← Back to my classes</Link></p>

      <section className="panel">
        <h2>Add a student</h2>
        <form className="inline-form" onSubmit={submit}>
          <label className="field">
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="student@school.edu" required />
          </label>
          <label className="field">
            Name (for new students)
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Kim Kid" maxLength={120} />
          </label>
          <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Adding…' : 'Add student'}</button>
        </form>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
      </section>

      <section className="panel">
        <h2>Students</h2>
        {students.loading && <p className="muted">Loading…</p>}
        {students.data && students.data.length === 0 && <p className="muted">No students yet.</p>}
        {students.data && students.data.length > 0 && (
          <table className="table">
            <thead><tr><th>Name</th><th>Email</th><th>Status</th></tr></thead>
            <tbody>
              {students.data.map((s) => (
                <tr key={s.user_id}>
                  <td>{s.full_name}</td>
                  <td>{s.email}</td>
                  <td><span className={s.joined ? 'pill pill-ok' : 'pill'}>{s.joined ? 'Active' : 'Invited'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </DashboardShell>
  )
}

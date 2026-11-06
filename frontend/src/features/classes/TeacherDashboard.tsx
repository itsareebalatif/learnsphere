import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Modal } from '../../components/Modal'
import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import { createClass, listClasses } from './api'

export default function TeacherDashboard() {
  const { data: classes, error, loading, reload } = useLoad(listClasses)
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [term, setTerm] = useState('')
  const [formError, setFormError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setFormError('')
    try {
      await createClass(name, term)
      setOpen(false)
      setName('')
      setTerm('')
      await reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Could not create the class')
    } finally {
      setBusy(false)
    }
  }

  return (
    <DashboardShell
      title="My classes"
      subtitle="Create a class, then add your students by email."
      actions={<button className="btn btn-primary" onClick={() => setOpen(true)}>+ New class</button>}
    >
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="alert alert-error">{error}</p>}
      {classes && classes.length === 0 && (
        <div className="empty">
          <h2>No classes yet</h2>
          <p>Create your first class to start adding students.</p>
        </div>
      )}
      {classes && classes.length > 0 && (
        <div className="card-grid">
          {classes.map((c) => (
            <Link key={c.class_id} to={`/teacher/classes/${c.class_id}`} className="class-card">
              <h2>{c.name}</h2>
              <p>{c.term || 'No term set'}</p>
              <span className="pill">{c.student_count} {c.student_count === 1 ? 'student' : 'students'}</span>
            </Link>
          ))}
        </div>
      )}

      {open && (
        <Modal title="New class" onClose={() => setOpen(false)}>
          <form className="form-stack" onSubmit={submit}>
            <label className="field">
              Class name
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Biology 101" required maxLength={100} autoFocus />
            </label>
            <label className="field">
              Term (optional)
              <input value={term} onChange={(e) => setTerm(e.target.value)} placeholder="Fall 2026" maxLength={20} />
            </label>
            {formError && <p className="alert alert-error" role="alert">{formError}</p>}
            <div className="modal-actions">
              <button type="button" className="btn btn-outline" onClick={() => setOpen(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Creating…' : 'Create class'}</button>
            </div>
          </form>
        </Modal>
      )}
    </DashboardShell>
  )
}

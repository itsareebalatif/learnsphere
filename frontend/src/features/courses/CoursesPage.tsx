import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Modal } from '../../components/Modal'
import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import { createCourse, listCourses } from './api'

export default function CoursesPage() {
  const { data: courses, error, loading, reload } = useLoad(listCourses)
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [formError, setFormError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setFormError('')
    try {
      await createCourse(title, subject)
      setOpen(false)
      setTitle('')
      setSubject('')
      await reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Could not create the course')
    } finally {
      setBusy(false)
    }
  }

  return (
    <DashboardShell
      title="My courses"
      subtitle="Upload your slides, PDFs and videos. The AI will turn them into a course."
      actions={<button className="btn btn-primary" onClick={() => setOpen(true)}>+ New course</button>}
    >
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="alert alert-error">{error}</p>}
      {courses && courses.length === 0 && (
        <div className="empty">
          <h2>No courses yet</h2>
          <p>Create a course, then upload the material it will be built from.</p>
        </div>
      )}
      {courses && courses.length > 0 && (
        <div className="card-grid">
          {courses.map((c) => (
            <Link key={c.course_id} to={`/teacher/courses/${c.course_id}`} className="class-card">
              <h2>{c.title}</h2>
              <p>{c.subject || 'No subject set'}</p>
              <span className="pill">{c.file_count} {c.file_count === 1 ? 'file' : 'files'} · {c.status}</span>
            </Link>
          ))}
        </div>
      )}

      {open && (
        <Modal title="New course" onClose={() => setOpen(false)}>
          <form className="form-stack" onSubmit={submit}>
            <label className="field">
              Title
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Introduction to Biology" required maxLength={200} autoFocus />
            </label>
            <label className="field">
              Subject (optional)
              <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Science" maxLength={80} />
            </label>
            {formError && <p className="alert alert-error" role="alert">{formError}</p>}
            <div className="modal-actions">
              <button type="button" className="btn btn-outline" onClick={() => setOpen(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Creating…' : 'Create course'}</button>
            </div>
          </form>
        </Modal>
      )}
    </DashboardShell>
  )
}

import { useState, type FormEvent } from 'react'
import { useAuth } from '../../auth/context'
import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import type { Role } from '../../lib/api'
import { createSchool, getSchool, inviteUser, listSchoolUsers, type School } from './api'

function CreateSchool() {
  const { refreshProfile } = useAuth()
  const [name, setName] = useState('')
  const [type, setType] = useState<School['type']>('school')
  const [region, setRegion] = useState<School['region']>('eu')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await createSchool(name, type, region)
      await refreshProfile() // the profile now has an org_id, so the page switches to the school view
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the school')
      setBusy(false)
    }
  }

  return (
    <section className="panel narrow">
      <h2>Create your school</h2>
      <p className="muted">Set up your organisation first, then invite teachers, students and parents.</p>
      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Oak High School" required minLength={2} maxLength={150} />
        </label>
        <label className="field">
          Type
          <select value={type} onChange={(e) => setType(e.target.value as School['type'])}>
            <option value="school">School</option>
            <option value="university">University</option>
            <option value="company">Company</option>
          </select>
        </label>
        <label className="field">
          Data region
          <select value={region} onChange={(e) => setRegion(e.target.value as School['region'])}>
            <option value="eu">Europe</option>
            <option value="us">United States</option>
          </select>
        </label>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Creating…' : 'Create school'}</button>
      </form>
    </section>
  )
}

function SchoolView() {
  const school = useLoad(getSchool)
  const users = useLoad(listSchoolUsers)
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState<Role>('teacher')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await inviteUser(email, name, role)
      setEmail('')
      setName('')
      await users.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not invite the user')
    } finally {
      setBusy(false)
    }
  }

  return (
    <DashboardShell title={school.data?.name ?? 'Your school'} subtitle="Invite people and see who has joined.">
      <section className="panel">
        <h2>Invite a user</h2>
        <form className="inline-form" onSubmit={submit}>
          <label className="field">
            Full name
            <input value={name} onChange={(e) => setName(e.target.value)} required maxLength={120} />
          </label>
          <label className="field">
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="field">
            Role
            <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
              <option value="teacher">Teacher</option>
              <option value="student">Student</option>
              <option value="parent">Parent</option>
            </select>
          </label>
          <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Inviting…' : 'Invite'}</button>
        </form>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <p className="muted small">They join by signing up or logging in with this email address.</p>
      </section>

      <section className="panel">
        <h2>People in your school</h2>
        {users.loading && <p className="muted">Loading…</p>}
        {users.error && <p className="alert alert-error">{users.error}</p>}
        {users.data && (
          <table className="table">
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
            <tbody>
              {users.data.map((u) => (
                <tr key={u.user_id}>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td><span className="role-badge">{u.role}</span></td>
                  <td><span className={u.joined ? 'pill pill-ok' : 'pill'}>{u.joined ? 'Active' : 'Invited'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </DashboardShell>
  )
}

export default function AdminDashboard() {
  const { profile } = useAuth()
  if (!profile?.org_id) {
    return (
      <DashboardShell title="Welcome" subtitle="Let's set up your organisation.">
        <CreateSchool />
      </DashboardShell>
    )
  }
  return <SchoolView />
}

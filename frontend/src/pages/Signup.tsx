import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { AuthLayout, GoogleIcon, Legal } from '../auth/AuthLayout'
import { useAuth } from '../auth/context'

export default function Signup() {
  const { signUp, signInWithGoogle } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      if ((await signUp(name, email, password)) === 'confirm-email') {
        setNotice('Check your email and click the confirmation link, then log in.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not sign up')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1>Create your account</h1>
        <p className="sub">Teachers start here. Students and parents are invited by their school.</p>
      </div>

      <button type="button" className="btn btn-outline" onClick={() => void signInWithGoogle()}>
        <GoogleIcon /> Sign up with Google
      </button>
      <div className="divider">or continue with email</div>

      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          Full name
          <input placeholder="Jane Smith" value={name} onChange={(e) => setName(e.target.value)} required autoComplete="name" />
        </label>
        <label className="field">
          Email
          <input type="email" placeholder="you@school.edu" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </label>
        <label className="field">
          Password
          <input type="password" placeholder="At least 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="new-password" />
        </label>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        {notice && <p className="alert alert-ok" role="status">{notice}</p>}
        <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button>
      </form>

      <p className="switch">Already have an account? <Link to="/login">Log in</Link></p>
      <Legal />
    </AuthLayout>
  )
}

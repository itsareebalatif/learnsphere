import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { AuthLayout, GoogleIcon, Legal } from '../auth/AuthLayout'
import { useAuth } from '../auth/context'

export default function Login() {
  const { signInWithPassword, signInWithGoogle } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await signInWithPassword(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1>Welcome back</h1>
        <p className="sub">Log in to continue to LearnSphere.</p>
      </div>

      <button type="button" className="btn btn-outline" onClick={() => void signInWithGoogle()}>
        <GoogleIcon /> Continue with Google
      </button>
      <div className="divider">or continue with email</div>

      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          Email
          <input type="email" placeholder="you@school.edu" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </label>
        <label className="field">
          <span className="field-row">Password <Link to="/forgot-password">Forgot password?</Link></span>
          <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
        </label>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
      </form>

      <p className="switch">New to LearnSphere? <Link to="/signup">Create an account</Link></p>
      <Legal />
    </AuthLayout>
  )
}

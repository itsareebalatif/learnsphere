import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { AuthLayout } from '../auth/AuthLayout'
import { useAuth } from '../auth/context'

export default function ForgotPassword() {
  const { sendPasswordReset } = useAuth()
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await sendPasswordReset(email)
      setSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send the email')
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1>Reset your password</h1>
        <p className="sub">Enter your email and we'll send you a link to choose a new one.</p>
      </div>
      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          Email
          <input type="email" placeholder="you@school.edu" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        {sent && <p className="alert alert-ok" role="status">If that email has an account, a reset link is on its way.</p>}
        <button type="submit" className="btn btn-primary">Send reset link</button>
      </form>
      <p className="switch"><Link to="/login">← Back to log in</Link></p>
    </AuthLayout>
  )
}

import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthLayout } from '../auth/AuthLayout'
import { useAuth } from '../auth/context'

/** Reached from the emailed link; Supabase has already logged the user in at this point. */
export default function ResetPassword() {
  const { updatePassword } = useAuth()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await updatePassword(password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update the password')
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1>Choose a new password</h1>
        <p className="sub">Pick something at least 8 characters long.</p>
      </div>
      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          New password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="new-password" />
        </label>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary">Save password</button>
      </form>
    </AuthLayout>
  )
}

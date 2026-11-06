import type { ReactNode } from 'react'

export function LogoMark() {
  return (
    <span className="logo-mark" aria-hidden="true">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 10 12 5 2 10l10 5 10-5Z" />
        <path d="M6 12v5c3 2.5 9 2.5 12 0v-5" />
      </svg>
    </span>
  )
}

const YEAR = new Date().getFullYear()

const FEATURES = [
  'Turn slides, PDFs and videos into a full course',
  'A personal AI tutor for every student',
  'Fast, fair grading you stay in control of',
]

/** Split-screen shell shared by login, sign-up and password pages. */
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="auth-page">
      <aside className="auth-brand">
        <div className="logo"><LogoMark /> LearnSphere</div>
        <div className="brand-copy">
          <h2>Teach more. Grade less.<br />Help every student.</h2>
          <p>The learning platform where your material becomes a course and every learner gets an AI tutor.</p>
          <ul className="feature-list">
            {FEATURES.map((f) => (
              <li key={f}><span className="tick">✓</span>{f}</li>
            ))}
          </ul>
        </div>
        <div className="brand-foot">© {YEAR} LearnSphere</div>
      </aside>
      <main className="auth-side">
        <div className="auth-card">
          <div className="logo mobile-logo"><LogoMark /> LearnSphere</div>
          {children}
        </div>
      </main>
    </div>
  )
}

export function Legal() {
  return (
    <p className="legal">
      By continuing, you agree to the <a href="/terms">Terms of Service</a> and{' '}
      <a href="/privacy">Privacy Policy</a>.
      <span className="privacy-note">Student data is never used to train AI models.</span>
    </p>
  )
}

export function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.2C12.4 13.5 17.7 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.8c4.3-4 6.9-9.9 6.9-17.2z" />
      <path fill="#FBBC05" d="M10.5 28.6a14.5 14.5 0 0 1 0-9.2l-7.9-6.2a24 24 0 0 0 0 21.6l7.9-6.2z" />
      <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.8c-2.1 1.4-4.8 2.3-8.5 2.3-6.3 0-11.6-4-13.5-9.9l-7.9 6.2C6.5 42.6 14.6 48 24 48z" />
    </svg>
  )
}

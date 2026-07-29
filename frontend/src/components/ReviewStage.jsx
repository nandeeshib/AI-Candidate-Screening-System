import { useState } from 'react'
import { api } from '../api'

export default function ReviewStage({ session, onStarted }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleStart() {
    setLoading(true)
    setError(null)
    try {
      const firstQuestion = await api.startInterview(session.session_id)
      onStarted(firstQuestion)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="eyebrow">Step 02 — Context construction</div>
      <h1 className="headline">Here's what we picked up</h1>
      <p className="lede">
        These are the skills detected on the resume for the <strong>{session.role_label}</strong> role.
        Each one will drive a targeted, retrieval-grounded question.
      </p>

      <div className="card">
        {session.extracted_skills.length > 0 ? (
          <div className="skill-chips">
            {session.extracted_skills.map((s) => (
              <span className="chip brass" key={s}>{s}</span>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
            No specific skill keywords were detected — the interview will fall back to
            general {session.role_label} topics.
          </p>
        )}

        {error && <div className="error-banner" style={{ marginTop: 20 }}>{error}</div>}

        <div style={{ marginTop: 24 }}>
          <button className="primary" disabled={loading} onClick={handleStart}>
            {loading ? 'Retrieving context…' : 'Start interview'}
          </button>
        </div>
      </div>
    </div>
  )
}

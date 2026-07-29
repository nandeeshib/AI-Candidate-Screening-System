import { useEffect, useState } from 'react'
import { api } from '../api'

export default function SetupStage({ onSessionCreated }) {
  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getRoles().then(setRoles).catch((e) => setError(e.message))
  }, [])

  const canSubmit = selectedRole && file && !loading

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    try {
      const session = await api.createSession(selectedRole, file)
      onSessionCreated(session)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="eyebrow">Step 01 — Setup</div>
      <h1 className="headline">Set up the screening session</h1>
      <p className="lede">
        Choose the role you're screening for and upload the candidate's resume.
        Questions will be generated from a knowledge base grounded to that role,
        shaped by what's actually on the resume.
      </p>

      <div className="card">
        <div className="role-grid">
          {roles.map((r) => (
            <button
              key={r.id}
              className={`role-option ${selectedRole === r.id ? 'selected' : ''}`}
              onClick={() => setSelectedRole(r.id)}
            >
              {r.label}
              <span className="role-option-check" />
            </button>
          ))}
        </div>

        <label
          htmlFor="resume-input"
          className={`upload-zone ${file ? 'has-file' : ''}`}
        >
          <div className="upload-zone-label">
            {file ? 'Resume selected' : 'Click to upload resume (PDF or .txt)'}
          </div>
          {file && <div className="upload-zone-filename">{file.name}</div>}
        </label>
        <input
          id="resume-input"
          type="file"
          accept=".pdf,.txt"
          style={{ display: 'none' }}
          onChange={(e) => setFile(e.target.files[0] || null)}
        />

        {error && <div className="error-banner">{error}</div>}

        <button className="primary" disabled={!canSubmit} onClick={handleSubmit}>
          {loading ? 'Parsing resume…' : 'Continue'}
        </button>
      </div>
    </div>
  )
}

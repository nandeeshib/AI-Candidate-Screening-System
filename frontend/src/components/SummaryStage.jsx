import { useEffect, useState } from 'react'
import { api } from '../api'

export default function SummaryStage({ session }) {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getSummary(session.session_id).then(setSummary).catch((e) => setError(e.message))
  }, [session.session_id])

  if (error) return <div className="error-banner">{error}</div>
  if (!summary) return <div className="loading-line">Compiling summary…</div>

  return (
    <div>
      <div className="eyebrow">Step 04 — Summary</div>
      <h1 className="headline">Session complete</h1>
      <p className="lede">
        {summary.role_label} screening — {summary.answered_questions} of {summary.total_questions} questions answered.
      </p>

      <div className="summary-stats">
        <div className="summary-stat">
          <div className="summary-stat-value">{summary.answered_questions}</div>
          <div className="summary-stat-label">Questions answered</div>
        </div>
        <div className="summary-stat">
          <div className="summary-stat-value">{summary.average_answer_length}</div>
          <div className="summary-stat-label">Avg. words / answer</div>
        </div>
        <div className="summary-stat">
          <div className="summary-stat-value">{summary.topics_covered.length}</div>
          <div className="summary-stat-label">Topics covered</div>
        </div>
      </div>

      <div className="insight-box">{summary.insight}</div>

      <div className="skill-chips" style={{ marginBottom: 28 }}>
        {summary.extracted_skills.map((s) => <span className="chip" key={s}>{s}</span>)}
      </div>

      <div className="card">
        {summary.transcript.map((t) => (
          <div className="transcript-item" key={t.order_index}>
            <div className="transcript-q">Q{t.order_index + 1}. {t.question_text}</div>
            <div className="source-tags">
              {t.source_topic && <span className="chip">{t.source_topic}</span>}
              {t.triggering_skill && <span className="chip brass">{t.triggering_skill}</span>}
            </div>
            <div className="transcript-a">{t.answer_text || 'No answer recorded.'}</div>
          </div>
        ))}
      </div>

      <div className="footer-note">Session ID: {summary.session_id}</div>
    </div>
  )
}

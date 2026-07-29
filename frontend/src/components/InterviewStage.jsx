import { useState } from 'react'
import { api } from '../api'

export default function InterviewStage({ session, question, onQuestionAdvance, onCompleted }) {
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit() {
    if (!answer.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await api.submitAnswer(session.session_id, question.question_id, answer)
      setAnswer('')
      if (result.completed) {
        onCompleted()
      } else {
        onQuestionAdvance(result.next_question)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="eyebrow">Step 03 — Interview</div>
      <div className="progress-line">
        Question {question.order_index + 1} of {question.total_questions}
      </div>

      <div className="card">
        <p className="question-text">{question.question_text}</p>

        <div className="source-tags">
          {question.source_topic && (
            <span className="chip">sourced from: {question.source_topic}</span>
          )}
          {question.triggering_skill && (
            <span className="chip brass">skill: {question.triggering_skill}</span>
          )}
        </div>

        <textarea
          className="answer-box"
          placeholder="Type the candidate's answer here…"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
        />

        {error && <div className="error-banner">{error}</div>}

        <button className="primary" disabled={loading || !answer.trim()} onClick={handleSubmit}>
          {loading
            ? 'Generating next question…'
            : question.order_index + 1 >= question.total_questions
            ? 'Submit final answer'
            : 'Submit & continue'}
        </button>
      </div>
    </div>
  )
}

import { useState } from 'react'
import SetupStage from './components/SetupStage'
import ReviewStage from './components/ReviewStage'
import InterviewStage from './components/InterviewStage'
import SummaryStage from './components/SummaryStage'

const STAGES = ['setup', 'review', 'interview', 'summary']

export default function App() {
  const [stage, setStage] = useState('setup')
  const [session, setSession] = useState(null)
  const [question, setQuestion] = useState(null)

  const stageIndex = STAGES.indexOf(stage)

  return (
    <div className="app-shell">
      <div className="brand">
        <span className="brand-mark" />
        <span className="brand-name">Panel</span>
        <span className="brand-tag">RAG Screening Interview</span>
      </div>

      <div className="stage-track">
        {STAGES.map((s, i) => (
          <div
            key={s}
            className={`stage-dot ${i === stageIndex ? 'active' : i < stageIndex ? 'done' : ''}`}
          />
        ))}
      </div>

      {stage === 'setup' && (
        <SetupStage
          onSessionCreated={(s) => {
            setSession(s)
            setStage('review')
          }}
        />
      )}

      {stage === 'review' && session && (
        <ReviewStage
          session={session}
          onStarted={(q) => {
            setQuestion(q)
            setStage('interview')
          }}
        />
      )}

      {stage === 'interview' && session && question && (
        <InterviewStage
          session={session}
          question={question}
          onQuestionAdvance={(q) => setQuestion(q)}
          onCompleted={() => setStage('summary')}
        />
      )}

      {stage === 'summary' && session && <SummaryStage session={session} />}
    </div>
  )
}

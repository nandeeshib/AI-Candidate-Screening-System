const BASE = '/api'

async function handle(res) {
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch (_) {}
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  getRoles: () => fetch(`${BASE}/roles`).then(handle),

  createSession: (roleId, resumeFile) => {
    const form = new FormData()
    form.append('role_id', roleId)
    form.append('resume', resumeFile)
    return fetch(`${BASE}/sessions`, { method: 'POST', body: form }).then(handle)
  },

  startInterview: (sessionId) =>
    fetch(`${BASE}/interview/${sessionId}/start`, { method: 'POST' }).then(handle),

  submitAnswer: (sessionId, questionId, answerText) =>
    fetch(`${BASE}/interview/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, question_id: questionId, answer_text: answerText }),
    }).then(handle),

  getSummary: (sessionId) =>
    fetch(`${BASE}/sessions/${sessionId}/summary`).then(handle),
}

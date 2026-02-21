import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type ChatIntent = 'search' | 'chat' | 'unknown'

type Candidate = {
  id?: string
  full_name?: string
  current_role?: string
  years_experience?: number
  location?: string
  skills?: string[]
}

type ChatApiResponse = {
  message: string
  intent: ChatIntent
  confidence?: number
  data?: {
    candidates?: Candidate[]
    count?: number
  } | null
}

type Message = {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  intent?: ChatIntent
  candidates?: Candidate[]
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Hi! I can help you find candidates by skill, role, location, and experience. Try: "Find senior Python developers in NYC."',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      intent: 'chat',
    },
  ])
  const [isLoading, setIsLoading] = useState(false)

  const placeholder = useMemo(() => {
    if (isLoading) {
      return 'Waiting for backend response...'
    }
    return 'Ask about candidates, e.g. "Find frontend engineers with React and 5+ years"'
  }, [isLoading])

  const sendMessage = async (event: FormEvent) => {
    event.preventDefault()
    const content = draft.trim()
    if (!content || isLoading) {
      return
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMessage])
    setDraft('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const payload = (await response.json()) as ChatApiResponse
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: payload.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: payload.intent,
        candidates: payload.data?.candidates,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const fallbackMessage: Message = {
        id: crypto.randomUUID(),
        role: 'system',
        content:
          error instanceof Error
            ? `Could not connect to ${API_BASE_URL}/chat. ${error.message}`
            : 'Unexpected error while reaching the chat API.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, fallbackMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="chat-layout">
      <section className="chat-shell">
        <header className="chat-header">
          <p className="eyebrow">Candidate DB Assistant</p>
          <h1>Recruiting Chat Console</h1>
          <span className="api-pill">API: {API_BASE_URL}</span>
        </header>

        <div className="message-feed" aria-live="polite">
          {messages.map((message) => (
            <article key={message.id} className={`message message-${message.role}`}>
              <div className="message-meta">
                <strong>{message.role === 'user' ? 'You' : message.role === 'assistant' ? 'Assistant' : 'System'}</strong>
                <span>{message.timestamp}</span>
              </div>
              <p>{message.content}</p>

              {message.intent === 'search' && message.candidates && message.candidates.length > 0 && (
                <div className="candidate-grid">
                  {message.candidates.map((candidate, index) => (
                    <div key={`${candidate.id ?? candidate.full_name ?? 'candidate'}-${index}`} className="candidate-card">
                      <h3>{candidate.full_name ?? 'Unknown candidate'}</h3>
                      <p>{candidate.current_role ?? 'Role unavailable'}</p>
                      <ul>
                        <li>Experience: {candidate.years_experience ?? 'N/A'} years</li>
                        <li>Location: {candidate.location ?? 'N/A'}</li>
                        <li>Skills: {candidate.skills?.join(', ') ?? 'N/A'}</li>
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </article>
          ))}

          {isLoading && (
            <article className="message message-assistant loading">
              <div className="typing-dots" aria-label="Assistant is typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}
        </div>

        <form className="composer" onSubmit={sendMessage}>
          <label htmlFor="chat-message" className="sr-only">
            Message
          </label>
          <textarea
            id="chat-message"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={placeholder}
            rows={2}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || draft.trim().length === 0}>
            Send
          </button>
        </form>
      </section>
    </main>
  )
}

export default App

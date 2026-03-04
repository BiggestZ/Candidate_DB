import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type ChatIntent = 'search' | 'chat' | 'unknown'
type AppPage = 'assistant' | 'add' | 'manage'

type Candidate = {
  id?: string
  full_name?: string
  role?: string
  years_experience?: number
  location?: string
  skills?: string
}

type CandidateSearchResult = {
  id: string
  full_name: string
  email: string
  role: string
  years_experience?: number
  location?: string
  skills?: string
  github_url?: string | null
  linkedin_url?: string | null
  website_url?: string | null
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

type CandidateCreatePayload = {
  full_name: string
  email: string
  recent_role: string
  location?: string
  years_experience?: number
  skills: string[]
  summary?: string
  github_url?: string
  linkedin_url?: string
  website_url?: string
}

type CandidateUpdatePayload = Partial<CandidateCreatePayload>

type CandidateMutationResponse = {
  id: string
  message: string
}

type Message = {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  intent?: ChatIntent
  candidates?: Candidate[]
}

type CandidateFormState = {
  full_name: string
  email: string
  recent_role: string
  location: string
  years_experience: string
  skills: string
  summary: string
  github_url: string
  linkedin_url: string
  website_url: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const emptyCandidateForm = (): CandidateFormState => ({
  full_name: '',
  email: '',
  recent_role: '',
  location: '',
  years_experience: '',
  skills: '',
  summary: '',
  github_url: '',
  linkedin_url: '',
  website_url: '',
})

function parseSkillsCsv(skills: string): string[] {
  return skills
    .split(',')
    .map((skill) => skill.trim())
    .filter(Boolean)
}

function App() {
  const [activePage, setActivePage] = useState<AppPage>('assistant')
  const [draft, setDraft] = useState('')
  const [candidateForm, setCandidateForm] = useState<CandidateFormState>(emptyCandidateForm())
  const [candidateStatus, setCandidateStatus] = useState<string | null>(null)
  const [isSubmittingCandidate, setIsSubmittingCandidate] = useState(false)

  const [searchFilters, setSearchFilters] = useState({
    name: '',
    role: '',
    location: '',
    skill: '',
    email: '',
    min_years_experience: '',
    max_years_experience: '',
  })
  const [searchResults, setSearchResults] = useState<CandidateSearchResult[]>([])
  const [searchStatus, setSearchStatus] = useState<string | null>(null)
  const [isSearchingCandidates, setIsSearchingCandidates] = useState(false)

  const [editingCandidateId, setEditingCandidateId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<CandidateFormState>(emptyCandidateForm())
  const [editStatus, setEditStatus] = useState<string | null>(null)
  const [isSavingEdit, setIsSavingEdit] = useState(false)
  const [deletingCandidateId, setDeletingCandidateId] = useState<string | null>(null)

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

  const runCandidateSearch = async () => {
    const params = new URLSearchParams()

    if (searchFilters.name.trim()) params.set('name', searchFilters.name.trim())
    if (searchFilters.role.trim()) params.set('role', searchFilters.role.trim())
    if (searchFilters.location.trim()) params.set('location', searchFilters.location.trim())
    if (searchFilters.skill.trim()) params.set('skill', searchFilters.skill.trim())
    if (searchFilters.email.trim()) params.set('email', searchFilters.email.trim())

    if (searchFilters.min_years_experience.trim()) {
      const minYears = Number(searchFilters.min_years_experience)
      if (Number.isNaN(minYears) || minYears < 0) {
        setSearchStatus('Min years must be a valid non-negative number.')
        return
      }
      params.set('min_years_experience', String(minYears))
    }

    if (searchFilters.max_years_experience.trim()) {
      const maxYears = Number(searchFilters.max_years_experience)
      if (Number.isNaN(maxYears) || maxYears < 0) {
        setSearchStatus('Max years must be a valid non-negative number.')
        return
      }
      params.set('max_years_experience', String(maxYears))
    }

    params.set('limit', '25')

    try {
      setIsSearchingCandidates(true)
      setSearchStatus(null)

      const response = await fetch(`${API_BASE_URL}/candidates?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const payload = (await response.json()) as CandidateSearchResult[]
      setSearchResults(payload)
      setSearchStatus(`Found ${payload.length} candidate(s).`)

      if (payload.length === 0) {
        setEditingCandidateId(null)
        setEditForm(emptyCandidateForm())
      }
    } catch (error) {
      setSearchResults([])
      setSearchStatus(
        error instanceof Error
          ? `Could not search candidates. ${error.message}`
          : 'Unexpected error while searching candidates.',
      )
    } finally {
      setIsSearchingCandidates(false)
    }
  }

  const submitCandidateSearch = async (event: FormEvent) => {
    event.preventDefault()
    await runCandidateSearch()
  }

  const beginEditCandidate = (candidate: CandidateSearchResult) => {
    setEditingCandidateId(candidate.id)
    setEditStatus(null)
    setEditForm({
      full_name: candidate.full_name ?? '',
      email: candidate.email ?? '',
      recent_role: candidate.role ?? '',
      location: candidate.location ?? '',
      years_experience:
        candidate.years_experience === undefined || candidate.years_experience === null
          ? ''
          : String(candidate.years_experience),
      skills: candidate.skills ?? '',
      summary: '',
      github_url: candidate.github_url ?? '',
      linkedin_url: candidate.linkedin_url ?? '',
      website_url: candidate.website_url ?? '',
    })
  }

  const submitCandidateEdit = async (event: FormEvent) => {
    event.preventDefault()
    if (!editingCandidateId || isSavingEdit) {
      return
    }

    const payload: CandidateUpdatePayload = {}
    if (editForm.full_name.trim()) payload.full_name = editForm.full_name.trim()
    if (editForm.email.trim()) payload.email = editForm.email.trim()
    if (editForm.recent_role.trim()) payload.recent_role = editForm.recent_role.trim()
    if (editForm.location.trim()) payload.location = editForm.location.trim()
    if (editForm.summary.trim()) payload.summary = editForm.summary.trim()
    if (editForm.github_url.trim()) payload.github_url = editForm.github_url.trim()
    if (editForm.linkedin_url.trim()) payload.linkedin_url = editForm.linkedin_url.trim()
    if (editForm.website_url.trim()) payload.website_url = editForm.website_url.trim()

    payload.skills = parseSkillsCsv(editForm.skills)

    if (editForm.years_experience.trim()) {
      const years = Number(editForm.years_experience)
      if (Number.isNaN(years) || years < 0) {
        setEditStatus('Years experience must be a valid non-negative number.')
        return
      }
      payload.years_experience = years
    }

    try {
      setIsSavingEdit(true)
      setEditStatus(null)

      const response = await fetch(`${API_BASE_URL}/candidates/${editingCandidateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = (await response.json()) as CandidateMutationResponse
      setEditStatus(`${data.message} (ID: ${data.id})`)
      await runCandidateSearch()
    } catch (error) {
      setEditStatus(
        error instanceof Error
          ? `Could not update candidate. ${error.message}`
          : 'Unexpected error while updating candidate.',
      )
    } finally {
      setIsSavingEdit(false)
    }
  }

  const deleteCandidate = async (candidateId: string) => {
    if (!window.confirm('Delete this candidate? This action cannot be undone.')) {
      return
    }

    try {
      setDeletingCandidateId(candidateId)
      setEditStatus(null)

      const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = (await response.json()) as CandidateMutationResponse
      setSearchStatus(`${data.message} (ID: ${data.id})`)

      if (editingCandidateId === candidateId) {
        setEditingCandidateId(null)
        setEditForm(emptyCandidateForm())
      }

      await runCandidateSearch()
    } catch (error) {
      setSearchStatus(
        error instanceof Error
          ? `Could not delete candidate. ${error.message}`
          : 'Unexpected error while deleting candidate.',
      )
    } finally {
      setDeletingCandidateId(null)
    }
  }

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

  const submitCandidate = async (event: FormEvent) => {
    event.preventDefault()
    if (isSubmittingCandidate) return

    const payload: CandidateCreatePayload = {
      full_name: candidateForm.full_name.trim(),
      email: candidateForm.email.trim(),
      recent_role: candidateForm.recent_role.trim(),
      skills: parseSkillsCsv(candidateForm.skills),
    }

    if (!payload.full_name || !payload.email || !payload.recent_role) {
      setCandidateStatus('Name, email, and role are required.')
      return
    }

    if (candidateForm.location.trim()) payload.location = candidateForm.location.trim()
    if (candidateForm.summary.trim()) payload.summary = candidateForm.summary.trim()
    if (candidateForm.github_url.trim()) payload.github_url = candidateForm.github_url.trim()
    if (candidateForm.linkedin_url.trim()) payload.linkedin_url = candidateForm.linkedin_url.trim()
    if (candidateForm.website_url.trim()) payload.website_url = candidateForm.website_url.trim()
    if (candidateForm.years_experience.trim()) {
      const years = Number(candidateForm.years_experience)
      if (!Number.isNaN(years)) payload.years_experience = years
    }

    try {
      setIsSubmittingCandidate(true)
      setCandidateStatus(null)

      const response = await fetch(`${API_BASE_URL}/candidates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = (await response.json()) as CandidateMutationResponse
      setCandidateStatus(`${data.message} (ID: ${data.id})`)
      setCandidateForm(emptyCandidateForm())
    } catch (error) {
      setCandidateStatus(
        error instanceof Error
          ? `Could not create candidate. ${error.message}`
          : 'Unexpected error while creating candidate.',
      )
    } finally {
      setIsSubmittingCandidate(false)
    }
  }

  return (
    <main className="app-layout">
      <nav className="top-nav">
        <div className="top-nav-inner">
          <p className="brand">Candidate DB</p>
          <div className="nav-links" role="tablist" aria-label="App Pages">
            <button
              type="button"
              role="tab"
              aria-selected={activePage === 'assistant'}
              className={activePage === 'assistant' ? 'active' : ''}
              onClick={() => setActivePage('assistant')}
            >
              Assistant
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activePage === 'add'}
              className={activePage === 'add' ? 'active' : ''}
              onClick={() => setActivePage('add')}
            >
              Add Candidate
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activePage === 'manage'}
              className={activePage === 'manage' ? 'active' : ''}
              onClick={() => setActivePage('manage')}
            >
              Manage Candidates
            </button>
          </div>
          <span className="api-pill">API: {API_BASE_URL}</span>
        </div>
      </nav>

      <section className="page-shell">
        {activePage === 'assistant' && (
          <section className="chat-page">
            <header className="chat-header">
              <p className="eyebrow">Candidate DB Assistant</p>
              <h1>Recruiting Chat Console</h1>
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
                          <p>{candidate.role ?? 'Role unavailable'}</p>
                          <ul>
                            <li>Experience: {candidate.years_experience ?? 'N/A'} years</li>
                            <li>Location: {candidate.location ?? 'N/A'}</li>
                            <li>Skills: {candidate.skills ?? 'N/A'}</li>
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
        )}

        {activePage === 'add' && (
          <section className="candidate-form-shell">
            <h2>Add Candidate</h2>
            <form className="candidate-form" onSubmit={submitCandidate}>
              <input
                placeholder="Full name *"
                value={candidateForm.full_name}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, full_name: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Email *"
                value={candidateForm.email}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, email: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Recent role *"
                value={candidateForm.recent_role}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, recent_role: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Location"
                value={candidateForm.location}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, location: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Years experience"
                value={candidateForm.years_experience}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, years_experience: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Skills (comma-separated)"
                value={candidateForm.skills}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, skills: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="GitHub URL"
                value={candidateForm.github_url}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, github_url: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="LinkedIn URL"
                value={candidateForm.linkedin_url}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, linkedin_url: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <input
                placeholder="Website URL"
                value={candidateForm.website_url}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, website_url: event.target.value }))}
                disabled={isSubmittingCandidate}
              />
              <textarea
                placeholder="Summary"
                value={candidateForm.summary}
                onChange={(event) => setCandidateForm((prev) => ({ ...prev, summary: event.target.value }))}
                rows={2}
                disabled={isSubmittingCandidate}
              />
              <button type="submit" disabled={isSubmittingCandidate}>
                {isSubmittingCandidate ? 'Adding...' : 'Add Candidate'}
              </button>
            </form>
            {candidateStatus && <p className="candidate-status">{candidateStatus}</p>}
          </section>
        )}

        {activePage === 'manage' && (
          <section className="candidate-manage-shell">
            <h2>Manage Candidates (Search, Edit, Delete)</h2>

            <form className="candidate-search-form" onSubmit={submitCandidateSearch}>
              <input
                placeholder="Name"
                value={searchFilters.name}
                onChange={(event) => setSearchFilters((prev) => ({ ...prev, name: event.target.value }))}
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Role / Position"
                value={searchFilters.role}
                onChange={(event) => setSearchFilters((prev) => ({ ...prev, role: event.target.value }))}
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Location"
                value={searchFilters.location}
                onChange={(event) => setSearchFilters((prev) => ({ ...prev, location: event.target.value }))}
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Skill"
                value={searchFilters.skill}
                onChange={(event) => setSearchFilters((prev) => ({ ...prev, skill: event.target.value }))}
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Email"
                value={searchFilters.email}
                onChange={(event) => setSearchFilters((prev) => ({ ...prev, email: event.target.value }))}
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Min years"
                value={searchFilters.min_years_experience}
                onChange={(event) =>
                  setSearchFilters((prev) => ({ ...prev, min_years_experience: event.target.value }))
                }
                disabled={isSearchingCandidates}
              />
              <input
                placeholder="Max years"
                value={searchFilters.max_years_experience}
                onChange={(event) =>
                  setSearchFilters((prev) => ({ ...prev, max_years_experience: event.target.value }))
                }
                disabled={isSearchingCandidates}
              />
              <button type="submit" disabled={isSearchingCandidates}>
                {isSearchingCandidates ? 'Searching...' : 'Search Candidates'}
              </button>
            </form>

            {searchStatus && <p className="candidate-status">{searchStatus}</p>}

            {searchResults.length > 0 && (
              <div className="manage-results-grid">
                {searchResults.map((candidate) => (
                  <article key={candidate.id} className="manage-candidate-card">
                    <h3>{candidate.full_name}</h3>
                    <p>{candidate.role}</p>
                    <ul>
                      <li>ID: {candidate.id}</li>
                      <li>Email: {candidate.email}</li>
                      <li>Experience: {candidate.years_experience ?? 'N/A'} years</li>
                      <li>Location: {candidate.location ?? 'N/A'}</li>
                      <li>Skills: {candidate.skills ?? 'N/A'}</li>
                    </ul>
                    <div className="manage-actions">
                      <button type="button" onClick={() => beginEditCandidate(candidate)} disabled={isSavingEdit}>
                        Edit
                      </button>
                      <button
                        type="button"
                        className="danger"
                        onClick={() => deleteCandidate(candidate.id)}
                        disabled={deletingCandidateId === candidate.id}
                      >
                        {deletingCandidateId === candidate.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}

            {editingCandidateId && (
              <form className="candidate-edit-form" onSubmit={submitCandidateEdit}>
                <h3>Editing Candidate: {editingCandidateId}</h3>
                <input
                  placeholder="Full name"
                  value={editForm.full_name}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, full_name: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Email"
                  value={editForm.email}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, email: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Recent role"
                  value={editForm.recent_role}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, recent_role: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Location"
                  value={editForm.location}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, location: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Years experience"
                  value={editForm.years_experience}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, years_experience: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Skills (comma-separated)"
                  value={editForm.skills}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, skills: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="GitHub URL"
                  value={editForm.github_url}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, github_url: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="LinkedIn URL"
                  value={editForm.linkedin_url}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, linkedin_url: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <input
                  placeholder="Website URL"
                  value={editForm.website_url}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, website_url: event.target.value }))}
                  disabled={isSavingEdit}
                />
                <textarea
                  placeholder="Summary"
                  value={editForm.summary}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, summary: event.target.value }))}
                  rows={2}
                  disabled={isSavingEdit}
                />
                <div className="manage-actions">
                  <button type="submit" disabled={isSavingEdit}>
                    {isSavingEdit ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEditingCandidateId(null)
                      setEditStatus(null)
                      setEditForm(emptyCandidateForm())
                    }}
                    disabled={isSavingEdit}
                  >
                    Cancel
                  </button>
                </div>
                {editStatus && <p className="candidate-status">{editStatus}</p>}
              </form>
            )}
          </section>
        )}
      </section>
    </main>
  )
}

export default App

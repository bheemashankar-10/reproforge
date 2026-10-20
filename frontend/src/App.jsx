import { useState } from 'react'
import History from './History'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function post(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`Server returned ${res.status}`)
  return res.json()
}

function splitList(text) {
  return text.split(',').map((s) => s.trim()).filter(Boolean)
}

function Card({ title, children }) {
  return (
    <section className="rounded-xl bg-slate-800/50 border border-slate-700 p-4 space-y-3">
      <h2 className="text-xl font-semibold text-emerald-300">{title}</h2>
      {children}
    </section>
  )
}

function Output({ error, result }) {
  return (
    <>
      {error && <p className="text-red-400">Error: {error}</p>}
      {result && (
        <pre className="rounded-lg bg-slate-900 p-3 text-sm overflow-x-auto whitespace-pre-wrap">
          {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
        </pre>
      )}
    </>
  )
}

function useAction(fn) {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  async function run() {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await fn())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }
  return { result, error, loading, run }
}

const inputClass = 'rounded bg-slate-800 p-2 border border-slate-700 text-sm'
const buttonClass =
  'rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-slate-900 hover:bg-emerald-400 disabled:opacity-50'

export default function App() {
  const [code, setCode] = useState('print(1 / 0)')
  const [timeout, setTimeoutValue] = useState(5)
  const [items, setItems] = useState('A, B, C, D')
  const [required, setRequired] = useState('B, D')
  const [expectedError, setExpectedError] = useState('ZeroDivisionError')

  const reproduce = useAction(() => post('/reproduce', { code, timeout: Number(timeout) }))
  const minimize = useAction(() =>
    post('/minimize', { items: splitList(items), required_items: splitList(required) }),
  )
  const generate = useAction(() => {
    const body = { code }
    if (expectedError.trim()) body.expected_error = expectedError.trim()
    return post('/generate-test', body)
  })

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-3xl mx-auto space-y-5">
        <h1 className="text-3xl font-bold text-emerald-400">ReproForge</h1>
        <p className="text-slate-400">Reproduce bugs, minimize inputs, generate regression tests.</p>

        <Card title="1. Reproduce">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={8}
            className={`${inputClass} w-full font-mono`}
          />
          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-400">Timeout (s)</label>
            <input
              type="number"
              min="1"
              max="10"
              value={timeout}
              onChange={(e) => setTimeoutValue(e.target.value)}
              className={`${inputClass} w-20`}
            />
            <button onClick={reproduce.run} disabled={reproduce.loading} className={buttonClass}>
              {reproduce.loading ? 'Running...' : 'Run'}
            </button>
          </div>
          <Output error={reproduce.error} result={reproduce.result} />
        </Card>

        <Card title="2. Minimize (demo)">
          <p className="text-sm text-slate-400">Comma-separated lists.</p>
          <input value={items} onChange={(e) => setItems(e.target.value)} className={`${inputClass} w-full`} placeholder="items" />
          <input value={required} onChange={(e) => setRequired(e.target.value)} className={`${inputClass} w-full`} placeholder="required items" />
          <button onClick={minimize.run} disabled={minimize.loading} className={buttonClass}>
            {minimize.loading ? 'Working...' : 'Minimize'}
          </button>
          <Output error={minimize.error} result={minimize.result} />
        </Card>

        <Card title="3. Generate regression test">
          <p className="text-sm text-slate-400">Uses the code from box 1.</p>
          <input
            value={expectedError}
            onChange={(e) => setExpectedError(e.target.value)}
            className={`${inputClass} w-full`}
            placeholder="expected error text (optional)"
          />
          <button onClick={generate.run} disabled={generate.loading} className={buttonClass}>
            {generate.loading ? 'Generating...' : 'Generate test'}
          </button>
          <Output error={generate.error} result={generate.result} />
                </Card>

        <History />
      </div>
    </div>
  )
}


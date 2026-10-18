import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export default function App() {
  const [code, setCode] = useState('print(1 / 0)')
  const [timeout, setTimeoutValue] = useState(5)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function runCode() {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/reproduce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, timeout: Number(timeout) }),
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-3xl mx-auto space-y-4">
        <h1 className="text-3xl font-bold text-emerald-400">ReproForge</h1>
        <p className="text-slate-400">Reproduce a bug by running a Python snippet.</p>

        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={10}
          className="w-full rounded-lg bg-slate-800 p-3 font-mono text-sm border border-slate-700"
        />

        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-400">Timeout (s)</label>
          <input
            type="number"
            min="1"
            max="30"
            value={timeout}
            onChange={(e) => setTimeoutValue(e.target.value)}
            className="w-20 rounded bg-slate-800 p-2 border border-slate-700"
          />
          <button
            onClick={runCode}
            disabled={loading}
            className="rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-slate-900 hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run'}
          </button>
        </div>

        {error && <p className="text-red-400">Error: {error}</p>}

        {result && (
          <pre className="rounded-lg bg-slate-800 p-3 text-sm overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}
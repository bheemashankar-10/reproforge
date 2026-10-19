import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function fetchRuns() {
  const res = await fetch(API_URL + '/history', { headers: { 'X-API-Key': import.meta.env.VITE_API_KEY || '' } })
  if (!res.ok) throw new Error('Server returned ' + res.status)
  return res.json()
}

export default function History() {
  const [runs, setRuns] = useState([])
  const [error, setError] = useState('')

  async function load() {
    try {
      setRuns(await fetchRuns())
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    let active = true
    fetchRuns()
      .then((data) => {
        if (active) setRuns(data)
      })
      .catch((e) => {
        if (active) setError(e.message)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <section className="rounded-xl bg-slate-800/50 border border-slate-700 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-emerald-300">4. History</h2>
        <button
          onClick={() => {
            setError('')
            load()
          }}
          className="rounded-lg bg-emerald-500 px-3 py-1 text-sm font-semibold text-slate-900 hover:bg-emerald-400"
        >
          Refresh
        </button>
      </div>
      {error && <p className="text-red-400">Error: {error}</p>}
      {runs.length === 0 && !error && <p className="text-slate-400">No runs yet.</p>}
      <ul className="space-y-2">
        {runs.map((r) => (
          <li key={r.id} className="rounded-lg bg-slate-900 p-3 text-sm">
            <div className="flex justify-between text-slate-400">
              <span className="font-semibold text-emerald-300">{r.kind}</span>
              <span>{new Date(r.created_at).toLocaleString()}</span>
            </div>
            <pre className="mt-2 whitespace-pre-wrap overflow-x-auto">
              {JSON.stringify(r.response, null, 2)}
            </pre>
          </li>
        ))}
      </ul>
    </section>
  )
}

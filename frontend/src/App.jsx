import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [metrics, setMetrics] = useState({ hit_rate: 0, hit_count: 0, miss_count: 0 })

  const fetchMetrics = async () => {
    try {
      const res = await fetch('http://localhost:8000/metrics')
      const data = await res.json()
      setMetrics(data)
    } catch (err) {
      console.error("Failed to fetch metrics", err)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      const data = await res.json()
      setResult(data)
      fetchMetrics()
    } catch (err) {
      alert("Error: Is the backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Sustainable Smart Mobility Assistant</h1>
        <p>AI-Powered Route Planning with Semantic Query Caching</p>
      </header>

      <div className="main-grid">
        <div className="query-section">
          <div className="card">
            <form onSubmit={handleSearch} className="search-box">
              <input 
                type="text" 
                placeholder="Where do you want to go? (e.g., fastest way to downtown)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Thinking...' : 'Search'}
              </button>
            </form>

            {result && (
              <div className="result-card">
                <span className={`badge ${result.cache_status.toLowerCase()}`}>
                  CACHE {result.cache_status}
                </span>
                
                <h2 style={{ marginBottom: '0.5rem', color: 'var(--primary)' }}>
                  {result.response.mode}
                </h2>
                <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                  {result.response.description}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="metric-card">
                    <span className="metric-name">Estimated Time</span>
                    <div className="metric-val">{result.response.estimated_time}</div>
                  </div>
                  <div className="metric-card">
                    <span className="metric-name">Carbon Impact</span>
                    <div className="metric-val" style={{ color: 'var(--accent-green)' }}>
                      {result.response.carbon_footprint}
                    </div>
                  </div>
                </div>

                <div className="stat-group">
                  <div className="stat-item">
                    <span className="stat-label">Similarity</span>
                    <span className="stat-value">{(result.similarity_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Latency</span>
                    <span className="stat-value">{result.total_latency}s</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="metrics-section">
          <div className="card metrics-panel">
            <h2>System Efficiency</h2>
            
            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-name">Cache Hit Rate</span>
                <span className="metric-val">{(metrics.hit_rate * 100).toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${metrics.hit_rate * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-name">Hits / Total</span>
                <span className="metric-val">{metrics.hit_count} / {metrics.hit_count + metrics.miss_count}</span>
              </div>
            </div>

            <div className="metric-card">
               <span className="metric-name">Savings Theory</span>
               <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                 Every Hit reduces LLM cost by ~95% and latency by ~1s.
               </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

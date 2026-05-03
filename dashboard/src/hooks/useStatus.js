import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '../api/client'
const POLL_MS = 5000
export function useStatus(token) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const ref = useRef(null)
  const fetch = useCallback(async () => {
    if (!token) return
    try { setData(await api.status(token)); setError(null); setLastUpdated(new Date()) }
    catch (e) { setError(e.detail || e.message) }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => {
    if (!token) return
    fetch(); ref.current = setInterval(fetch, POLL_MS)
    return () => clearInterval(ref.current)
  }, [fetch, token])
  const refresh = useCallback(() => { setLoading(true); fetch() }, [fetch])
  return { data, error, loading, lastUpdated, refresh }
}
import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
export function useWorlds(token, { includeSize = false } = {}) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const fetch = useCallback(async () => {
    if (!token) return
    setLoading(true)
    try { setData(await api.worlds(token, includeSize)); setError(null) }
    catch (e) { setError(e.detail || e.message) }
    finally { setLoading(false) }
  }, [token, includeSize])
  useEffect(() => { fetch() }, [fetch])
  return { data, error, loading, refresh: fetch }
}
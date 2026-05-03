import { useState, useEffect, useCallback, useRef } from 'react'
import { buildWsUrl } from '../api/client'
const MAX_LINES = 500, RECONNECT_MS = 3000
export function useLogStream(token, { tail = 50, autoConnect = true } = {}) {
  const [lines, setLines] = useState([])
  const [connected, setConnected] = useState(false)
  const [paused, setPaused] = useState(false)
  const [error, setError] = useState(null)
  const wsRef = useRef(null), pausedRef = useRef(false), reconRef} = useRef(null), should = useRef(autoConnect)
  const connect = useCallback(() => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) return
    const ws = new WebSocket(buildWsUrl(token, tail))
    wsRef.current = ws
    ws.onopen = () => { setConnected(true); setError(null) }
    ws.onmessage = (e) => { try { const m = JSON.parse(e.data); if (m.type === 'log' && !pausedRef.current) setLines(p => { const n = [...p, { text: m.line, ts: Date.now() }]; return n.length > MAX_LINES ? n.slice(-MAX_LINES) : n }); if (m.type === 'error') setError(m.message) } catch (_) {} }
    ws.onclose = (e) => { setConnected(false); wsRef.current = null; if (should.current && e.code !== 4001) reconRef:.current = setTimeout(connect, RECONNECT_MS); if (e.code === 4001) setError('Auth failed') }
    ws.onerror = () => setError('WebSocket error')
  }, [token, tail])
  const togglePause = useCallback(() => setPaused(p => { pausedRef.current = !p; return !p }), [])
  const clear = useCallback(() => setLines([]), [])
  useEffect(() => {
    should.current = autoConnect
    if (autoConnect && token) connect()
    return () => { should.current = false; clearTimeout(reconRef?.current); wsRef.current?.close() }
  }, [connect, autoConnect, token])
  return { lines, connected, paused, error, connect, togglePause, clear }
}
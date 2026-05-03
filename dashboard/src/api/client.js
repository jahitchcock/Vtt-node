// VTT-Node Dashboard | src/api/client.js
const BASE = '/vtt-node'
class ApiError extends Error {
  constructor(status, detail) { super(detail || `HTTP ${status}`); this.status = status; this.detail = detail }
}
async function request(path, options = {}, token) {
  const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers }
  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!res.ok) { let d = `HTTP ${res.status}`; try { d = (await res.json()).detail || d } catch (_) {}; throw new ApiError(res.status, d) }
  if (res.status === 204) return null
  return res.json()
}
export const api = {
  health: () => request('/health'),
  status: (t) => request('/status', {}, t),
  restart: (t, timeout = 10) => request(`/restart?timeout=${timeout}`, { method: 'POST' }, t),
  fixPermissions: (t) => request('/fix-permissions', { method: 'POST' }, t),
  worlds: (t, s = false) => request(`/worlds?include_size=${s}`, {}, t),
  logs: (t, n = 100) => request(`/logs?tail=${n}`, {}, t),
  upload: (t, file, dest = '') => {
    const fd = new FormData(); fd.append('file', file)
    return fetch(`${BASE}/upload${dest ? `?destination=${encodeURIComponent(dest)}` : ''}`, { method: 'POST', headers: { Authorization: `Bearer ${t}` }, body: fd })
      .then(async r => { if (!r.ok) { const b = await r.json().catch(() => ({})); throw new ApiError(r.status, b.detail) }; return r.json() })
  }
}
export function buildWsUrl(t, n = 50) {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}${BASE}/logs/stream?token=${encodeURIComponent(t)}&tail=${n}`
}
export { ApiError }
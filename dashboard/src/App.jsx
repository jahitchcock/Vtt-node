// =============================================================================
// VTT-Node Dashboard | src/App.jsx
// Root component — auth gate → dashboard
// Layout: header + 2-column responsive grid
// =============================================================================

import { useState } from 'react'
import AuthGate       from './components/AuthGate'
import StatusHeader   from './components/StatusHeader'
import StatsPanel     from './components/StatsPanel'
import ActionBar      from './components/ActionBar'
import LogTerminal    from './components/LogTerminal'
import WorldBrowser   from './components/WorldBrowser'
import AssetUploader  from './components/AssetUploader'
import { useStatus }  from './hooks/useStatus'

function Dashboard({ token, onLogout }) {
  const { data, error, loading, lastUpdated, refresh } = useStatus(token)
  const engine = data?.container?.engine ?? 'foundry'

  return (
    <div className="min-h-screen flex flex-col p-4 gap-4 max-w-6xl mx-auto">
      <div className="ambient-bg" />
      <StatusHeader
        data={data}
        loading={loading}
        lastUpdated={lastUpdated}
        onRefresh={refresh}
        onLogout={onLogout}
      />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1">
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4">
            <StatsPanel stats={data?.stats} error={data?.error} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ActionBar token={token} engine={engine} />
          </div>
          <AssetUploader token={token} engine={engine} />
        </div>
        <div className="flex flex-col gap-4">
          <LogTerminal token={token} />
          <WorldBrowser token={token} />
        </div>
      </div>
      <footer className="text-center text-xs text-slate-700 pb-2 font-body">
        VTT-Node v0.3.0 — Storyteller Dashboard
      </footer>
    </div>
  )
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem('vtt-token') || null)
  function handleAuth(t) { setToken(t) }
  function handleLogout() { sessionStorage.removeItem('vtt-token'); setToken(null) }
  if (!token) return <AuthGate onAuth={handleAuth} />
  return <Dashboard token={token} onLogout={handleLogout} />
}

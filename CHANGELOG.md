# Changelog

All notable changes to VTT-Node will be documented here.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

### In Progress
- Phase 3: React management dashboard
- Phase 4: Sigil Rescue migration wizard

---

## [0.2.0] — 2026-05-01 — Phase 2: Management Backend

### Added
- FastAPI management backend (`vtt-ui/`)
- `GET /health` - `GET /status` - `POST /restart` - `POST /fix-permissions`
- `POST /upload` - `GET /worlds` - `GET /logs` - `WS /logs/stream`
- Bearer token auth with constant-time comparison
- Pydantic v2 response schemas
- OpenAPI docs at `/vtt-node/docs`

### Fixed (code review)
- `auth.py`: `secrets.compare_digest()` - timing-attack resistant
- `logs.py`: `asyncio.Queue` + `ThreadPoolExecutor` - blocking iterator off event loop
- `docker_client.py`: raises `RuntimeError` on socket failure
- `files.py`: `Path.relative_to()` for path traversal
- `control.py`: async subprocess, preserves `.sh` executability
- `nginx.conf`: rate limit 30r/m → 10r/s
- `entrypoint.sh`: bash array args - safe for spaces in names

---

## [0.1.0] —  2026-05-01 - Phase 1: Core Infrastructure

### Added
- `docker-compose.yml` - shared services: Nginx, Cloudflare, vtt-ui, backup
- `engines/foundry.yml` - Foundry VTT overlay
- `engines/maptool.yml` + `maptool-docker/` - MapTool headless
- `nginx/` - WebSocket, 500MB uploads, rate limiting
- `bootstrap.sh` - interactive setup wizard
- `.env.example` - fully documented
- Nightly encrypted backups via offen/docker-volume-backup

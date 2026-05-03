# VTT-Node | routers/logs.py - POST-review version
import asyncio
import docker.errors
import concurrent.futures
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from core.auth import require_api_key
from core.config import settings
from core.docker_client import docker_client
router = APIRouter()

@router.get("/logs", dependencies=[Depends(require_api_key)])
async def get_logs(tail: int = Query(default=100, ge=1, le=5000)):
    try:
        container = docker_client.get_vtt_container()
        raw = container.logs(tail=tail, timestamps=True)
        lines = raw.decode("utf-8", errors="replace").splitlines()
        return {"container": settings.container_name, "lines": lines, "count": len(lines)}
    except docker.errors.NotFound: raise HTTPException(404, f"Container not found")
    except Exception as e: raise HTTPException(503, f"Log fetch failed: {e}")

@router.websocket("/logs/stream")
async def stream_logs(websocket: WebSocket, tail: int = Query(default=50), token: str = Query(default="")):
    import secrets as _secrets
    from core.config import settings as cfg
    if not token or not _secrets.compare_digest(token, cfg.api_secret):
        await websocket.close(code=4001, reason="Unauthorized")
        return
    await websocket.accept()
    try: container = docker_client.get_vtt_container()
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close(); return
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    _SENTINEL = object()
    def _producer():
        try:
            for raw_line in container.logs(stream=True, follow=True, tail=tail, timestamps=True):
                loop.call_soon_threadsafe(queue.put_nowait, raw_line.decode("utf-8", errors="replace").rstrip())
        except Exception as exc: loop.call_soon_threadsafe(queue.put_nowait, exc)
        finally: loop.call_soon_threadsafe(queue.put_nowait, _SENTINEL)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, _producer)
    try:
        while True:
            item = await queue.get()
            if item is _SENTINEL: break
            if isinstance(item, Exception): await websocket.send_json({"type": "error", "message": str(item)}); break
            await websocket.send_json({"type": "log", "line": item})
    except WebSocketDisconnect: pass
    finally: executor.shutdown(wait=False); await websocket.close()
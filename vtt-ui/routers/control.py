# VTT-Node | routers/control.py
import asyncio
import docker.errors
from fastapi import APIRouter, Depends, HTTPException, Query
from core.auth import require_api_key
from core.config import settings
from core.docker_client import docker_client
from models.schemas import RestartResponse
router = APIRouter()

@router.post("/restart", response_model=RestartResponse, dependencies=[Depends(require_api_key)])
async def restart_engine(timeout: int = Query(default=10, ge=1, le=60)):
    try:
        docker_client.restart_container(timeout=timeout)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container '{settings.container_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restart failed: {e}")
    return RestartResponse(success=True, message=f"Restarted (timeout={timeout}s)", container=settings.container_name)

@router.post("/fix-permissions", dependencies=[Depends(require_api_key)])
async def fix_permissions():
    data_path = settings.vtt_data_path
    async def _run(cmd):
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        return proc.returncode, stderr.decode()
    try:
        rc, err = await _run(["find", data_path, "-type", "d", "-exec", "chmod", "755", "{}", "+"])
        if rc != 0: raise HTTPException(500, f"chmod dirs failed: {err}")
        rc, err = await _run(["find", data_path, "-type", "f", "!", "-name", "*.sh", "-exec", "chmod", "644", "{}", "+"])
        if rc != 0: raise HTTPException(500, f"chmod files failed: {err}")
        rc, err = await _run(["find", data_path, "-name", "*.sh", "-exec", "chmod", "755", "{}", "+"])
        if rc != 0: raise HTTPException(500, f"chmod scripts failed: {err}")
        return {"success": True, "message": f"Permissions fixed on {data_path}"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, f"Permission fix failed: {e}")
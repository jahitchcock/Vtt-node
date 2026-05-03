# VTT-Node | routers/files.py - Post-review version
import tempfile, zipfile
from pathlib import Path
import magic
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from core.auth import require_api_key
from core.config import settings
from models.schemas import UploadResponse, WorldEntry, WorldsResponse
router = APIRouter()
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
ALLOWED_MIME_TYPES = {"application/zip", "application/x-zip", "application/x-zip-compressed", "application/octet-stream"}

def _dir_size_mb(path): return round(sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 ** 2), 2)

@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(require_api_key)])
async def upload_asset(file: UploadFile = File(...), destination: str = Query(default="")):
    if not file.filename or not file.filename.endswith(".zip"): raise HTTPException(400, "Only .zip files are accepted.")
    base_path = Path(settings.upload_path).resolve()
    if destination:
        dest_path = (base_path / destination).resolve()
        try: dest_path.relative_to(base_path)
        except ValueError: raise HTTPException(400, "Invalid destination path.")
    else: dest_path = base_path
    dest_path.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = Path(tmp.name); bytes_written = 0
        try:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk: break
                bytes_written += len(chunk)
                if bytes_written > MAX_UPLOAD_BYTES: tmp_path.unlink(missing_ok=True); raise HTTPException(413, "File exceeds 500MB limit")
                tmp.write(chunk)
        except HTTPException: raise
        except Exception as e: tmp_path.unlink(missing_ok=True); raise HTTPException(500, f"Upload error: {e}")
    mime = magic.from_file(str(tmp_path), mime=True)
    if mime not in ALLOWED_MIME_TYPES: tmp_path.unlink(missing_ok=True); raise HTTPException(400, f"Type '{mime}' not allowed")
    try:
        with zipfile.ZipFile(tmp_path, "r") as zf:
            for member in zf.namelist():
                try: (dest_path / member).resolve().relative_to(dest_path)
                except ValueError: tmp_path.unlink(missing_ok=True); raise HTTPException(400, f"Unsafe ZIP path: {member}")
            zf.extractall(dest_path); count = len(zf.namelist())
    except zipfile.BadZipFile: tmp_path.unlink(missing_ok=True); raise HTTPException(400, "Invalid ZIP")
    finally: tmp_path.unlink(missing_ok=True)
    return UploadResponse(success=True, filename=file.filename, extracted_to=str(dest_path), files_extracted=count, message=f"Extracted {count} files")

@router.get("/worlds", response_model=WorldsResponse, dependencies=[Depends(require_api_key)])
async def list_worlds(include_size: bool = Query(default=False)):
    worlds_path = Path(settings.worlds_path)
    if not worlds_path.exists(): return WorldsResponse(engine=settings.vtt_engine, worlds_path=str(worlds_path), worlds=[], count=0)
    worlds = [WorldEntry(name=e.name, path=str(e), size_mb=_dir_size_mb(e) if include_size else None) for e in sorted(worlds_path.iterdir()) if e.is_dir()]
    return WorldsResponse(engine=settings.vtt_engine, worlds_path=str(worlds_path), worlds=worlds, count=len(worlds))
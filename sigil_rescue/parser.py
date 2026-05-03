# VTT-Node | sigil_rescue/parser.py - Sigil JSON parser
# Handles: official Sigil format, community-reverse-engineered format, ZIP archives

from __future__ import annotations
import json, zipfile, io
from pathlib import Path
from typing import Union
from pydantic import ValidationError
from .models import SigilScene

class SigilParseError(Exception):
    pass

def _find_scene_json(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        candidates = [n for n in names if Path(n).name in {"scene.json", "export.json"}] + \
                      [n for n in names if n.endswith(".scene") or n.endswith(".sigil")] + \
                      [n for n in names if n.endswith(".json") and "/" not in n.strip("/")]
        if not candidates: raise SigilParseError(f"No scene file found in ZIP. Found: {names[:10]}")
        return zf.read(candidates[0])

def _normalize_raw(data):
    if "scene" in data and isinstance(data["scene"], dict): data = data["scene"]
    for k1, k2 in [("mapWidth","width"),("mapHeight","height"),("gridSize","grid_size"),("sceneName","name")]:
        if k1 in data: data.setdefault(k2, data.pop(k1))
    for wk in ("wallData","wall_data","mapWalls"):
        if wk in data: data.setdefault("walls", data.pop(wk))
    for lk in ("lightData","light_data","mapLights","lightsources"):
        if lk in data: data.setdefault("lights", data.pop(lk))
    walls = []
    for w in data.get("walls", []):
        if isinstance(w, dict):
            if "x1" in w and "start" not in w:
                w["start"] = {"x": w.pop("x1"), "y": w.pop("y1"), "z": w.pop("z1", 0)}
                w["end"] = {"x": w.pop("x2"), "y": w.pop("y2"), "z": w.pop("z2", 0)}
            elif "coords" in w:
                c = w.pop("coords")
                w["start"] = {"x": c[0], "y": c[1], "z": c[2] if len(c)>2 else 0}
                w["end"] = {"x": c[3], "y": c[4], "z": c[5] if len(c)>5 else 0}
            walls.append(w)
    data["walls"] = walls
    lights = []
    for l in data.get("lights", []):
        if isinstance(l, dict):
            if "x" in l and "position" not in l:
                l["position"] = {"x": l.pop("x"), "y": l.pop("y"), "z": l.pop("z", 0)}
            if "r" in l and "radius" not in l: l["radius"] = l.pop("r")
            for ck in ("col","colour","hex"):
                if ck in l and "color" not in l: l["color"] = l.pop(ck)
            lights.append(l)
    data["lights"] = lights
    return data

def parse_bytes(content, filename="unknown"):
    is_zip = content[:4] == b"PK\x03\x04" or filename.lower().endswith(".zip")
    if is_zip:
        try: content = _find_scene_json(content)
        except zipfile.BadZipFile: raise SigilParseError("Invalid ZIP file.")
    try: raw = json.loads(content)
    except json.JSONDecodeError as e: raise SigilParseError(f"Invalid JSON: {e}")
    if not isinstance(raw, dict): raise SigilParseError("Expected JSON object at root")
    normalized = _normalize_raw(raw)
    try: scene = SigilScene.model_validate(normalized)
    except ValidationError as e:
        errs = e.errors(include_url=False)
        raise SigilParseError(f"Schema error: {'; '.join({'.'.join(str(l) for l in e['loc']) for e in errs[:3]})}")
    if not scene.walls and not scene.lights:
        raise SigilParseError("Scene contains no walls or lights - may be empty or unsupported")
    return scene

def parse_file(path):
    p = Path(path)
    if not p.exists(): raise SigilParseError(f"File not found: {path}")
    return parse_bytes(p.read_bytes(), filename=p.name)

def generate_sample_export(name="Sample Tavern"):
    return {"version": "1.0", "scene": {"name": name, "width": 1400, "height": 1000, "depth": 300, "grid_size": 100, "background_image": None, "walls": [{"id": "w001", "start": {"x": 100, "y": 100, "z": 0}, "end": {"x": 1300, "y": 100, "z": 0}, "height": 200}, {"id": "w002", "start": {"x": 1300, "y": 100, "z": 0}, "end": {"x": 1300, "y": 900, "z": 0}, "height": 200}, {"id": "w003", "start": {"x": 1300, "y": 900, "z": 0}, "end": {"x": 100, "y": 900, "z": 0}, "height": 200}, {"id": "w004", "start": {"x": 100, "y": 900, "z": 0}, "end": {"x": 100, "y": 100, "z": 0}, "height": 200}, {"id": "w005", "start": {"x": 100, "y": 400, "z": 0}, "end": {"x": 100, "y": 500, "z": 0}, "height": 200, "type": "door", "is_door": true, "blocks_vision": false}, {"id": "w6", "start": {"x": 300, "y": 100, "z": 250}, "end": {"x": 300, "y": 900, "z": 250}, "height": 50}], "lights": [{"id": "l001", "position": {"x": 300, "y": 500, "z": 10}, "radius": 250, "bright": 0.4, "color": "#ff8844", "intensity": 0.9}, {"id": "l002", "position": {"x": 1100, "y": 700, "z": 200}, "radius": 200, "bright": 0.3, "color": "#ffd080", "intensity": 0.6}]}}
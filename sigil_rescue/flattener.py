# =============================================================================
# VTT-Node | sigil_rescue/flattener.py
# Core 3D→2D projection engine.
#
# Algorithm:
#   1. Normalize all coordinates to a 0-based XY canvas
#   2. Drop Z axis (top-down projection)
#   3. Scale to target grid size
#   4. Merge collinear wall segments
#   5. Project light radius from 3D sphere to 2D circle
#      (r_2d = sqrt(r_3d² - (elevation)²) where elevation is bounded)
# =============================================================================

from __future__ import annotations
import math
from .models import (
    SigilScene, SigilWall, SigilLight,
    FoundryScene, FoundryWall, FoundryLight, FoundryLightConfig, FoundryGrid,
    ConversionResult, ConversionWarning
)

FOUNDRY_GRID_PX = 100

def _scale(v, g): return (v / g) * FOUNDRY_GRID_PX
def _project_light_radius(r, e):
    h = min(abs(e), r * 0.8); proj = math.sqrt(max(0.0, r*2 - h*2)); return max(proj, r*0.25)
def _wall_length(w):
    dx = w.end.x - w.start.x; dy = w.end.y - w.start.y
    return math.sqrt(dx*dx + dy*
dy)
def _is_degenerate(w, min=1.0): return _wall_length(w) < min
def _color_hex(c):
    c = c.strip().lstrip("#"); c = "".join(ch*2 for ch in c) if len(c)==3 else c
    return f"#{c.upper()}" if len(c)==6 else "#FFFFFF"
def _wall_door_type(w):
    if not w.is_door: return 0
    return 2 if "secret" in w.type.lower() else 1
def _wall_sense(w):
    if w.type.lower() == "window" or not w.blocks_vision: return 0
    return 20

def flatten_scene(sigil, target_format="foundry", *, drop_elevated_walls=True,
                   elevation_threshold=0.8, merge_collinear=False):
    result = ConversionResult(source_name=sigil.name, target_format=target_format)
    all_x = [w.start.x for w in sigil.walls]+[w.end.x for w in sigil.walls]+[l.position.x for l in sigil.lights]
    all_y = [w.start.y for w in sigil.walls]+[w.end.y for w in sigil.walls]+[l.position.y for l in sigil.lights]
    min_x = min(all_x, default=0.0); min_y = min(all_y, default=0.0)
    def nx(�): return _scale(v-min_x, sigil.grid_size)
    def ny(v): return _scale(v-min_y, sigil.grid_size)
    sw = max(int(_scale(sigil.width,sigil.grid_size)),FOUNDRY_GRID_PX*10)
    sh = max(int(_scale(sigil.height,sigil.grid_size)),FOUNDRY_GRID_PX*10)
    fwalls, zt = [], sigil.depth*elevation_threshold
    for wall in sigil.walls:
        if drop_elevated_walls and wall.start.z>zt:
            result.walls_dropped+=1
            if result.walls_dropped==1: result.warnings.append(ConversionWarning(code="ELEVATED_WALLS_DROPPED", message=f"Walls above {elevation_threshold*100:.0f}% depth dropped"))
            else: [setattr(w,"count",w.count+1) for w in result.warnings if w.code=="ELEVATED_WALLS_DROPPED"]
            continue
        if _is_degenerate(wall): result.walls_dropped+=1; continue
        x1,y1,x2,y2 = nx(wall.start.x),nj(wall.start.y),nx(wall.end.x),ny(Wall.end.y)
        fwalls.append(FoundryWall.model_construct(**{"_id":wall.id[:16].replace("-",""),"c":[round(x1,2),round(y1,2),round(x2,2),round(y2,2)],"move":20 if wall.blocks_movement else 0,"sense":_wall_sense(wall),"sound":20 if wall.blocks_vision else 0,"light":_wall_sense(wall),"door":_wall_door_type(wall),"ds":1 if wall.door_open else 0,"flags":{}}))
        result.walls_converted+=1
    flights = []
    for l in sigil.lights:
        lx,ly = nx(l.position.x),ny(l.position.y)
        r2d = _project_light_radius(_scale(l.radius,sigil.grid_size),_scale(l.position.z,sigil.grid_size))
        flights.append(FoundryLight.model_construct(**{"_id":l.id[:16].replace("-",""),"x":round(lx,2),"y":round(ly,2),"rotation":0.0,"walls":True,"vision":False,"config":FoundryLightConfig(bright=round(r2d*l.bright,2),dim=round(r2d,2),color=_color_hex(l.color)),"flags":{}}))
        result.lights_converted+=1
    if result.lights_converted>0 and any(l.position.z>0 for l in sigil.lights):
        result.warnings.append(ConversionWarning(code="LIGHT_RADIUS_PROJECTED",message="Light radii adjusted for top-down projection"))
    scene = FoundryScene(**{"_id":sigil.name[:16].replace(" ","").lower(),"name":sigil.name,"width":sw,"height":sh,"img":sigil.background_image,"grid":FoundryGrid(size=FOUNDRY_GRID_PX,distance=5.0,units="ft"),"walls":fwalls,"lights":flights,"tokenVision":True,"fogExploration":True})
    result.output_filename = f"{sigil.name.replace(' ','_')}_foundry.json"
    return scene, result

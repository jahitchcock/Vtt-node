# =============================================================================
# VTT-Node | sigil_rescue/foundry_export.py
# Serializes a FoundryScene to the JSON format Foundry VTT v12 expects.
from __future__ import annotations
import json
from .models import FoundryScene

def to_foundry_json(scene: FoundryScene, pretty: bool = True) -> str:
    data = scene.model_dump(by_alias=True, exclude_none=True)
    walls_out = [{"_id":w["_id"],"c":[round(v,1) for v in w["c"]],"move":w.get("move",20),"sense":w.get("sense",20),"sound":w.get("sound",20),"light":w.get("light",20),"door":w.get("door",0),"ds":w.get("ds",0),"flags":w.get("flags",{})} for w in data.get("walls",[])]
    data["walls"] = walls_out
    lights_out = []
    for l in data.get("lights", []):
        cfg = l.get("config",{})
        lights_out.append({"_id":l["_id"],"x":round(l["x"],1),"y":round(l["y"],1),"rotation":l.get("rotation",0.0),"walls":l.get("walls",True),"vision":l.get("vision",False),"config":{"alpha":cfg.get("alpha",0.5),"angle":cfg.get("angle",360),"bright":round(cfg.get("bright",0),1),"color":cfg.get("color"),"coloration":cfg.get("coloration",1),"dim":round(cfg.get("dim",0),1),"attenuation":cfg.get("attenuation",0.5),"luminosity":cfg.get("luminosity",0.5),"saturation":cfg.get("saturation",0.0),"contrast":cfg.get("contrast",0.0),"shadows":cfg.get("shadows",0.0),"animation":{"type":None,"speed":5,"intensity":5},"darkness":{"min":0,"max":1}},"flags":l.get("flags",{})})
    data["lights"] = lights_out
    if "grid" in data: data["grid"] = {k:val for k,val in data["grid"].items() if val is not None}
    for key in ("drawings","tokens","notes","sounds","templates","tiles","region"): data.setdefault(key,[])
    return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)

def write_foundry_json(scene, path):
    with open(path,"w",encoding="utf-8") as f: f.write(to_foundry_json(scene))

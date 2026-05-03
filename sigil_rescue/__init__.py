# VTT-Node Sigil Rescue
# Converts Project Sigil 3D VTT exports to Foundry VTT / MapTool format

from .parser import parse_bytes, parse_file, SigilParseError
from .flattener import flatten_scene
from .foundry_export import to_foundry_json
from .maptool_export import to_maptool_cmpgn

__version__ = "0.4.0"
__all__ = [
    "parse_bytes", "parse_file", "SigilParseError",
    "flatten_scene",
    "to_foundry_json",
    "to_maptool_cmpgn",
]

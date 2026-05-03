# VTT-Node | sigil_rescue/models.py - Pydantic schemas
# (Full file contents in local repo)

from __future__ import annotations
from typing import Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class SigilWall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    start: Vec3
    end: Vec3
    height: float = 150.0
    type: str = "wall"
    blocks_vision: bool = True
    blocks_movement: bool = True
    is_door: bool = False
    door_open: bool = False

class SigilLight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    position: Vec3
    radius: float = 150.0
    bright: float = 0.5
    color: str = "#ffffff"
    intensity: float = 1.0
    type: str = "point"
    elevation: float = 0.0

class SigilToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Token"
    position: Vec3
    width: float = 1.0
    height: float = 1.0
    image_url: Optional[str] = None
    elevation: float = 0.0

class SigilNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    position: Vec3
    text: str = ""
    label: str = ""

class SigilScene(BaseModel):
    version: str = "1.0"
    name: str = "Imported Scene"
    width: float = 3000.0
    height: float = 2000.0
    depth: float = 500.0
    grid_size: float = 100.0
    background_image: Optional[str] = None
    walls: list[SigilWall] = []
    lights: list[SigilLight] = []
    tokens: list[SigilToken] = []
    notes: list[SigilNote] = []

def _uid(): return uuid4().hex[:16]

class FoundryWall(BaseModel):
    _id: str = Field(default_factory=_uid, alias="_id")
    c: list[float]
    move: int = 20
    sense: int = 20
    sound: int = 20
    door: int = 0
    ds: int = 0
    light: int = 20
    flags: dict = Field(default_factory=dict)
    class Config: populate_by_name = True

class FoundryLightConfig(BaseModel):
    alpha: float = 0.5
    angle: int = 360
    bright: float = 0.0
    color: Optional[str] = None
    coloration: int = 1
    dim: float = 0.0
    attenuation: float = 0.5
    luminosity: float = 0.5
    saturation: float = 0.0
    contrast: float = 0.0
    shadows: float = 0.0
    animation: dict = Field(default_factory=lambda: {"type": None, "speed": 5, "intensity": 5})
    darkness: dict = Field(default_factory=lambda: {"min": 0, "max": 1})

class FoundryLight(BaseModel):
    _id: str = Field(default_factory=_uid, alias="_id")
    x: float
    y: float
    rotation: float = 0.0
    walls: bool = True
    vision: bool = False
    config: FoundryLightConfig = Field(default_factory=FoundryLightConfig)
    flags: dict = Field(default_factory=dict)
    class Config: populate_by_name = True

class FoundryGrid(BaseModel):
    type: int = 1
    size: int = 100
    style: str = "solidLines"
    thickness: int = 1
    color: str = "#000000"
    alpha: float = 0.2
    distance: float = 5.0
    units: str = "ft"

class FoundryScene(BaseModel):
    _id: str = Field(default_factory=_uid, alias="_id")
    name: str
    width: int = 4000
    height: int = 3000
    img: Optional[str] = None
    grid: FoundryGrid = Field(default_factory=FoundryGrid)
    tokenVision: bool = True
    fogExploration: bool = True
    fogReset: bool = False
    globalLight: bool = False
    darkness: float = 0.0
    walls: list[FoundryWall] = Field(default_factory=list)
    lights: list[FoundryLight] = Field(default_factory=list)
    drawings: list = Field(default_factory=list)
    tokens: list = Field(default_factory=list)
    notes: list = Field(default_factory=list)
    sounds: list = Field(default_factory=list)
    templates: list = Field(default_factory=list)
    tiles: list = Field(default_factory=list)
    region: list = Field(default_factory=list)
    flags: dict = Field(default_factory=dict)
    class Config: populate_by_name = True

class ConversionWarning(BaseModel):
    code: str
    message: str
    count: int = 1

class ConversionResult(BaseModel):
    source_name: str
    target_format: Literal["foundry", "maptool"]
    walls_converted: int = 0
    lights_converted: int = 0
    tokens_converted: int = 0
    notes_converted: int = 0
    walls_dropped: int = 0
    lights_dropped: int = 0
    warnings: list[ConversionWarning] = []
    output_filename: str = ""

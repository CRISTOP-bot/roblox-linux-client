from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Experience:
    place_id: str
    uri: str
    name: str = "Experiencia de Roblox"
    description: str = ""
    fetched: bool = False

@dataclass(frozen=True)
class RuntimeInfo:
    name: str
    app_id: str
    version: str
    installed: bool

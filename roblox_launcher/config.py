from __future__ import annotations
import json
from pathlib import Path
from .models import Experience

class Config:
    def __init__(self):
        self.path = Path.home()/".config"/"roblox-launcher"/"config.json"
        self.data = {"recent": [], "favorites": []}
        try: self.data.update(json.loads(self.path.read_text()))
        except (OSError, ValueError): pass
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True); self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
    def add_recent(self, exp: Experience):
        items = [x for x in self.data["recent"] if x.get("place_id") != exp.place_id]
        items.insert(0, {"place_id": exp.place_id, "name": exp.name}); self.data["recent"] = items[:10]; self.save()
    def is_favorite(self, place_id): return any(x.get("place_id") == place_id for x in self.data["favorites"])
    def toggle_favorite(self, exp):
        if self.is_favorite(exp.place_id): self.data["favorites"] = [x for x in self.data["favorites"] if x.get("place_id") != exp.place_id]
        else: self.data["favorites"].insert(0, {"place_id": exp.place_id, "name": exp.name})
        self.save()

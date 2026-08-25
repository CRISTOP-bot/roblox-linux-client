from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from .models import Experience, Favorite, HistoryItem, now_iso

class Config:
    """JSON storage with migration from the original {recent, favorites} format."""
    def __init__(self, path: Path | None = None):
        self.path = path or Path.home() / ".config/roblox-launcher/config.json"
        self.data = {"version": 1, "favorites": [], "history": []}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self.data["favorites"] = raw.get("favorites", [])
                self.data["history"] = raw.get("history", raw.get("recent", []))
        except (OSError, json.JSONDecodeError):
            pass
        self._normalise()

    def _normalise(self):
        self.data["favorites"] = [x for x in self.data["favorites"] if isinstance(x, dict) and x.get("place_id")]
        self.data["history"] = [x for x in self.data["history"] if isinstance(x, dict) and x.get("place_id")]
        for x in self.data["history"]:
            x.setdefault("url", f"roblox://placeId={x['place_id']}")
            x.setdefault("name", "Experiencia de Roblox"); x.setdefault("last_played", now_iso()); x.setdefault("launches", 1)
        for x in self.data["favorites"]:
            x.setdefault("url", f"roblox://placeId={x['place_id']}"); x.setdefault("name", "Experiencia de Roblox")
            x.setdefault("added_at", now_iso()); x.setdefault("last_played", None)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_history(self, exp: Experience):
        found = next((x for x in self.data["history"] if x["place_id"] == exp.place_id), None)
        if found:
            found.update(name=exp.name, url=exp.url, last_played=now_iso(), launches=found.get("launches", 0) + 1)
            if exp.thumbnail_url: found["thumbnail_url"] = exp.thumbnail_url
            item = found; self.data["history"].remove(found)
        else:
            item = asdict(HistoryItem(exp.place_id, exp.name, exp.url, thumbnail_url=exp.thumbnail_url))
        self.data["history"].insert(0, item); self.data["history"] = self.data["history"][:50]
        for fav in self.data["favorites"]:
            if fav["place_id"] == exp.place_id: fav["last_played"] = item["last_played"]
        self.save()

    def toggle_favorite(self, exp: Experience) -> bool:
        old = next((x for x in self.data["favorites"] if x["place_id"] == exp.place_id), None)
        if old: self.data["favorites"].remove(old); result = False
        else:
            self.data["favorites"].insert(0, asdict(Favorite(exp.place_id, exp.name, exp.url, thumbnail_url=exp.thumbnail_url))); result = True
        self.save(); return result

    def remove_favorite(self, place_id: str):
        self.data["favorites"] = [x for x in self.data["favorites"] if x["place_id"] != place_id]; self.save()
    def clear_history(self): self.data["history"] = []; self.save()
    def is_favorite(self, place_id: str) -> bool: return any(x["place_id"] == place_id for x in self.data["favorites"])

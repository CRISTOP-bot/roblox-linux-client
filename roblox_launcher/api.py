from __future__ import annotations
import json, logging
from urllib.request import Request, urlopen
from .models import Experience
log = logging.getLogger(__name__)

def fetch_experience(place_id: str, uri: str) -> Experience:
    # Best effort only. No login or credentials are used.
    endpoint = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    try:
        with urlopen(Request(endpoint, headers={"User-Agent": "roblox-linux-launcher/0.3"}), timeout=5) as r:
            universe_id = json.load(r)["universeId"]
        with urlopen(Request(f"https://games.roblox.com/v1/games?universeIds={universe_id}", headers={"User-Agent": "roblox-linux-launcher/0.3"}), timeout=5) as r:
            item = json.load(r).get("data", [{}])[0]
        return Experience(place_id, uri, item.get("name") or "Experiencia de Roblox", item.get("description") or "", True)
    except Exception as exc:
        log.debug("No se pudo obtener información del juego: %s", exc)
        return Experience(place_id, uri)

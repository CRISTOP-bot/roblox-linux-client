from __future__ import annotations
import re
from urllib.parse import parse_qs, urlsplit
PLACE_RE = re.compile(r"^[1-9][0-9]{0,19}$")

def experience_uri(place_id: str) -> str:
    if not PLACE_RE.fullmatch(place_id): raise ValueError("El Place ID debe ser un número entero positivo.")
    return f"roblox://experiences/start?placeId={place_id}"

def parse_target(place: str|None, uri: str|None) -> tuple[str, str]:
    if place and uri: raise ValueError("Usa --place o --uri, no ambos.")
    if place: return place, experience_uri(place)
    if not uri: return "", "roblox://"
    parts = urlsplit(uri)
    if parts.scheme.lower() in {"http", "https"}:
        match = re.search(r"/games/(\\d+)", parts.path)
        if match: return match.group(1), experience_uri(match.group(1))
        raise ValueError("La URL web no contiene un ID de experiencia válido.")
    if parts.scheme.lower() != "roblox": raise ValueError("La URL debe usar roblox:// o una URL de experiencia de Roblox.")
    query = parse_qs(parts.query)
    value = (query.get("placeId") or query.get("placeid") or [None])[0]
    if value is None and parts.netloc.startswith("placeId="): value = parts.netloc.split("=", 1)[1]
    if value is None: raise ValueError("La URL no contiene un placeId válido.")
    return value, experience_uri(value)

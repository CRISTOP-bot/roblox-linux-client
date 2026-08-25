from __future__ import annotations
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

def cached_thumbnail(url: str | None, cache_dir: Path | None = None) -> Path | None:
    if not url: return None
    directory = cache_dir or Path.home()/".cache/roblox-launcher/thumbnails"; directory.mkdir(parents=True, exist_ok=True)
    path = directory/(hashlib.sha256(url.encode()).hexdigest()+".png")
    if path.exists() and path.stat().st_size <= 512_000: return path
    try:
        with urlopen(Request(url, headers={"User-Agent":"roblox-linux-launcher/0.4"}), timeout=5) as r:
            data = r.read(512_001)
        if len(data) > 512_000: return None
        path.write_bytes(data); return path
    except Exception: return None

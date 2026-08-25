from __future__ import annotations
import argparse, logging
from .config import Config
from .launcher import parse_target
from .models import Experience
from .runtime import RuntimeManager
VERSION = "2.0.0"

def main(argv=None):
    p=argparse.ArgumentParser(description="Frontend comunitario de Roblox para Linux mediante Sober")
    g=p.add_mutually_exclusive_group(); g.add_argument("--place"); g.add_argument("--uri"); g.add_argument("--favorite", metavar="PLACE_ID", help="añade o quita un favorito")
    p.add_argument("--history", action="store_true", help="muestra el historial y termina")
    p.add_argument("--diagnose", action="store_true", help="muestra diagnóstico detallado")
    p.add_argument("--detect", action="store_true"); p.add_argument("--verbose", action="store_true"); p.add_argument("--version", action="version", version=VERSION)
    a=p.parse_args(argv); logging.basicConfig(level=logging.DEBUG if a.verbose else logging.WARNING)
    manager=RuntimeManager()
    if a.history:
        for x in Config().data["history"]: print(f"{x.get('name')} · {x['place_id']} · {x.get('launches',1)} inicio(s)")
        return 0
    if a.detect or a.diagnose:
        runtime, info=manager.detect(); print(f"Flatpak: {'✓' if info.flatpak_available else '✗'}"); print(f"Sober: {'✓' if info.installed else '✗'}"); print(f"Sober ID: {info.app_id}"); print(f"Versión: {info.version or 'desconocida'}"); print(f"Runtime disponible: {'✓' if runtime else '✗'}"); return 0 if runtime else 3
    try: place, uri = parse_target(a.place or a.favorite, a.uri)
    except ValueError as e: p.error(str(e))
    if a.favorite:
        exp=Experience(place, uri); added=Config().toggle_favorite(exp); print("Favorito añadido." if added else "Favorito eliminado."); return 0
    try:
        from .gui import App
        App(place or None, uri if a.uri else None).run([])
    except RuntimeError as e: print(f"Error: {e}"); return 4
    return 0

if __name__ == "__main__": raise SystemExit(main())

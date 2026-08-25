from __future__ import annotations
import argparse, logging
from .runtime import RuntimeManager
from .launcher import parse_target
VERSION = "0.3.0"
def main(argv=None):
    p=argparse.ArgumentParser(description="Launcher comunitario de Roblox para Linux")
    g=p.add_mutually_exclusive_group(); g.add_argument("--place"); g.add_argument("--uri")
    p.add_argument("--detect", action="store_true"); p.add_argument("--verbose", action="store_true"); p.add_argument("--version", action="version", version=VERSION)
    a=p.parse_args(argv); logging.basicConfig(level=logging.DEBUG if a.verbose else logging.WARNING)
    if a.detect:
        r,i=RuntimeManager().detect(); print(f"Flatpak: {'detectado' if r else 'no disponible'}"); print(f"Sober ({i.app_id}): {'instalado' if i.installed else 'no instalado'}"); return 0 if r else 3
    try: place, uri = parse_target(a.place, a.uri)
    except ValueError as e: p.error(str(e))
    try:
        from .gui import App
        App(place or None, uri if a.uri else None).run([])
    except RuntimeError as e: print(f"Error: {e}"); return 4
    return 0

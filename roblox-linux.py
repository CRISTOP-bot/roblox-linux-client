#!/usr/bin/env python3
"""Roblox Linux launcher (community launcher, not an official Roblox client)."""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_runner() -> str | None:
    for name in ("vinegar", "vinegar-launcher", "umu-run", "wine"):
        path = shutil.which(name)
        if path:
            return path
    return None


def launch(place_id: str | None, uri: str | None) -> int:
    runner = find_runner()
    if not runner:
        print("No encontré Vinegar, umu-run ni Wine.", file=sys.stderr)
        print("Instala Vinegar desde https://vinegarhq.org/ y vuelve a intentarlo.", file=sys.stderr)
        return 1

    target = uri or (f"roblox://placeId={place_id}" if place_id else "roblox://")
    env = os.environ.copy()
    env.setdefault("ROBLOX_LINUX_LAUNCHER", "1")

    # Vinegar understands Roblox URLs directly. For generic runners, delegate
    # to xdg-open so the registered Roblox protocol handler can do the work.
    if Path(runner).name in {"vinegar", "vinegar-launcher"}:
        cmd = [runner, "run", target]
    else:
        opener = shutil.which("xdg-open")
        if not opener:
            print("No encontré xdg-open para abrir la URL de Roblox.", file=sys.stderr)
            return 1
        cmd = [opener, target]

    print("Iniciando:", " ".join(cmd))
    return subprocess.call(cmd, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Launcher comunitario de Roblox para Linux")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--place", help="ID del juego/place que quieres abrir")
    group.add_argument("--uri", help="URL roblox:// completa")
    args = parser.parse_args()
    return launch(args.place, args.uri)


if __name__ == "__main__":
    raise SystemExit(main())

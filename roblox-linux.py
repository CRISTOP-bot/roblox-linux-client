#!/usr/bin/env python3
"""Roblox Linux Launcher — community launcher, not an official Roblox client."""
from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from urllib.parse import urlsplit

VERSION = "0.2.0"
PLACE_ID_RE = re.compile(r"^[1-9][0-9]*$")
EXIT_OK = 0
EXIT_ARGS = 2
EXIT_NO_RUNNER = 3
EXIT_RUNNER_BROKEN = 4
EXIT_NO_XDG_OPEN = 5
EXIT_NO_HANDLER = 6
EXIT_INVALID_TARGET = 7
EXIT_LAUNCH_FAILED = 8

log = logging.getLogger("roblox-linux")


@dataclass(frozen=True)
class Runner:
    name: str
    executable: str


RUNNERS = (
    ("Vinegar", "vinegar"),
    ("vinegar-launcher", "vinegar-launcher"),
    ("umu-run", "umu-run"),
    ("Wine", "wine"),
)


def discover_runners() -> list[Runner]:
    """Return installed runners in preference order, without executing them."""
    found: list[Runner] = []
    for name, command in RUNNERS:
        path = shutil.which(command)
        if path:
            found.append(Runner(name, path))
    return found


def runner_works(runner: Runner) -> tuple[bool, str]:
    """Safely check a runner without starting Roblox or a shell."""
    try:
        result = subprocess.run(
            [runner.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, type(exc).__name__
    output = (result.stdout or result.stderr).strip().splitlines()
    detail = output[0] if output else f"código {result.returncode}"
    return result.returncode == 0, detail


def choose_runner(runners: list[Runner]) -> tuple[Runner | None, dict[str, tuple[bool, str]]]:
    status: dict[str, tuple[bool, str]] = {}
    for runner in runners:
        status[runner.name] = runner_works(runner)
        if status[runner.name][0]:
            return runner, status
    return None, status


def build_uri(place_id: str | None, uri: str | None) -> str:
    if place_id is not None:
        if not PLACE_ID_RE.fullmatch(place_id):
            raise ValueError("el place ID debe ser un número entero positivo")
        return f"roblox://placeId={place_id}"
    if uri is None:
        return "roblox://"
    parts = urlsplit(uri)
    if parts.scheme.lower() != "roblox" or parts.path or parts.fragment:
        raise ValueError("la URL debe usar el protocolo roblox://")
    if not parts.netloc and not parts.query:
        return "roblox://"
    target = parts.netloc + (("?" + parts.query) if parts.query else "")
    if not target.startswith("placeId="):
        raise ValueError("la URL roblox:// debe contener placeId=<número>")
    value = target.removeprefix("placeId=")
    if not PLACE_ID_RE.fullmatch(value):
        raise ValueError("el place ID de la URL no es válido")
    return f"roblox://placeId={value}"


def xdg_handler() -> str | None:
    xdg_mime = shutil.which("xdg-mime")
    if not xdg_mime:
        return None
    try:
        result = subprocess.run(
            [xdg_mime, "query", "default", "x-scheme-handler/roblox"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    handler = result.stdout.strip()
    return handler or None


def launch(runner: Runner, target: str) -> int:
    if runner.name in {"Vinegar", "vinegar-launcher"}:
        command = [runner.executable, "run", target]
    else:
        xdg_open = shutil.which("xdg-open")
        if not xdg_open:
            print("Error: falta xdg-open para abrir el protocolo roblox://.", file=sys.stderr)
            return EXIT_NO_XDG_OPEN
        handler = xdg_handler()
        if not handler:
            print("Error: no existe un handler registrado para roblox://.", file=sys.stderr)
            print("Configura primero una instalación de Roblox compatible con Linux.", file=sys.stderr)
            return EXIT_NO_HANDLER
        if "roblox-linux.desktop" in handler:
            print("Error: el handler roblox:// apunta a este launcher y causaría un bucle.", file=sys.stderr)
            return EXIT_NO_HANDLER
        command = [xdg_open, target]

    log.debug("Ejecutando: %r", command)
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"Error: no se pudo ejecutar {runner.name}: {exc}", file=sys.stderr)
        return EXIT_LAUNCH_FAILED
    if result.returncode != 0:
        print(f"Error: {runner.name} terminó con código {result.returncode}.", file=sys.stderr)
        return EXIT_LAUNCH_FAILED
    return EXIT_OK


def print_detection() -> int:
    runners = discover_runners()
    if not runners:
        print("Runners detectados: ninguno")
        return EXIT_NO_RUNNER
    selected, status = choose_runner(runners)
    print("Runners detectados:")
    for runner in runners:
        works, detail = status[runner.name]
        print(f"  - {runner.name}: {'funciona' if works else 'no responde'} ({runner.executable}; {detail})")
    print(f"Seleccionado: {selected.name if selected else 'ninguno funcional'}")
    return EXIT_OK if selected else EXIT_RUNNER_BROKEN


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Launcher comunitario de Roblox para Linux")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--place", metavar="ID", help="ID numérico del juego que quieres abrir")
    group.add_argument("--uri", metavar="URL", help="URL roblox://placeId=<ID>")
    p.add_argument("--detect", action="store_true", help="muestra runners y selección, sin lanzar Roblox")
    p.add_argument("--verbose", action="store_true", help="activa logs de diagnóstico")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")
    if args.detect:
        return print_detection()
    try:
        target = build_uri(args.place, args.uri)
    except ValueError as exc:
        print(f"Error: {exc}.", file=sys.stderr)
        return EXIT_INVALID_TARGET

    runners = discover_runners()
    if not runners:
        print("Error: no encontré Vinegar, vinegar-launcher, umu-run ni Wine.", file=sys.stderr)
        print("Instala y configura uno manualmente; este launcher no descarga software.", file=sys.stderr)
        return EXIT_NO_RUNNER
    selected, status = choose_runner(runners)
    if selected is None:
        print("Error: encontré runners, pero ninguno funciona correctamente.", file=sys.stderr)
        for name, (_, detail) in status.items():
            print(f"  {name}: {detail}", file=sys.stderr)
        return EXIT_RUNNER_BROKEN
    log.debug("Runner seleccionado: %s (%s)", selected.name, selected.executable)
    return launch(selected, target)


if __name__ == "__main__":
    sys.exit(main())

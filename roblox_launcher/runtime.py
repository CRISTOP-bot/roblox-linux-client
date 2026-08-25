from __future__ import annotations
import logging, shutil, subprocess
from dataclasses import dataclass
from .models import RuntimeInfo
log = logging.getLogger(__name__)
SOBER_ID = "org.vinegarhq.Sober"

@dataclass
class RunningGame:
    process: subprocess.Popen
    target: str

class SoberRuntime:
    def __init__(self, flatpak: str): self.flatpak = flatpak
    def info(self) -> RuntimeInfo:
        try:
            p = subprocess.run([self.flatpak, "info", SOBER_ID], capture_output=True, text=True, timeout=8)
        except (OSError, subprocess.TimeoutExpired):
            return RuntimeInfo("Sober", SOBER_ID, "", False)
        version = ""
        for line in p.stdout.splitlines():
            if line.lower().startswith("version:"):
                version = line.split(":", 1)[1].strip()
        return RuntimeInfo("Sober", SOBER_ID, version, p.returncode == 0)
    def start(self, target: str) -> RunningGame:
        # Sober accepts Roblox protocol targets; no undocumented subcommand is used.
        p = subprocess.Popen([self.flatpak, "run", SOBER_ID, target], start_new_session=True)
        return RunningGame(p, target)

class RuntimeManager:
    def detect(self) -> tuple[SoberRuntime|None, RuntimeInfo]:
        flatpak = shutil.which("flatpak")
        if not flatpak:
            return None, RuntimeInfo("Sober", SOBER_ID, "", False)
        runtime = SoberRuntime(flatpak)
        info = runtime.info()
        return (runtime if info.installed else None), info

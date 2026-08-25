from __future__ import annotations
import logging
try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
except (ImportError, ValueError) as exc:
    raise RuntimeError("Falta PyGObject/GTK4. Instálalo desde los paquetes de tu distribución.") from exc
from .api import fetch_experience
from .config import Config
from .launcher import parse_target
from .runtime import RuntimeManager
log = logging.getLogger(__name__)

class Window(Gtk.ApplicationWindow):
    def __init__(self, app, initial_place=None, initial_uri=None):
        super().__init__(application=app, title="Roblox Launcher", default_width=560, default_height=480)
        self.config, self.manager, self.running = Config(), RuntimeManager(), None
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin_top=28, margin_bottom=28, margin_start=28, margin_end=28); self.set_child(box)
        title = Gtk.Label(label="Roblox Launcher"); title.add_css_class("title-1"); box.append(title)
        box.append(Gtk.Label(label="Frontend comunitario para un runtime compatible", xalign=0))
        self.entry = Gtk.Entry(placeholder_text="Place ID o URL roblox://"); box.append(self.entry)
        if initial_place: self.entry.set_text(initial_place)
        elif initial_uri: self.entry.set_text(initial_uri)
        row = Gtk.Box(spacing=8); box.append(row)
        play = Gtk.Button(label="▶  JUGAR"); play.add_css_class("suggested-action"); play.connect("clicked", self.on_play); row.append(play)
        detect = Gtk.Button(label="Detectar runtime"); detect.connect("clicked", self.on_detect); row.append(detect)
        self.status = Gtk.Label(label="Estado: comprobando runtime…", xalign=0); box.append(self.status)
        self.details = Gtk.Label(label="", xalign=0, wrap=True); box.append(self.details)
        box.append(Gtk.Separator())
        box.append(Gtk.Label(label="Recientes", xalign=0))
        self.recent = Gtk.ListBox(); box.append(self.recent); self.refresh_recent(); self.on_detect()
    def on_detect(self, *_):
        runtime, info = self.manager.detect()
        self.runtime = runtime
        self.status.set_text("Runtime detectado: Sober ✓" if runtime else "Estado: runtime no disponible")
        self.details.set_text((f"Versión: {info.version or 'desconocida'}") if runtime else "Instala Sober mediante Flatpak y vuelve a abrir el launcher.")
    def on_play(self, *_):
        try: place, uri = parse_target(None, self.entry.get_text().strip())
        except ValueError as e: self.status.set_text(f"Error: {e}"); return
        if not self.runtime: self.on_detect()
        if not self.runtime: return
        self.status.set_text("Estado: preparando…"); exp = fetch_experience(place, uri) if place else None
        if exp: self.config.add_recent(exp); self.refresh_recent()
        try:
            self.status.set_text("Estado: iniciando…"); self.running = self.runtime.start(uri)
            GLib.timeout_add(1000, self.poll_process)
        except OSError as e: self.status.set_text(f"Error al iniciar Sober: {e}")
    def poll_process(self):
        if not self.running: return False
        code = self.running.process.poll()
        if code is None: self.status.set_text("Estado: jugando"); return True
        self.status.set_text("Estado: cerrado" if code == 0 else f"Estado: error (código {code})"); self.running = None; return False
    def refresh_recent(self):
        while (child := self.recent.get_first_child()): self.recent.remove(child)
        for item in self.config.data.get("recent", []): self.recent.append(Gtk.Label(label=f"{item.get('name')}  ·  {item.get('place_id')}", xalign=0))

class App(Gtk.Application):
    def __init__(self, place=None, uri=None): super().__init__(application_id="org.community.RobloxLauncher"); self.place, self.uri = place, uri
    def do_activate(self): Window(self, self.place, self.uri).present()

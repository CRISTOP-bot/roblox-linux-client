from __future__ import annotations
import logging, threading
try:
    import gi; gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
except (ImportError, ValueError) as exc:
    raise RuntimeError("Falta GTK4/PyGObject. Instala los paquetes python3-gi y GTK4 de tu distribución.") from exc
from .api import fetch_experience
from .config import Config
from .launcher import parse_target
from .models import Experience
from .runtime import RuntimeManager
log = logging.getLogger(__name__)

class Window(Gtk.ApplicationWindow):
    def __init__(self, app, place=None, uri=None):
        super().__init__(application=app, title="Roblox Linux Client", default_width=900, default_height=600)
        self.config = Config(); self.manager = RuntimeManager(); self.runtime = None; self.running = None
        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL); self.set_child(root)
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT); self.stack.set_vexpand(True); root.append(self.stack)
        sidebar = Gtk.StackSidebar(); sidebar.set_stack(self.stack); sidebar.set_size_request(180, -1); root.prepend(sidebar)
        self.home = self._home(place, uri); self.stack.add_titled(self.home, "home", "🏠  Inicio")
        self.fav_box = self._list_page("Favoritos", True); self.stack.add_titled(self.fav_box, "favorites", "⭐  Favoritos")
        self.hist_box = self._list_page("Recientes", False); self.stack.add_titled(self.hist_box, "history", "🕘  Recientes")
        self.settings = self._settings(); self.stack.add_titled(self.settings, "settings", "⚙  Ajustes")
        self.diag = self._diagnostic(); self.stack.add_titled(self.diag, "diagnostic", "🧪  Diagnóstico")
        self.refresh_lists(); GLib.idle_add(self.detect_runtime)

    def _home(self, place, uri):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin_top=36, margin_bottom=36, margin_start=42, margin_end=42)
        title=Gtk.Label(label="Roblox Linux Client"); title.add_css_class("title-1"); box.append(title)
        box.append(Gtk.Label(label="Launcher comunitario · Sober es el runtime", xalign=0))
        self.entry=Gtk.Entry(placeholder_text="Place ID o URL de una experiencia"); self.entry.set_hexpand(True); box.append(self.entry)
        if place: self.entry.set_text(place)
        elif uri: self.entry.set_text(uri)
        row=Gtk.Box(spacing=10); box.append(row)
        play=Gtk.Button(label="▶  JUGAR"); play.add_css_class("suggested-action"); play.set_size_request(180, 48); play.connect("clicked", self.play); row.append(play)
        detect=Gtk.Button(label="Detectar runtime"); detect.connect("clicked", lambda *_: self.detect_runtime()); row.append(detect)
        self.status=Gtk.Label(label="Estado: comprobando…", xalign=0); box.append(self.status)
        self.runtime_label=Gtk.Label(label="", xalign=0); box.append(self.runtime_label)
        self.favorite_button=Gtk.Button(label="☆ Añadir a favoritos"); self.favorite_button.connect("clicked", self.toggle_current_favorite); box.append(self.favorite_button)
        return box

    def _list_page(self, title, favorites):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=30, margin_start=30, margin_end=30, margin_bottom=30)
        box.append(Gtk.Label(label=title, xalign=0)); listbox=Gtk.ListBox(); listbox.set_selection_mode(Gtk.SelectionMode.NONE); box.append(listbox)
        if not favorites:
            clear=Gtk.Button(label="Limpiar historial"); clear.connect("clicked", lambda *_: (self.config.clear_history(), self.refresh_lists())); box.append(clear)
        box.listbox=listbox; return box

    def _settings(self):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=30, margin_start=30); box.append(Gtk.Label(label="Ajustes", xalign=0)); box.append(Gtk.Label(label="El tema sigue la preferencia del sistema GTK4.\nLos datos se guardan localmente y no contienen credenciales.", xalign=0, wrap=True)); return box
    def _diagnostic(self):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=30, margin_start=30); box.append(Gtk.Label(label="Diagnóstico", xalign=0)); self.diag_label=Gtk.Label(label="Comprobando…", xalign=0); box.append(self.diag_label); return box

    def detect_runtime(self):
        runtime, info = self.manager.detect(); self.runtime=runtime
        text=f"Flatpak: {'✓' if info.flatpak_available else '✗'}\nSober: {'✓' if info.installed else '✗'}\nSober ID: {info.app_id}\nRuntime disponible: {'✓' if runtime else '✗'}"
        self.diag_label.set_text(text); self.runtime_label.set_text(f"Runtime: Sober ✓ ({info.version or 'versión desconocida'})" if runtime else "Runtime: Sober no está instalado")
        self.status.set_text("Estado: listo" if runtime else "Estado: falta un runtime compatible"); return False

    def play(self, *_):
        try: place, uri = parse_target(self.entry.get_text().strip() or None, None)
        except ValueError as exc: self.status.set_text(f"Error: {exc}"); return
        if not self.runtime: self.detect_runtime()
        if not self.runtime: return
        self.status.set_text("Estado: preparando…")
        threading.Thread(target=self._prepare, args=(place, uri), daemon=True).start()

    def _prepare(self, place, uri):
        exp=fetch_experience(place, uri)
        GLib.idle_add(self._start, exp)
    def _start(self, exp: Experience):
        try:
            self.config.add_history(exp); self.refresh_lists(); self.status.set_text("Estado: iniciando…")
            self.running=self.runtime.start(exp.url); GLib.timeout_add(1000, self.poll)
        except OSError as exc: self.status.set_text(f"Error al iniciar Sober: {exc}")
        return False
    def poll(self):
        if not self.running: return False
        code=self.running.process.poll()
        if code is None: self.status.set_text("Estado: jugando (proceso activo)"); return True
        self.status.set_text("Estado: cerrado" if code == 0 else f"Estado: error (código {code})"); self.running=None; return False
    def toggle_current_favorite(self, *_):
        try: place, uri=parse_target(self.entry.get_text().strip() or None, None)
        except ValueError as exc: self.status.set_text(f"Error: {exc}"); return
        exp=Experience(place, uri); added=self.config.toggle_favorite(exp); self.favorite_button.set_label("★ En favoritos" if added else "☆ Añadir a favoritos"); self.refresh_lists()
    def refresh_lists(self):
        for box, key, fav in [(self.fav_box,"favorites",True),(self.hist_box,"history",False)]:
            while (child:=box.listbox.get_first_child()): box.listbox.remove(child)
            for item in self.config.data[key]:
                row=Gtk.Box(spacing=8, margin_top=5, margin_bottom=5, margin_start=5, margin_end=5); label=Gtk.Label(label=f"{item.get('name','Experiencia')} · {item['place_id']}", xalign=0); label.set_hexpand(True); row.append(label)
                button=Gtk.Button(label="Jugar"); button.connect("clicked", lambda _, x=item: self.use_item(x)); row.append(button)
                if fav:
                    remove=Gtk.Button(label="Eliminar"); remove.connect("clicked", lambda _, x=item: (self.config.remove_favorite(x['place_id']), self.refresh_lists())); row.append(remove)
                box.listbox.append(row)
    def use_item(self, item): self.entry.set_text(item.get("url", f"roblox://placeId={item['place_id']}")); self.stack.set_visible_child_name("home")

class App(Gtk.Application):
    def __init__(self, place=None, uri=None): super().__init__(application_id="org.community.RobloxLauncher"); self.place=place; self.uri=uri
    def do_activate(self): Window(self, self.place, self.uri).present()

from __future__ import annotations
import logging, threading, platform
try:
    import gi; gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
except (ImportError, ValueError) as exc: raise RuntimeError("Falta GTK4/PyGObject. Instala GTK4 y python3-gi.") from exc
from .api import fetch_experience
from .config import Config
from .launcher import parse_target
from .models import Experience
from .runtime import RuntimeManager
from .widgets import ExperienceCard
log=logging.getLogger(__name__)

class Window(Gtk.ApplicationWindow):
    def __init__(self, app, place=None, uri=None):
        super().__init__(application=app,title="Roblox Linux Client",default_width=1000,default_height=680)
        self.config=Config(); self.manager=RuntimeManager(); self.runtime=None; self.running=None; self.current=None
        root=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL); self.set_child(root)
        self.stack=Gtk.Stack(transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT); self.stack.set_hexpand(True); self.stack.set_vexpand(True); root.append(self.stack)
        side=Gtk.StackSidebar(); side.set_stack(self.stack); side.set_size_request(190,-1); root.prepend(side)
        self.home=self.make_home(place,uri); self.stack.add_titled(self.home,"home","🏠  Inicio")
        self.fav_page=self.make_collection("Favoritos",True); self.stack.add_titled(self.fav_page,"favorites","⭐  Favoritos")
        self.history_page=self.make_collection("Recientes",False); self.stack.add_titled(self.history_page,"history","🕘  Recientes")
        self.search_page=self.make_search(); self.stack.add_titled(self.search_page,"search","🔍  Buscar")
        self.stack.add_titled(self.make_settings(),"settings","⚙  Ajustes"); self.stack.add_titled(self.make_diagnostic(),"diagnostic","🧪  Diagnóstico")
        self.refresh_all(); GLib.idle_add(self.detect)

    def make_home(self,place,uri):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14,margin_top=28,margin_bottom=28,margin_start=30,margin_end=30)
        title=Gtk.Label(label="Roblox Linux Client"); title.add_css_class("title-1"); box.append(title); box.append(Gtk.Label(label="Elige una experiencia y pulsa Jugar",xalign=0))
        self.entry=Gtk.Entry(placeholder_text="Place ID o URL de una experiencia"); self.entry.set_tooltip_text("Introduce un Place ID numérico o una URL de Roblox"); box.append(self.entry)
        if place:self.entry.set_text(place)
        elif uri:self.entry.set_text(uri)
        row=Gtk.Box(spacing=8); box.append(row); play=Gtk.Button(label="▶  JUGAR"); play.add_css_class("suggested-action"); play.set_size_request(180,48); play.connect("clicked",self.play_input); row.append(play)
        self.status=Gtk.Label(label="Estado: comprobando…",xalign=0); box.append(self.status); self.runtime_label=Gtk.Label(label="",xalign=0); box.append(self.runtime_label)
        self.favorite_button=Gtk.Button(label="☆ Favorito"); self.favorite_button.connect("clicked",self.favorite_input); box.append(self.favorite_button)
        box.append(Gtk.Label(label="Favoritos",xalign=0)); self.home_favs=Gtk.FlowBox(); self.home_favs.set_max_children_per_line(4); self.home_favs.set_selection_mode(Gtk.SelectionMode.NONE); box.append(self.home_favs)
        box.append(Gtk.Label(label="Recientes",xalign=0)); self.home_recent=Gtk.FlowBox(); self.home_recent.set_max_children_per_line(4); self.home_recent.set_selection_mode(Gtk.SelectionMode.NONE); box.append(self.home_recent); return box

    def make_collection(self,title,favorites):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12,margin_top=28,margin_bottom=28,margin_start=30,margin_end=30); box.append(Gtk.Label(label=title,xalign=0)); flow=Gtk.FlowBox(); flow.set_max_children_per_line(4); flow.set_selection_mode(Gtk.SelectionMode.NONE); box.append(flow); box.flow=flow
        if not favorites:
            clear=Gtk.Button(label="Limpiar historial"); clear.connect("clicked",self.confirm_clear); box.append(clear)
        return box

    def make_search(self):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12,margin_top=28,margin_start=30,margin_end=30); box.append(Gtk.Label(label="Buscar experiencias",xalign=0)); self.search_entry=Gtk.SearchEntry(placeholder_text="Place ID o URL"); self.search_entry.set_tooltip_text("La búsqueda pública por nombre depende de la API disponible"); self.search_entry.connect("activate",self.search); box.append(self.search_entry); b=Gtk.Button(label="Buscar"); b.connect("clicked",self.search); box.append(b); self.search_results=Gtk.FlowBox(); self.search_results.set_selection_mode(Gtk.SelectionMode.NONE); box.append(self.search_results); return box

    def make_settings(self):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10,margin_top=28,margin_start=30); box.append(Gtk.Label(label="Ajustes",xalign=0)); box.append(Gtk.Label(label="El tema claro u oscuro sigue la preferencia del sistema GTK4.\nNo se guardan credenciales, cookies ni contraseñas.",xalign=0,wrap=True)); return box
    def make_diagnostic(self):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10,margin_top=28,margin_start=30); box.append(Gtk.Label(label="Diagnóstico",xalign=0)); self.diag=Gtk.Label(label="Comprobando…",xalign=0); box.append(self.diag); b=Gtk.Button(label="🔄 Volver a detectar"); b.connect("clicked",lambda *_:self.detect()); box.append(b); copy=Gtk.Button(label="📋 Copiar diagnóstico"); copy.connect("clicked",self.copy_diag); box.append(copy); return box

    def detect(self):
        runtime,info=self.manager.detect(); self.runtime=runtime; self.diagnostic=f"Sistema\nOS: Linux\nArquitectura: {platform.machine()}\nGTK: GTK4\n\nRuntime\nFlatpak: {'✓' if info.flatpak_available else '✗'}\nSober: {'✓' if info.installed else '✗'}\nID: {info.app_id}\nVersión: {info.version or 'desconocida'}\nEstado: {'Disponible' if runtime else 'No disponible'}"; self.diag.set_text(self.diagnostic); self.runtime_label.set_text(f"Runtime: Sober ✓ ({info.version or 'versión desconocida'})" if runtime else "Runtime: Sober no está disponible"); self.status.set_text("Estado: listo" if runtime else "Estado: falta Sober"); return False
    def copy_diag(self,*_):
        self.get_clipboard().set(self.diagnostic)
    def parse_entry(self,text): return parse_target(text.strip() or None,None)
    def play_input(self,*_):
        try: place,uri=self.parse_entry(self.entry.get_text())
        except ValueError as e:self.status.set_text(f"Error: {e}"); return
        if not self.runtime:self.detect()
        if not self.runtime:return
        self.status.set_text("Preparando experiencia…"); threading.Thread(target=self.prepare,args=(place,uri),daemon=True).start()
    def prepare(self,place,uri): GLib.idle_add(self.start,fetch_experience(place,uri))
    def start(self,exp):
        try:
            self.current=exp; self.config.add_history(exp); self.refresh_all(); self.status.set_text("Iniciando Sober…"); self.running=self.runtime.start(exp.url); GLib.timeout_add(1000,self.poll)
        except OSError as e:self.status.set_text(f"Error al iniciar Sober: {e}")
        return False
    def poll(self):
        if not self.running:return False
        code=self.running.process.poll()
        if code is None:self.status.set_text("Jugando (proceso de Sober activo)"); return True
        self.status.set_text("Cerrado" if code==0 else f"Error: Sober terminó con código {code}"); self.running=None; return False
    def favorite_input(self,*_):
        try: place,uri=self.parse_entry(self.entry.get_text())
        except ValueError as e:self.status.set_text(f"Error: {e}"); return
        exp=Experience(place,uri); added=self.config.toggle_favorite(exp); self.favorite_button.set_label("★ En favoritos" if added else "☆ Favorito"); self.refresh_all()
    def use(self,exp): self.entry.set_text(exp.url); self.stack.set_visible_child_name("home")
    def card(self,item,favorite=False):
        exp=Experience(str(item['place_id']),item.get('url',f"roblox://placeId={item['place_id']}"),item.get('name','Experiencia de Roblox'),thumbnail_url=item.get('thumbnail_url')); return ExperienceCard(exp,self.use,lambda x:self.config.toggle_favorite(x) or self.refresh_all(),(lambda x:(self.config.remove_favorite(x.place_id),self.refresh_all())) if favorite else None)
    def clear_flow(self,flow):
        while (c:=flow.get_first_child()):flow.remove(c)
    def fill(self,flow,items,favorite=False): self.clear_flow(flow); [flow.append(self.card(x,favorite)) for x in items]
    def refresh_all(self):
        fav=self.config.data['favorites']; hist=self.config.data['history']; self.fill(self.home_favs,fav,True); self.fill(self.home_recent,hist[:6]); self.fill(self.fav_page.flow,fav,True); self.fill(self.history_page.flow,hist)
    def search(self,*_):
        self.clear_flow(self.search_results); text=self.search_entry.get_text().strip()
        if not text:return
        try: place,uri=self.parse_entry(text); self.search_results.append(self.card({'place_id':place,'url':uri,'name':'Resultado por Place ID'}))
        except ValueError: self.search_results.append(Gtk.Label(label="Escribe un Place ID o una URL válida."))
    def confirm_clear(self,*_):
        dialog=Gtk.AlertDialog(message="¿Limpiar todo el historial?"); dialog.set_detail("Esta acción no afecta a tus favoritos."); dialog.set_buttons(["Cancelar","Limpiar"]); dialog.choose(self,None,self.clear_response)
    def clear_response(self,dialog,result):
        try:
            if dialog.choose_finish(result)==1:self.config.clear_history(); self.refresh_all()
        except Exception: log.exception("No se pudo limpiar el historial")

class App(Gtk.Application):
    def __init__(self,place=None,uri=None): super().__init__(application_id="org.community.RobloxLauncher"); self.place=place; self.uri=uri
    def do_activate(self): Window(self,self.place,self.uri).present()

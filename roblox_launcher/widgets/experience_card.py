from __future__ import annotations
from typing import Callable
from ..models import Experience

try:
    import gi; gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk
except (ImportError, ValueError) as exc:
    raise RuntimeError("GTK4/PyGObject no está disponible") from exc

class ExperienceCard(Gtk.Frame):
    """Reusable native GTK card for home, favorites, recents and search."""
    def __init__(self, experience: Experience, on_play: Callable[[Experience], None], on_favorite: Callable[[Experience], None] | None = None, on_remove: Callable[[Experience], None] | None = None):
        super().__init__(); self.experience=experience; self.add_css_class("card")
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        image=Gtk.Image.new_from_icon_name("applications-games-symbolic"); image.set_pixel_size(110); image.set_tooltip_text("Thumbnail no disponible"); box.append(image)
        name=Gtk.Label(label=experience.name, xalign=0); name.set_wrap(True); name.add_css_class("heading"); box.append(name)
        box.append(Gtk.Label(label=f"Place ID: {experience.place_id}", xalign=0))
        row=Gtk.Box(spacing=6); play=Gtk.Button(label="▶ Jugar"); play.set_tooltip_text("Iniciar esta experiencia"); play.connect("clicked", lambda *_: on_play(experience)); row.append(play)
        if on_favorite:
            fav=Gtk.Button(label="☆ Favorito"); fav.set_tooltip_text("Añadir o quitar favorito"); fav.connect("clicked", lambda *_: on_favorite(experience)); row.append(fav)
        if on_remove:
            remove=Gtk.Button(label="Eliminar"); remove.set_tooltip_text("Eliminar favorito"); remove.connect("clicked", lambda *_: on_remove(experience)); row.append(remove)
        box.append(row); self.set_child(box)

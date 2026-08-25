from .config import Config
from .models import Experience
class Favorites:
    def __init__(self, config: Config): self.config=config
    def toggle(self, exp: Experience) -> bool: return self.config.toggle_favorite(exp)
    def remove(self, place_id: str): self.config.remove_favorite(place_id)
    def all(self): return list(self.config.data["favorites"])

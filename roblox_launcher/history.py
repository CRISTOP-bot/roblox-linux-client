from .config import Config
from .models import Experience
class History:
    def __init__(self, config: Config): self.config=config
    def record(self, exp: Experience): self.config.add_history(exp)
    def clear(self): self.config.clear_history()
    def all(self): return list(self.config.data["history"])

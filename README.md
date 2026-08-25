# Roblox Linux Client

Launcher comunitario de escritorio para Linux, inspirado en la experiencia de Sober. Sober permanece como runtime principal (`org.vinegarhq.Sober`); este proyecto no lo recrea, no incluye código propietario, no usa Wine/`xdg-open`/navegador como mecanismo principal y no instala software automáticamente.

## Flujo

```text
GTK4/CLI → Flatpak/Sober → roblox://experiences/start?placeId=… → Roblox
```

La integración invoca Flatpak directamente con argumentos separados. El destino `roblox://experiences/start?placeId=...` se mantiene aislado en `runtime.py` y se basa en el mecanismo observable/documentado por el runtime; no se inventa un subcomando de Sober.

## Estructura

```text
launcher.py
roblox_launcher/
├── main.py          # CLI
├── gui.py           # GTK4, páginas y tareas en segundo plano
├── runtime.py       # Flatpak/Sober y ciclo de vida del proceso
├── launcher.py      # validación y URI
├── api.py           # metadatos públicos opcionales
├── config.py        # migración y persistencia
├── models.py
└── thumbnails.py    # caché con límite de tamaño
data/org.community.RobloxLauncher.desktop
tests/test_launcher.py
pyproject.toml
install.sh
```

## Dependencias

Python 3.10+, GTK4, PyGObject y Flatpak. Sober debe estar instalado por el usuario. La consulta de metadatos/thumbnails es best-effort, tiene timeout, no usa login y nunca impide iniciar por Place ID.

## Instalación y ejecución

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
roblox-launcher
roblox-launcher --place 123456789
roblox-launcher --uri 'roblox://placeId=123456789'
```

También existe `./install.sh`, que instala el paquete para el usuario y copia el `.desktop`. Si el ejecutable no aparece, añade `~/.local/bin` al `PATH`.

## CLI y diagnóstico

```bash
roblox-launcher --detect
roblox-launcher --diagnose
roblox-launcher --history
roblox-launcher --favorite 123456789
roblox-launcher --verbose --place 123456789
roblox-launcher --version
```

La GUI tiene Inicio, Favoritos, Recientes, Ajustes y Diagnóstico. Los datos se guardan en `~/.config/roblox-launcher/config.json`; el formato anterior con `recent` se migra sin perderlo. Los thumbnails se almacenan en `~/.cache/roblox-launcher/thumbnails` y se limitan a 512 KiB por imagen.

El estado `Jugando` es aproximado: indica que el proceso Sober sigue activo. No afirma que Roblox terminó de cargar porque el runtime no expone necesariamente ese estado.

## Tests

```bash
python -m unittest discover -s tests -v
python3 launcher.py --detect
```

## Desktop y empaquetado

```bash
mkdir -p ~/.local/share/applications
cp data/org.community.RobloxLauncher.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

El `.desktop` no registra automáticamente `roblox://` para evitar bucles. Para Flatpak futuro, empaquetar solo esta GUI y declarar GTK4/PyGObject; Sober debe seguir siendo un runtime separado. Para AppImage incluir dependencias GTK, pero no Roblox/Sober. La modularidad también permite crear después un paquete `.deb`.

## Seguridad y alcance

No hay credenciales, cookies, tokens, login, exploits, cheats, bypasses, modificaciones del cliente ni evasión de sistemas de seguridad. Roblox y Sober son marcas/proyectos de sus respectivos autores; este launcher no está afiliado con ellos.

# Roblox Launcher para Linux

Frontend/orquestador comunitario inspirado en la experiencia de Sober. **No es un cliente oficial de Roblox ni recrea Sober**: usa un runtime compatible ya instalado, con prioridad para Sober mediante Flatpak (`org.vinegarhq.Sober`). No contiene código propietario, credenciales, bypasses ni exploits, y no instala software automáticamente.

## Arquitectura

```text
GUI / CLI → detección de Sober → URI roblox://experiences/start?placeId=… → Sober → Roblox → experiencia
```

El launcher no usa `xdg-open`, Wine ni navegador como mecanismo principal. Invoca directamente Flatpak/Sober con una lista de argumentos segura. El formato `roblox://experiences/start?placeId=...` se usa como destino de experiencia; si una versión del runtime cambia su interfaz, la integración queda aislada en `roblox_launcher/runtime.py`.

## Dependencias

- Python 3.10+
- GTK4 y PyGObject (`python3-gi` y el paquete GTK4 de tu distribución)
- Flatpak
- Sober instalado y configurado por el usuario: `org.vinegarhq.Sober`

El launcher solo detecta el runtime. No ejecuta instalaciones ni actualizaciones automáticas.

## Uso desde el código

```bash
python3 launcher.py
python3 launcher.py --place 123456789
python3 launcher.py --uri 'roblox://placeId=123456789'
python3 launcher.py --detect
python3 launcher.py --verbose
python3 launcher.py --version
```

`--detect` funciona incluso si GTK no está instalado y muestra Flatpak/Sober. La ventana muestra los estados `Runtime detectado`, `Preparando`, `Iniciando`, `Jugando`, `Cerrado` y `Error`. La información de la experiencia se solicita de forma opcional y sin autenticación; si la API no responde, el juego aún puede iniciarse.

## Instalación de desarrollo

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
roblox-launcher --detect
```

Para integrar el menú de aplicaciones:

```bash
mkdir -p ~/.local/share/applications
cp data/org.community.RobloxLauncher.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

## Estructura

```text
roblox-launcher/
├── launcher.py
├── roblox_launcher/
│   ├── main.py       # CLI y entrada
│   ├── gui.py        # GTK4
│   ├── runtime.py    # detección y proceso Sober
│   ├── launcher.py   # validación y URI
│   ├── api.py        # metadatos opcionales
│   ├── config.py     # recientes/favoritos
│   └── models.py
├── data/
├── tests/
├── pyproject.toml
└── LICENSE
```

## Empaquetado futuro

- **Flatpak:** crear un manifiesto con runtime GTK4, permisos de red solo si se desea mostrar metadatos y acceso al servicio de sesión; Sober debe seguir siendo una dependencia/runtime separado, no copiarse dentro de este proyecto.
- **AppImage:** empaquetar Python, PyGObject y las bibliotecas GTK compatibles con linuxdeploy; no incluir Roblox ni Sober.

## Limitaciones

La aplicación puede detectar que el proceso de Sober fue creado y cuándo termina, pero no puede garantizar que Roblox terminó de cargar una experiencia sin una API de estado expuesta por el runtime. El estado `Jugando` significa que el proceso sigue activo.

MIT. Roblox y Sober pertenecen a sus respectivos autores; este proyecto no está afiliado con ellos.

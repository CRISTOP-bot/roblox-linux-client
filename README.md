# Roblox Linux Launcher

Launcher comunitario para iniciar Roblox en Linux. **No es un cliente oficial de Roblox**, no incluye archivos propietarios, no descarga software y no intenta evadir sistemas de seguridad.

## Requisitos

- Linux moderno y Python 3.10+.
- Vinegar, `vinegar-launcher`, `umu-run` o Wine ya instalado y configurado.
- Para runners que delegan en el sistema: `xdg-open`, `xdg-mime` y un handler funcional para `roblox://`.

El launcher no instala ni descarga nada automáticamente.

## Uso

```bash
python3 roblox-linux.py --place 123456
python3 roblox-linux.py --uri 'roblox://placeId=123456'
python3 roblox-linux.py                 # apertura general: roblox://
python3 roblox-linux.py --detect
python3 roblox-linux.py --version
python3 roblox-linux.py --place 123456 --verbose
```

Vinegar se prioriza sobre `vinegar-launcher`, `umu-run` y Wine. `--detect` ejecuta una comprobación segura de versión y muestra el runner seleccionado. Los códigos de salida son útiles para scripts: `3` sin runner, `4` runner no funcional, `5` sin `xdg-open`, `6` sin handler, `7` destino inválido y `8` fallo al lanzar.

## Instalación local

```bash
chmod +x roblox-linux.py install.sh
./install.sh
roblox-linux --place 123456
```

## Protocolo `roblox://`

La asociación debe hacerla el software compatible que ya tengas instalado. Puedes inspeccionarla con:

```bash
xdg-mime query default x-scheme-handler/roblox
xdg-mime query filetype roblox://placeId=123456
```

No registres este launcher como handler del protocolo si vas a usar un runner que dependa de `xdg-open`, porque provocaría un bucle. Vinegar se ejecuta directamente cuando está disponible. Si quieres integrar el launcher en el menú, copia el `.desktop` a `~/.local/share/applications/` después de instalarlo y actualiza la base de datos del escritorio. El archivo incluido es una entrada de aplicación normal, no una asociación automática del protocolo.

## Estructura propuesta para una instalación Linux

```text
roblox-linux-client/
├── pyproject.toml
├── src/roblox_linux_launcher/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── runners.py
│   └── protocol.py
├── tests/
├── data/roblox-linux.desktop
├── README.md
└── LICENSE
```

La separación sugerida facilita pruebas unitarias de detección, validación y construcción de comandos sin ejecutar Roblox.

## Licencia

MIT. Roblox es una marca de Roblox Corporation; este proyecto no está afiliado con Roblox Corporation.

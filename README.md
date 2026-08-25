# Roblox Linux Launcher

Launcher comunitario para iniciar Roblox en Linux usando [Vinegar](https://vinegarhq.org/), una capa de compatibilidad basada en Wine.

> **Importante:** Roblox Corporation no ofrece un cliente oficial para Linux. Este proyecto no contiene archivos propietarios de Roblox, no modifica el cliente y puede dejar de funcionar si cambian el cliente o sus sistemas antitrampas. Úsalo respetando los términos de servicio de Roblox.

## Requisitos

- Linux x86_64
- Python 3.10+
- [Vinegar](https://vinegarhq.org/) recomendado (Wine/umu-run como alternativas)
- Una instalación funcional de Roblox configurada por Vinegar

## Uso

```bash
chmod +x install.sh
./install.sh
roblox-linux --place 1818
# o abre una URL roblox://
roblox-linux --uri 'roblox://placeId=1818'
```

El ID `1818` es solo un ejemplo. El launcher no descarga ni redistribuye Roblox.

## Estado

MVP inicial: detección del runner, apertura de URLs `roblox://`, instalación local y archivo `.desktop`. Las siguientes mejoras pueden incluir configuración gráfica, logs, perfiles y detección de instalaciones.

## Licencia

MIT. Roblox es una marca de Roblox Corporation; este proyecto no está afiliado con Roblox Corporation.

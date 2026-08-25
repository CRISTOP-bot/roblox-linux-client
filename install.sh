#!/usr/bin/env bash
set -euo pipefail
prefix="${1:-$HOME/.local}"
mkdir -p "$prefix/bin" "$prefix/share/applications" "$prefix/share/icons/hicolor/scalable/apps"
install -m 755 roblox-linux.py "$prefix/bin/roblox-linux"
install -m 644 roblox-linux.desktop "$prefix/share/applications/roblox-linux.desktop"
update-desktop-database "$prefix/share/applications" 2>/dev/null || true
echo "Instalado en $prefix/bin/roblox-linux"

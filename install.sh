#!/usr/bin/env bash
set -euo pipefail
prefix="${1:-$HOME/.local}"
python3 -m pip install --user .
mkdir -p "$prefix/share/applications"
install -m 644 data/org.community.RobloxLauncher.desktop "$prefix/share/applications/"
update-desktop-database "$prefix/share/applications" 2>/dev/null || true
echo "Instalado: $prefix/bin/roblox-launcher"

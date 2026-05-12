#!/usr/bin/env bash
# =====================================================
#  run_local.sh — Startet die lokale Dash-App mit uv
#  Voraussetzungen: uv (https://astral.sh/uv) installiert
# =====================================================
set -euo pipefail

# In Skriptverzeichnis wechseln
cd "$(dirname "$0")"

# Prüfen, ob uv im PATH ist
if ! command -v uv >/dev/null 2>&1; then
  echo "[Fehler] 'uv' wurde nicht gefunden."
  echo "Bitte installiere uv (macOS/Linux):"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "[1/3] Virtuelle Umgebung anlegen (uv venv)"
uv venv

echo "[2/3] Abhängigkeiten installieren (requirements.txt)"
uv pip install -r requirements.txt

echo "[3/3] Starte App (uv run app.py)"
uv run app.py

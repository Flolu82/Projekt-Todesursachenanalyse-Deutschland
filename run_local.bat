@echo off
REM =====================================================
REM  run_local.bat — Startet die lokale Dash-App mit uv
REM  Voraussetzungen: uv (https://astral.sh/uv) installiert
REM =====================================================

REM In Skriptverzeichnis wechseln
cd /d "%~dp0"

REM Prüfen, ob uv im PATH ist
where uv >nul 2>nul
if errorlevel 1 (
  echo [Fehler] 'uv' wurde nicht gefunden.
  echo Bitte installiere uv (PowerShell):
  echo   irm https://astral.sh/uv/install.ps1 ^| iex
  exit /b 1
)

echo [1/3] Virtuelle Umgebung anlegen (uv venv)
uv venv

echo [2/3] Abhaengigkeiten installieren (requirements.txt)
uv pip install -r requirements.txt

echo [3/3] Starte App (uv run todesursachen_dash_lokal.py)
uv run todesursachen_dash_lokal.py

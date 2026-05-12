# Todesursachen-Analyse Deutschland 1980–2024

Interaktives Dashboard zur Visualisierung der amtlichen Sterbefalldaten des
Statistischen Bundesamts. Refactor + Production-Build der Original-Version
(educx-Abschlussprojekt, 09/2025).

**Live-Demo:** [dash.fl-pro-consulting.de](https://dash.fl-pro-consulting.de)
**Kontext-Seite:** [fl-pro-consulting.de/selbst-forschen](https://fl-pro-consulting.de/selbst-forschen/)

## Was die App kann

- Zeitreihen für ~80 Todesursachen-Kategorien (1980–2024, 45 Jahre)
- Vergleich männlich / weiblich / Gesamt
- 3 Darstellungsmodi: Linien · Gestapelt · Anteil %
- Zeitraum frei wählbar via RangeSlider
- **Altersverteilung pro Ursache und Jahr** (17 Altersgruppen)
- Deutsche Tausender-Trennung, Lade-Spinner, Healthcheck
- Production-ready: Docker + gunicorn + Reverse-Proxy

## Was sich vs. Original-Version (09/2025) geändert hat

Vollständiger Changelog steht **im Code-Header von `app.py`** (Punkte 1–13). Kurzfassung:

| Bereich | Vorher | Jetzt |
|---|---|---|
| Datenumfang | 1990–2023, nur Jahr × Geschlecht | **1980–2024, plus 17 Altersgruppen** |
| Tabs | – | „Zeitverlauf" + **„Altersverteilung"** (neu) |
| View-Modi | nur Linien | Linien · Gestapelt · Anteil % |
| Default | 2 Ursachen alphabetisch | Top-5 nach Toten im neuesten Jahr |
| Filter | nur Ursache | + Geschlecht + Zeitraum + Jahr (im Age-Tab) |
| Sprache | DE/EN mix | komplett Deutsch |
| Zahlen-Format | `72,517` (US) | `72.517` (DE) |
| Production | `app.run_server(debug=True)` (dev only) | `server = app.server` für gunicorn, Docker, `/health` |
| Performance | Excel bei jedem Request neu lesen | `@lru_cache`, einmal pro Prozess |
| Parser | hardcoded `skiprows=5` | sucht Header-Zeilen via Content-Match (Layout-tolerant) |
| Versionen | Dash 2.17 + Plotly 5.22 + Pandas 2.2 | Dash 2.18 + Plotly 5.24 + Pandas 2.2 + Flask 3 + gunicorn 23 |

## Daten

| Datei | Inhalt | Zeitraum | Quelle |
|---|---|---|---|
| `data/23211-0001_de.xlsx` | Todesursache × Jahr × Geschlecht | 1980–2024 | Destatis [23211-0001](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0001) |
| `data/23211-0002_de.xlsx` | + 17 Altersgruppen | 1980–2024 | Destatis [23211-0002](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0002) |

Stand der Daten: **12.05.2026**.

## Setup

### Variante A — Lokal (Python + uv)

```bash
# macOS/Linux
./run_local.sh

# Windows
run_local.bat
```

uv installiert die Abhängigkeiten automatisch in eine venv und startet `app.py`.
Erreichbar dann unter http://127.0.0.1:8080.

### Variante B — Lokal (klassisch ohne uv)

```bash
python -m venv .venv
.venv/bin/activate  # bzw. .venv\Scripts\activate auf Windows
pip install -r requirements.txt
python app.py
```

### Variante C — Production (Docker + Reverse Proxy)

```bash
docker compose up -d --build
```

Container läuft dann mit gunicorn auf Port 8080 im Docker-Netz `web-proxy`
(externes Netz, muss existieren — siehe `docker-compose.yml`). Reverse Proxy
(Nginx, Caddy, Traefik) auf den Container-Port routen, TLS via Let's Encrypt.

Health-Check Endpoint:
```
GET /health
→ {"status":"ok","causes":81,"year_min":1980,"year_max":2024,"age_years":45}
```

## Daten aktualisieren

Destatis veröffentlicht jährlich (ca. November/Dezember). Update-Workflow:

1. Auf [GENESIS-Online 23211-0001](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0001) gehen
   - Werteansicht: alle Jahre, beide Geschlechter + Insgesamt, alle Todesursachen
   - Format: **Excel (.xlsx)**, Sprache **Deutsch**
   - Datei als `data/23211-0001_de.xlsx` ablegen
2. Dasselbe für [Tabelle 23211-0002](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0002) (mit Altersgruppen)
3. Container neu starten: `docker compose restart` (das `data/`-Volume wird neu eingelesen,
   kein Rebuild nötig)

Der Parser ist robust gegen kleine Layout-Änderungen (sucht Header-Zeilen anhand
Content-Match wie „männlich" / „unter 1 Jahr"), nicht anhand fester Zeilenindizes.

## Architektur

```
.
├── app.py                — Dash-App: Loader + Layout + Callbacks + Health-Endpoint
│                           Detaillierter Changelog im File-Header (Zeilen 1–145)
├── requirements.txt      — Python-Deps (pinned major)
├── data/
│   ├── 23211-0001_de.xlsx — Jahres-Daten 1980–2024
│   └── 23211-0002_de.xlsx — Alters-Daten 1980–2024
├── Dockerfile            — Production-Image (python:3.12-slim + gunicorn)
├── docker-compose.yml    — Service-Block (read-only Daten-Volume, 384MB limit)
├── run_local.sh / .bat   — uv-Starter für lokale Entwicklung
├── CITATION.cff          — Zitierangaben
├── DATA-LICENSE          — Datenlizenz Destatis
└── README.md             — diese Datei
```

## Lizenz

- Code: MIT (siehe Git-History für Autorschaft)
- Daten: siehe `DATA-LICENSE` (Destatis-Datenlizenz)

## Quellen

- Statistisches Bundesamt: Tabellen [23211-0001](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0001) + [23211-0002](https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0002)
- Plotly Dash: [dash.plotly.com](https://dash.plotly.com/)
- Original-Repo-Historie (educx-Abschluss 09/2025): siehe `git log`

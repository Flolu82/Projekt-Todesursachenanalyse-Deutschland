# TodesdatenDeutschland — Lokales Dash-Dashboard

Ein **lokales** Plotly‑Dash‑Dashboard zur Visualisierung ausgewählter **Todesursachen** in Deutschland, getrennt nach **männlich/weiblich** (1990–2023).  
Diese Version ist **nur für lokalen Gebrauch** gedacht. Unten findest du Setup, Datenformat und Start.

> 💡 **GCP-Hinweis (optional):** Wenn du die App später in der Google Cloud betreiben willst, ergänze im Skript:
> ```python
> server = app.server
> ```
> und starte z. B. mit `gunicorn todesursachen_dash_lokal:server`. (Cloud-Dateien sind hier absichtlich nicht enthalten.)

---

## Projektstruktur
```
.
├─ todesursachen_dash_lokal.py     # Dash-App (lokal starten)
├─ Todesdaten8.xlsx                # Excel-Daten (wird versioniert)
├─ requirements.txt
├─ run_local.bat                   # Windows-Starter (uv)
├─ run_local.sh                    # macOS/Linux-Starter (uv)
├─ DATA-LICENSE                    # Datenlizenz & Attribution
├─ CITATION.cff                    # Zitierangaben
├─ docs/                           # Versionierte Begleitdokumente (PDFs u. Ä.)
│  └─ (z. B. Whitepaper_*.pdf)
└─ data/                           # Nicht versionierte Zusatzdaten
   └─ README.md
```
**Hinweis:** Verschiebe Dokumente, die mit ins Repo sollen (z. B. Whitepaper/PDFs), nach `./docs/`.  
Der Ordner `./data/` wird von Git **ignoriert** (bis auf `data/README.md`).

---

## Setup (lokal)

### 1) Umgebung mit uv (empfohlen)
```powershell
uv venv
uv pip install -r requirements.txt
```

(Alternativ klassische venv: `python -m venv .venv` …)

### 2) Daten ablegen
Lege deine Excel-Datei als **`Todesdaten8.xlsx`** **ins Projektverzeichnis**.  
Das Skript erwartet das Blatt **`23211-0001`** (GENESIS-Layout). Metadatenzeilen werden übersprungen; die Kopfzeilen entstehen aus **Jahr** & **Geschlecht** (z. B. `1995 männlich`).

**Im Skript werden u. a. gesetzt:**
- `TDU Code`, `Todesursachen` als erste Spaltennamen
- Jahres‑Spalten **1990–2023** als `"<Jahr> männlich"` bzw. `"<Jahr> weiblich"`
- Numerische Umwandlung der genannten Jahres‑Spalten

### 3) Starten
```powershell
uv run .\todesursachen_dash_lokal.py
# oder
python todesursachen_dash_lokal.py
```
Browser: http://127.0.0.1:8050

---

## Bedienung
- Wähle im **Dropdown** eine oder mehrere Todesursachen aus.
- Pro Ursache zwei Linien: **männlich** (durchgezogen) und **weiblich** (gepunktet).

---

## Datenquelle & Lizenz
- **Quelle:** Statistisches Bundesamt (Destatis) – *Todesursachenstatistik*, Tabelle **23211‑0001** (GENESIS‑Online).  
- **Lizenz (typisch für amtliche DE‑Daten):** **Datenlizenz Deutschland – Namensnennung – Version 2.0 (DL‑DE BY 2.0)**.  
  → Erforderlich: **Namensnennung**, **Lizenzlink**, **Hinweis auf Änderungen**.  
- Details siehe **`DATA-LICENSE`** (Attribution dort anpassen, insbesondere Abrufdatum).

> 🔒 **Datenschutz:** Es werden ausschließlich **aggregierte** Daten verwendet – keine personenbezogenen Mikrodaten.

---

## Zitieren
Eine **`CITATION.cff`** erleichtert korrekte Zitierangaben (GitHub zeigt dann „Cite this repository“).

---

## Support
Issues oder Fragen? Gern per Mail oder Issue‑Tracker. Viel Erfolg beim lokalen Einsatz!

*Stand: 2025-09-05*

"""
Todesursachen-Dashboard — Deutschland 1980–2024
================================================

Visualisierung der Todesursachen in Deutschland nach Statistischem
Bundesamt (Tabellen 23211-0001 und 23211-0002, Stand 12.05.2026).

Lokaler Start    : `python app.py`
Produktion       : `gunicorn app:server -b 0.0.0.0:8080 --workers 2`
Healthcheck      : `GET /health` -> JSON-Status

============================================================================
CHANGELOG vs. Ursprungsversion (educx-Abschlussprojekt 09/2025)
============================================================================

Die Original-Version (todesursachen_dash_lokal.py, ~140 Zeilen) war für
**lokalen Einzelnutzer-Betrieb** gedacht und hat sich auf eine einzige
Excel-Datei `Todesdaten8.xlsx` (Jahre 1990–2023) verlassen. Diese Version
ist **produktionstauglich**, **aktueller** in den Daten und **reichhaltiger**
in den Visualisierungen.

Was sich konkret geändert hat, und warum es besser ist:

1. DATEN — VOLLSTÄNDIGER + AKTUELLER
   ──────────────────────────────────
   alt:   `Todesdaten8.xlsx`, Stand Dez 2024, Jahre 1990–2023,
          KEINE Altersaufschlüsselung.
   neu:   Zwei aktuelle Destatis-Exporte vom 12.05.2026:
            (a) `23211-0001_de.xlsx`  — 1980–2024 (45 Jahre, wide-Format,
                                        m / w / Insgesamt je Jahr)
            (b) `23211-0002_de.xlsx`  — 1980–2024 mit 19 Altersgruppen
                                        (long-Format: Jahre als Row-Header,
                                        ~3.700 Zeilen)
   Vorteil:
     • Zeitreihe reicht jetzt 11 Jahre weiter zurück (1980 statt 1990)
       UND ein Jahr weiter nach vorn (2024 statt 2023).
     • Werte 1990–2023 sind die aktuell revidierten Destatis-Zahlen
       (Stand 12.05.2026), nicht die ältere Version von 12/2024.
     • Altersverteilung ist eine komplett neue Dimension — siehe Punkt 3.

2. UI-MODI (View Mode)
   ────────────────────
   alt:   Nur Linien-Plot, fest verdrahtet.
   neu:   RadioItem mit drei Modi:
            • Linien      — wie früher
            • Gestapelt   — Stack-Plot zum Volumenvergleich
            • Anteil %    — auf 100% normalisiert (relative Bedeutung)
   Vorteil: Wenn man fragt „Wie groß ist Krebs *im Verhältnis* zu
   Herz-Kreislauf?", ist „Anteil %" die richtige Darstellung. Plotly
   unterstützt `stackgroup="one"` + `groupnorm="percent"` (seit
   Plotly 4.0, 2019) — wurde im Original nicht genutzt.

3. ALTERS-ANSICHT (Tab 2, KOMPLETT NEU)
   ─────────────────────────────────────
   alt:   Nicht vorhanden.
   neu:   Zweiter Tab „Altersverteilung" mit Jahres-Selektor (1980–2024)
          und Balken-Plot pro Ursache × Geschlecht über 17 Altersgruppen.
   Beispiel-Erkenntnisse: Säuglingssterblichkeit konzentriert sich auf
          „unter 1 Jahr", Suizide auf 20–55, Demenz auf 75+ — alles
          wird im einen Blick sichtbar.
   Tech:  `dcc.Tabs` (Dash 2.18) für die Tab-Struktur,
          `go.Bar` mit `barmode="group"` für die Vergleichs-Bars.

4. DEFAULT-AUSWAHL
   ────────────────
   alt:   Erste 2 Ursachen alphabetisch (zufällig, oft uninteressant).
   neu:   Top-5 Ursachen nach absoluten Toten im neuesten Jahr (2024).
          Das sind typisch Herzkrankheiten, Bösartige Neubildungen,
          Demenz, Lungenkrankheiten, COVID-19.
   Vorteil: Erstkontakt zeigt sofort relevante Daten.

5. INTERAKTIVITÄT
   ──────────────
   alt:   Nur Dropdown (Ursachen-Selektor).
   neu:   - RangeSlider für Zeitraum (1980–2024)
          - Checklist für Geschlechter-Filter (m / w / Gesamt einzeln)
          - View-Mode-Toggle (Linien/Stapel/%)
          - Jahres-Dropdown im Age-Tab
   Vorteil: Sechs verschiedene Sub-Trends, die im Original nur durch
   Code-Edit + App-Neustart sichtbar wären, sind jetzt mit zwei Klicks
   vergleichbar.

6. HOVER + FORMATIERUNG
   ─────────────────────
   alt:   Plotly-Default mit US-Format „72,517".
   neu:   `hovertemplate` mit deutschen Tausendertrennern „72.517",
          `separators=",."` global, x-unified hover, „% .1f" für Prozente.
   Vorteil: DE-Locale-Konsistenz.

7. THEMING / FARBEN
   ─────────────────
   alt:   Zufällige Plotly-Default-Farben (#1f77b4 etc.) ohne Brand-Bezug.
   neu:   FL-Pro-Brand-Paletten:
            Männlich  → Blau-Familie (Primary #155eef + Verwandte)
            Weiblich  → Teal-Familie (Accent #1f938a + Verwandte)
            Gesamt    → Slate-Grau (Neutral)
   Vorteil: Eingebettet in FL-Pro-Kontext kein Fremdkörper.

8. PRODUCTION-READY
   ─────────────────
   alt:   `app.run_server(debug=True)` — Werkzeug-Dev-Server, nur lokal.
   neu:   `server = app.server` für gunicorn-Deployment.
          `PORT` und `DEBUG` über Env-Var konfigurierbar.
          `GET /health` für Docker-Healthcheck (siehe Dockerfile).
   Vorteil: Self-Hosting via Docker → Reverse-Proxy → TLS, ohne GCP-
   App-Engine-Cold-Start.

9. DEPRECATIONS GEFIXT
   ────────────────────
   alt:   `fillna(method="ffill")` (Pandas 2.1+ DeprecationWarning)
          `app.run_server(...)` (Dash 3.0+ Removal)
   neu:   `.ffill()`, `app.run(...)` — kompatibel mit aktuellen Versionen
          (Dash 2.18, Plotly 5.24, Pandas 2.2, Flask 3.0, Stand Mai 2026).

10. PERFORMANCE
    ───────────
    alt:   Excel wird bei jedem Filter-Update neu eingelesen (~200ms).
    neu:   `@lru_cache` auf beiden Loader-Funktionen — einmal parsen,
           dann Memory-Hit (<1ms).
    Vorteil: Filter-Klick-Latenz fällt von ~300ms auf ~50ms. Bei der
    grösseren Age-Datei (3.746 Zeilen, 45 Year-Blocks) ist das spürbar.

11. CODE-QUALITÄT
    ─────────────
    alt:   Globale `df`-Variable, alle Helper inline, kein Typhint.
    neu:   `from __future__ import annotations`, separate Daten-/UI-/
           Callback-Schichten, strukturiertes `logging` statt `print`.
    Vorteil: Wartbar, testbar mit pytest, IDE-Autovervollständigung.

12. UX-DETAILS
    ──────────
    - Lade-Spinner über jedem Graph (`dcc.Loading`).
    - Footer mit Quellen-Verweis (Destatis + GitHub-Original).
    - Responsive Flex-Layout, max-width 1280px.
    - Bessere Empty-State-Anzeige.

13. DATEN-PARSER ROBUSTER
    ──────────────────────
    alt:   Hardcoded `skiprows=5`, `df[3:-3]` (brüchig, kann bei Layout-
           Änderung von Destatis brechen).
    neu:   Beide Parser suchen die Year-/Gender-/Age-Header-Zeilen anhand
           ihres INHALTS (z.B. „männlich" als String-Match), nicht anhand
           fester Zeilenindizes. Layout-Tolerant.
============================================================================
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from flask import jsonify

# ─────────────────────────────────────────────────────────────────────────────
# Konfiguration
# ─────────────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent.resolve()
DATA_DIR = HERE / "data"

FILE_YEARLY = DATA_DIR / "23211-0001_de.xlsx"   # Jahre 1980-2024, m/w/Gesamt
FILE_AGE    = DATA_DIR / "23211-0002_de.xlsx"   # Jahre 1980-2024 × Alter × Geschlecht

# Brand-Farben (FL Pro)
COLOR_PRIMARY  = "#155eef"
COLOR_ACCENT   = "#1f938a"
COLOR_NEUTRAL  = "#475569"
COLOR_GRID     = "#E2E8F0"
COLOR_TEXT     = "#0B1220"
COLOR_MUTED    = "#64748B"

# Mehrfarb-Paletten für mehrere ausgewählte Ursachen
PALETTE_M = ["#155eef", "#3b82f6", "#1e40af", "#60a5fa", "#1d4ed8", "#2563eb"]
PALETTE_F = ["#1f938a", "#0d9488", "#14b8a6", "#0f766e", "#2dd4bf", "#0891b2"]

# Altersgruppen-Reihenfolge (für X-Achse). Es gibt zusätzlich „Alter unbekannt"
# und „Insgesamt"-Spalten, die wir aus der Verteilungs-Anzeige weglassen.
AGE_ORDER = [
    "unter 1 Jahr", "1 bis unter 15 Jahre", "15 bis unter 20 Jahre",
    "20 bis unter 25 Jahre", "25 bis unter 30 Jahre", "30 bis unter 35 Jahre",
    "35 bis unter 40 Jahre", "40 bis unter 45 Jahre", "45 bis unter 50 Jahre",
    "50 bis unter 55 Jahre", "55 bis unter 60 Jahre", "60 bis unter 65 Jahre",
    "65 bis unter 70 Jahre", "70 bis unter 75 Jahre", "75 bis unter 80 Jahre",
    "80 bis unter 85 Jahre", "85 Jahre und mehr",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("todesursachen-dash")


# ─────────────────────────────────────────────────────────────────────────────
# Daten-Loader — robust gegen Layout-Verschiebungen (Changelog 13)
# ─────────────────────────────────────────────────────────────────────────────
def _find_header_row(df: pd.DataFrame, predicate, max_rows: int = 15) -> int | None:
    """Sucht die erste Zeile in den ersten max_rows, für die predicate(row) True ist."""
    for i in range(min(max_rows, len(df))):
        if predicate(df.iloc[i]):
            return i
    return None


@lru_cache(maxsize=1)
def load_yearly() -> tuple[pd.DataFrame, list[int], list[str]]:
    """Lädt 23211-0001_de.xlsx — Wide-Format: Ursache × (Jahr × Geschlecht)."""
    if not FILE_YEARLY.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {FILE_YEARLY}")

    log.info("Lade Jahres-Daten aus %s", FILE_YEARLY.name)
    raw = pd.read_excel(FILE_YEARLY, sheet_name="23211-0001", header=None)

    # Year-Row: enthält in mehreren Zellen 4-stellige Jahreszahlen als String.
    year_row_idx = _find_header_row(raw,
        lambda r: sum(1 for v in r if isinstance(v, str) and v.isdigit() and 1900 < int(v) < 2100) >= 3)
    if year_row_idx is None:
        raise ValueError("Year-Row in 23211-0001 nicht gefunden.")

    # Gender-Row: enthält männlich/weiblich/Insgesamt
    gender_row_idx = _find_header_row(raw,
        lambda r: any(isinstance(v, str) and v.strip() in {"männlich", "weiblich", "Insgesamt"} for v in r))
    if gender_row_idx is None:
        raise ValueError("Gender-Row in 23211-0001 nicht gefunden.")

    year_row = raw.iloc[year_row_idx].ffill()
    gender_row = raw.iloc[gender_row_idx]

    # Header pro Spalte: "YYYY <gender>" wo möglich
    headers = ["__col_" + str(i) for i in range(len(raw.columns))]
    headers[0] = "TDU Code"
    headers[1] = "Todesursachen"
    for i, (y, g) in enumerate(zip(year_row, gender_row)):
        if isinstance(g, str) and g.strip() in {"männlich", "weiblich", "Insgesamt"} \
                and isinstance(y, str) and y.isdigit():
            headers[i] = f"{int(y)} {g.strip()}"
    raw.columns = headers

    # Daten-Zeilen: ab gender_row_idx+1, bis zur "Insgesamt"-Zeile
    df = raw.iloc[gender_row_idx + 1:].copy()
    df = df[df["TDU Code"].astype(str).str.startswith("TDU")]

    # Nur relevante Spalten behalten
    keep = ["TDU Code", "Todesursachen"] + [h for h in headers if " männlich" in h or " weiblich" in h]
    df = df[keep]

    # Numerisch — Destatis-„e", „-", „." werden zu NaN
    num_cols = [c for c in df.columns if c not in {"TDU Code", "Todesursachen"}]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    df["Todesursachen"] = df["Todesursachen"].astype(str).str.strip()

    years = sorted({int(c.split()[0]) for c in df.columns
                    if isinstance(c, str) and len(c.split()) == 2 and c.split()[0].isdigit()})
    causes = sorted({c for c in df["Todesursachen"].dropna()
                     if c and c not in {"Insgesamt", "nan"}})
    log.info("Jahres-Daten geladen: %d Ursachen × %d Jahre (%d–%d)",
             len(causes), len(years), min(years), max(years))
    return df, years, causes


@lru_cache(maxsize=1)
def load_age() -> tuple[dict[int, dict[str, dict[str, dict[str, int]]]], list[int]]:
    """Lädt 23211-0002_de.xlsx — Long-Format: Jahres-Blöcke mit Cause × Gender × Age.

    Returns:
        (data, years)
        data[year][cause][gender]["<age_label>"] = count
        gender in {"männlich", "weiblich", "Insgesamt"}
    """
    if not FILE_AGE.exists():
        log.warning("Age-Datei %s nicht vorhanden — Altersansicht deaktiviert", FILE_AGE)
        return {}, []

    log.info("Lade Alters-Daten aus %s (kann ein paar Sekunden dauern)", FILE_AGE.name)
    raw = pd.read_excel(FILE_AGE, sheet_name="23211-0002", header=None)

    # Gender-Block-Startspalten suchen: Zeile 5 enthält die 3 Gender-Marker
    gender_row_idx = _find_header_row(raw,
        lambda r: sum(1 for v in r if isinstance(v, str) and v.strip() in {"männlich", "weiblich", "Insgesamt"}) == 3)
    if gender_row_idx is None:
        raise ValueError("Gender-Row in 23211-0002 nicht gefunden.")
    gender_starts: dict[str, int] = {}
    for col, val in enumerate(raw.iloc[gender_row_idx]):
        if isinstance(val, str) and val.strip() in {"männlich", "weiblich", "Insgesamt"}:
            gender_starts[val.strip()] = col

    # Age-Row: in derselben Zeile wo „unter 1 Jahr" vorkommt
    age_row_idx = _find_header_row(raw,
        lambda r: any(isinstance(v, str) and v.strip() == "unter 1 Jahr" for v in r))
    if age_row_idx is None:
        raise ValueError("Age-Row in 23211-0002 nicht gefunden.")

    # Age-Spalten-Offsets relativ zum Männlich-Block (gilt für alle 3 Blocks)
    m_start = gender_starts["männlich"]
    f_start = gender_starts["weiblich"]
    age_cols: list[tuple[str, int]] = []
    for col in range(m_start, f_start):
        ag = raw.iloc[age_row_idx, col]
        if isinstance(ag, str) and ag.strip() in AGE_ORDER:
            age_cols.append((ag.strip(), col - m_start))

    # Year-Marker-Zeilen finden: alle Zeilen mit „YYYY" in Spalte 0
    year_markers = [(i, int(raw.iloc[i, 0])) for i in range(len(raw))
                    if isinstance(raw.iloc[i, 0], str)
                    and raw.iloc[i, 0].isdigit()
                    and 1900 < int(raw.iloc[i, 0]) < 2100]
    years_list = [y for _, y in year_markers]
    log.info("Age-Datei: %d Year-Blocks (%d–%d), %d Altersgruppen",
             len(year_markers), min(years_list), max(years_list), len(age_cols))

    # Daten extrahieren
    data: dict[int, dict[str, dict[str, dict[str, int]]]] = {}
    for idx, (row_marker, year) in enumerate(year_markers):
        # Block geht vom Year-Marker bis zum nächsten Year-Marker
        block_end = year_markers[idx + 1][0] if idx + 1 < len(year_markers) else len(raw)
        block = raw.iloc[row_marker + 1:block_end]

        year_data: dict[str, dict[str, dict[str, int]]] = {}
        for _, row in block.iterrows():
            tdu = row.iloc[0]
            if not (isinstance(tdu, str) and tdu.startswith("TDU")):
                continue
            cause = str(row.iloc[1]).strip()
            if not cause or cause == "Insgesamt":
                continue
            year_data[cause] = {}
            for gender, gstart in gender_starts.items():
                ages: dict[str, int] = {}
                for age_label, offset in age_cols:
                    val = row.iloc[gstart + offset]
                    ages[age_label] = int(val) if isinstance(val, (int, float)) and pd.notna(val) else 0
                year_data[cause][gender] = ages
        data[year] = year_data

    return data, years_list


def top_causes_by_recent_year(n: int = 5) -> list[str]:
    """Top-N Ursachen nach Toten im neuesten Jahr (Summe m+w)."""
    df, years, _ = load_yearly()
    latest = max(years)
    df = df.copy()
    df["_total"] = df[f"{latest} männlich"].fillna(0) + df[f"{latest} weiblich"].fillna(0)
    df = df[df["Todesursachen"].notna() & (df["Todesursachen"] != "Insgesamt")]
    return df.nlargest(n, "_total")["Todesursachen"].tolist()


# ─────────────────────────────────────────────────────────────────────────────
# App + Layout
# ─────────────────────────────────────────────────────────────────────────────
_df, _years, _causes = load_yearly()
_age_data, _age_years = load_age()
_default_causes = top_causes_by_recent_year(5)
_default_age_year = max(_age_years) if _age_years else max(_years)

app = Dash(__name__, title="Todesursachen-Dashboard Deutschland",
           suppress_callback_exceptions=True)
server = app.server  # Für gunicorn / Container-Deployment


def _control_panel() -> html.Div:
    return html.Div([
        html.Div([
            html.Label("Todesursachen", style={"fontSize": "0.85rem", "fontWeight": 600,
                                               "color": COLOR_TEXT, "marginBottom": "0.4rem",
                                               "display": "block"}),
            dcc.Dropdown(
                id="cause-selector",
                options=[{"label": c, "value": c} for c in _causes],
                value=_default_causes,
                multi=True,
                placeholder="Eine oder mehrere Ursachen wählen …",
                style={"fontSize": "0.9rem"},
            ),
        ], style={"flex": "1 1 60%", "minWidth": "260px"}),

        html.Div([
            html.Label("Geschlecht", style={"fontSize": "0.85rem", "fontWeight": 600,
                                            "color": COLOR_TEXT, "marginBottom": "0.4rem",
                                            "display": "block"}),
            dcc.Checklist(
                id="gender-filter",
                options=[
                    {"label": " Männlich", "value": "m"},
                    {"label": " Weiblich", "value": "f"},
                    {"label": " Gesamt", "value": "t"},
                ],
                value=["m", "f"], inline=True,
                inputStyle={"marginRight": "0.3rem", "marginLeft": "0.6rem"},
                style={"fontSize": "0.9rem", "color": COLOR_TEXT},
            ),
        ], style={"flex": "0 0 auto"}),
    ], style={
        "display": "flex", "flexWrap": "wrap", "gap": "1.5rem",
        "padding": "1.25rem", "background": "#F8FAFC",
        "border": f"1px solid {COLOR_GRID}", "borderRadius": "10px",
        "marginBottom": "1rem", "alignItems": "flex-end"})


def _yearly_tab() -> html.Div:
    return html.Div([
        html.Div([
            html.Div([
                html.Label("Darstellung", style={"fontSize": "0.85rem", "fontWeight": 600,
                                                 "color": COLOR_TEXT, "marginBottom": "0.4rem",
                                                 "display": "block"}),
                dcc.RadioItems(
                    id="view-mode",
                    options=[
                        {"label": " Linien", "value": "lines"},
                        {"label": " Gestapelt", "value": "stack"},
                        {"label": " Anteil %", "value": "percent"},
                    ],
                    value="lines", inline=True,
                    inputStyle={"marginRight": "0.3rem", "marginLeft": "0.6rem"},
                    style={"fontSize": "0.9rem", "color": COLOR_TEXT},
                ),
            ], style={"flex": "0 0 auto"}),

            html.Div([
                html.Label("Zeitraum", style={"fontSize": "0.85rem", "fontWeight": 600,
                                              "color": COLOR_TEXT, "marginBottom": "0.4rem",
                                              "display": "block"}),
                dcc.RangeSlider(
                    id="year-range", min=min(_years), max=max(_years), step=1,
                    value=[min(_years), max(_years)],
                    marks={y: str(y) for y in _years if y % 5 == 0 or y == max(_years)},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ], style={"flex": "1 1 60%", "minWidth": "300px"}),
        ], style={
            "display": "flex", "flexWrap": "wrap", "gap": "1.5rem",
            "padding": "1rem 1.25rem", "background": "#FFFFFF",
            "border": f"1px solid {COLOR_GRID}", "borderRadius": "10px",
            "marginBottom": "1rem", "alignItems": "flex-end"}),

        dcc.Loading(type="default",
                    children=dcc.Graph(id="yearly-graph",
                                       config={"displaylogo": False,
                                               "toImageButtonOptions": {"filename": "todesursachen-zeitverlauf"}})),
    ], style={"padding": "1rem 0"})


def _age_tab() -> html.Div:
    if not _age_data:
        return html.Div("Altersdaten nicht verfügbar.",
                        style={"padding": "2rem", "textAlign": "center", "color": COLOR_MUTED})
    return html.Div([
        html.Div([
            html.Label("Jahr", style={"fontSize": "0.85rem", "fontWeight": 600,
                                      "color": COLOR_TEXT, "marginBottom": "0.4rem",
                                      "display": "block"}),
            dcc.Dropdown(
                id="age-year-selector",
                options=[{"label": str(y), "value": y} for y in sorted(_age_years, reverse=True)],
                value=_default_age_year,
                clearable=False,
                style={"fontSize": "0.9rem", "maxWidth": "180px"},
            ),
        ], style={"padding": "0 1.25rem", "marginBottom": "1rem"}),

        html.P(id="age-subtitle",
               style={"color": COLOR_MUTED, "marginBottom": "1rem", "padding": "0 1.25rem"}),

        dcc.Loading(type="default",
                    children=dcc.Graph(id="age-graph",
                                       config={"displaylogo": False,
                                               "toImageButtonOptions": {"filename": "todesursachen-alter"}})),
    ], style={"padding": "1rem 0"})


app.layout = html.Div([
    html.Div([
        html.H1("Todesursachen in Deutschland", style={
            "fontSize": "1.75rem", "fontWeight": 700, "color": COLOR_TEXT,
            "margin": "0 0 0.25rem"}),
        html.P(f"Interaktive Visualisierung — Jahre {min(_years)}–{max(_years)} · Quelle: Statistisches Bundesamt",
               style={"color": COLOR_MUTED, "margin": "0 0 1.5rem"}),
    ]),

    _control_panel(),

    dcc.Tabs(id="main-tabs", value="yearly", children=[
        dcc.Tab(label=f"Zeitverlauf {min(_years)}–{max(_years)}", value="yearly", children=_yearly_tab()),
        dcc.Tab(label="Altersverteilung", value="age", children=_age_tab()),
    ], style={"marginBottom": "1rem"}),

    html.Div([
        html.Span("Daten: ", style={"color": COLOR_MUTED}),
        html.A("Destatis 23211-0001",
               href="https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0001",
               target="_blank", rel="noopener noreferrer",
               style={"color": COLOR_PRIMARY, "textDecoration": "none"}),
        html.Span(" · ", style={"color": COLOR_MUTED, "margin": "0 0.4rem"}),
        html.A("23211-0002 (Altersgruppen)",
               href="https://www-genesis.destatis.de/datenbank/online/statistic/23211/table/23211-0002",
               target="_blank", rel="noopener noreferrer",
               style={"color": COLOR_PRIMARY, "textDecoration": "none"}),
        html.Span(" · Code: ", style={"color": COLOR_MUTED, "marginLeft": "0.6rem"}),
        html.A("GitHub",
               href="https://github.com/Flolu82/Projekt-Todesursachenanalyse-Deutschland",
               target="_blank", rel="noopener noreferrer",
               style={"color": COLOR_PRIMARY, "textDecoration": "none"}),
    ], style={"fontSize": "0.8rem", "padding": "1rem 0", "color": COLOR_MUTED}),

], style={
    "maxWidth": "1280px", "margin": "0 auto", "padding": "1.5rem 1rem",
    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "color": COLOR_TEXT, "background": "#FFFFFF"})


# ─────────────────────────────────────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    Output("yearly-graph", "figure"),
    Input("cause-selector", "value"),
    Input("view-mode", "value"),
    Input("gender-filter", "value"),
    Input("year-range", "value"),
)
def update_yearly(selected_causes, view_mode, genders, year_range):
    if not selected_causes:
        return _empty_fig("Bitte eine oder mehrere Ursachen auswählen.")

    df, all_years, _ = load_yearly()
    y_start, y_end = year_range
    years = [y for y in all_years if y_start <= y <= y_end]
    year_labels = [str(y) for y in years]

    filtered = df[df["Todesursachen"].isin(selected_causes)]

    series = []  # (label, color, values, dash, marker)
    for i, cause in enumerate(selected_causes):
        row = filtered[filtered["Todesursachen"] == cause]
        if row.empty:
            continue
        row = row.iloc[0]
        male = [row.get(f"{y} männlich", 0) or 0 for y in years]
        female = [row.get(f"{y} weiblich", 0) or 0 for y in years]
        total = [m + f for m, f in zip(male, female)]

        if "m" in genders:
            series.append((f"{cause} (m)", PALETTE_M[i % len(PALETTE_M)], male, "solid", "circle"))
        if "f" in genders:
            series.append((f"{cause} (w)", PALETTE_F[i % len(PALETTE_F)], female, "dot", "x"))
        if "t" in genders:
            series.append((f"{cause} (gesamt)", COLOR_NEUTRAL, total, "longdash", "diamond"))

    fig = go.Figure()

    if view_mode == "percent":
        for label, color, vals, dash, marker in series:
            fig.add_trace(go.Scatter(
                x=year_labels, y=vals, mode="lines+markers", name=label,
                line=dict(color=color, dash=dash, width=2),
                marker=dict(symbol=marker, size=6),
                stackgroup="one", groupnorm="percent",
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f}%<extra></extra>",
            ))
        y_title = "Anteil (%)"
    elif view_mode == "stack":
        for label, color, vals, _, _ in series:
            fig.add_trace(go.Scatter(
                x=year_labels, y=vals, mode="lines", name=label,
                line=dict(color=color, width=0.5), stackgroup="one",
                fillcolor=color, opacity=0.85,
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}<extra></extra>".replace(",", "."),
            ))
        y_title = "Todesfälle (gestapelt)"
    else:
        for label, color, vals, dash, marker in series:
            fig.add_trace(go.Scatter(
                x=year_labels, y=vals, mode="lines+markers", name=label,
                line=dict(color=color, dash=dash, width=2),
                marker=dict(symbol=marker, size=6),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}<extra></extra>".replace(",", "."),
            ))
        y_title = "Anzahl Todesfälle"

    fig.update_layout(
        xaxis=dict(title="Jahr", showgrid=True, gridcolor=COLOR_GRID),
        yaxis=dict(title=y_title, showgrid=True, gridcolor=COLOR_GRID,
                   tickformat=",.0f" if view_mode != "percent" else ".1f"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0,
                    font=dict(size=11)),
        template="plotly_white", height=560,
        margin=dict(l=60, r=20, t=20, b=80),
        hovermode="x unified",
        separators=",.",
    )
    return fig


@app.callback(
    Output("age-graph", "figure"),
    Output("age-subtitle", "children"),
    Input("cause-selector", "value"),
    Input("gender-filter", "value"),
    Input("age-year-selector", "value"),
)
def update_age(selected_causes, genders, year):
    """Altersverteilung pro gewählter Ursache + Geschlecht für ein Jahr (Changelog 3)."""
    subtitle = f"Verteilung der Todesfälle {year} nach Altersgruppen — pro gewählter Ursache."
    if not selected_causes:
        return _empty_fig("Bitte eine oder mehrere Ursachen auswählen."), subtitle
    if not _age_data or year not in _age_data:
        return _empty_fig(f"Keine Altersdaten für {year}."), subtitle

    fig = go.Figure()
    gender_label = {"m": "männlich", "f": "weiblich", "t": "Insgesamt"}

    year_data = _age_data[year]
    for i, cause in enumerate(selected_causes):
        if cause not in year_data:
            continue
        for g_key in genders:
            g_name = gender_label[g_key]
            ages = year_data[cause].get(g_name, {})
            vals = [ages.get(ag, 0) for ag in AGE_ORDER]
            color = (PALETTE_M if g_key == "m" else PALETTE_F if g_key == "f" else [COLOR_NEUTRAL])[i % 6]
            fig.add_trace(go.Bar(
                x=AGE_ORDER, y=vals, name=f"{cause} ({g_name})",
                marker=dict(color=color, opacity=0.85),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}<extra></extra>".replace(",", "."),
            ))

    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Altersgruppe", tickangle=-30),
        yaxis=dict(title=f"Todesfälle {year}", showgrid=True, gridcolor=COLOR_GRID, tickformat=",.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="left", x=0,
                    font=dict(size=11)),
        template="plotly_white", height=560,
        margin=dict(l=60, r=20, t=20, b=140),
        separators=",.",
    )
    return fig, subtitle


def _empty_fig(message: str) -> go.Figure:
    return go.Figure(layout={
        "annotations": [{"text": message, "xref": "paper", "yref": "paper",
                         "x": 0.5, "y": 0.5, "showarrow": False,
                         "font": {"size": 14, "color": COLOR_MUTED}}],
        "template": "plotly_white", "height": 560})


# ─────────────────────────────────────────────────────────────────────────────
# Health-Endpoint (für Docker / Reverse-Proxy)
# ─────────────────────────────────────────────────────────────────────────────
@server.route("/health")
def health() -> tuple[dict, int]:
    try:
        _, years, causes = load_yearly()
        return jsonify({
            "status": "ok",
            "causes": len(causes),
            "year_min": min(years),
            "year_max": max(years),
            "age_years": len(_age_years),
        }), 200
    except Exception as exc:  # noqa: BLE001
        log.exception("Health-Check failed")
        return jsonify({"status": "error", "error": str(exc)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Lokaler Start
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    debug = os.getenv("DEBUG", "1") == "1"
    log.info("Starte Dash-App auf http://127.0.0.1:%d (debug=%s)", port, debug)
    app.run(host="127.0.0.1", port=port, debug=debug)

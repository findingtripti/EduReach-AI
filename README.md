# EduReach AI

An exploratory AI/ML and GIS decision-support dashboard that looks at **government-school accessibility** for villages in **Jamunaha block, Shravasti district, Uttar Pradesh**. It is an early-stage academic prototype, not an official or validated tool.

**Idea:** a school that is close on the map is not automatically accessible, and some villages have no recorded local school. EduReach AI scores each village with a transparent index, groups villages with an unsupervised model, shows them on a map, explains each score, and lets you try *hypothetical* interventions.

## Features

- KPI cards, sidebar filters (accessibility status, local-school record) that update every card, chart, map and table
- Village map (folium) coloured by status, with a popup and tooltip per village
- Accessibility analytics and ML pattern distribution, plus an "ML model diagnostics" panel (BIC/AIC, seed stability, reproducibility)
- "Why Is This Village Flagged?" panel: weighted score contributions that reconstruct the stored index
- Intervention scenario simulator: baseline vs hypothetical, user-chosen assumptions, village-wise comparison
- Built-in data checks (missing columns, duplicates, invalid coordinates, score bounds)

## Folder structure

```
app.py                      Streamlit dashboard
edureach_core.py            data loading, validation, scoring, explanation, scenarios, ML diagnostics
edureach_map.py             folium village map
edureach_dashboard.csv      dashboard dataset (115 villages)
requirements.txt            runtime dependencies
requirements-dev.txt        + pytest, openpyxl
.streamlit/config.toml      light theme
tests/                      pytest suite
docs/                       report, methodology, data dictionary, testing report, viva Q&A, lean canvas
*.py (other)                data-preparation scripts (see docs/METHODOLOGY.md)
*.csv, *.xlsx, *.geojson    intermediate and raw data used by those scripts
```

## Prerequisites

Python 3.10 or newer (developed and tested on 3.12). Internet access when viewing the map (map tiles and the Leaflet library are loaded from the web).

## Setup (Windows PowerShell)

```powershell
cd path\to\EduReach_AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

If script activation is blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## Light and dark theme

The dashboard has a light and a dark look. By default it follows your device or browser setting; you can switch System / Light / Dark from the ⋮ menu at the top right of the page. All cards, banners, tables and charts adapt to the active Streamlit theme. The map offers a **Light map / Dark map** switch (layers icon at the top right of the map); the dark map is the same OpenStreetMap data darkened with a CSS filter. To force one theme, replace the two `[theme.light]` / `[theme.dark]` sections in `.streamlit/config.toml` with:

```toml
[theme]
base = "dark"   # or "light"
primaryColor = "#3b82f6"
```

## Run the app

```powershell
python -m streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501). Keep `app.py` and `edureach_dashboard.csv` in the same folder.

## Run the tests

```powershell
python -m pytest tests -q
```

## Dataset requirements

`edureach_dashboard.csv` must contain the columns listed in `docs/DATA_DICTIONARY.md` (the app checks the required ones at start-up and shows a clear message if something is missing or invalid). Missing values are never filled silently.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt` |
| "edureach_dashboard.csv was not found" | Run from the project folder; the CSV must sit next to `app.py` |
| Map area is blank | Check your internet connection (Leaflet and tiles load from the web) |
| "Data check" error banner | Read the message; it names the column or problem in the CSV |
| Port already in use | `python -m streamlit run app.py --server.port 8502` |

## Limitations (read before using the results)

- Distances are **straight-line** estimates between village-level coordinates, not road distance or travel time.
- The Accessibility Index is a **project-defined indicator** (weights 40/40/20 chosen by the author), not a validated metric. In this data, "Potential Gap" coincides with "no recorded local school".
- Clusters are **unsupervised descriptive groups**, not validated predictions; `Has_School` is a model input.
- Scenarios are **hypothetical assumptions**, not forecasts. A new school is not modelled for capacity, staffing or feasibility.
- Villages and schools are matched by name; spelling differences can cause mismatches. No field validation has been done.
- Data freshness and the exact original sources of the raw files must be confirmed by the author (see `docs/DATA_DICTIONARY.md`).

## Attribution

Built by Tripti Singh as an academic AI/ML project. Raw data files come from public government reports/boundary files whose exact publisher, year and extraction date the author still needs to confirm. Libraries: Streamlit, pandas, NumPy, scikit-learn, folium, streamlit-folium. Map tiles: OpenStreetMap contributors.

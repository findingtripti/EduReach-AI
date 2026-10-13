# Testing Report

Everything below was actually run in the author's assistant workspace. Where something was **not** run or not visually checked, it says so.

## Environment

Python 3.12.3 (Linux), streamlit 1.65.0, pandas 3.0.2, scikit-learn 1.8.0, folium 0.20.0, streamlit-folium 0.27.4, pytest 9.1.1, Chromium 141 via Playwright. Windows with Python 3.11 was tested by the author (see "Run on the author's machine"). Python 3.14 was not tested.

## Commands executed

| Command | Result |
|---|---|
| `python -m py_compile app.py` | compiled without error |
| `python -m pytest tests -q` | see "Final run" below |
| `python -m streamlit run app.py --server.headless true --server.port 8599` | server started, health check HTTP 200 |
| Streamlit `AppTest` runs of `app.py` (inside pytest) | no exceptions |
| Playwright Chromium page loads at 1440x900 and 1280x720 | all section headings rendered, no Traceback text |

## Automated tests (`tests/test_edureach.py`)

Coverage of the requested items: dataset loading and required columns; duplicate villages; missing values and invalid coordinates; formula and score bounds; score-explanation reconstruction for every village and edge cases; threshold boundaries (39.99, 40, 69.99, 70) and NaN handling; ML reproducibility (refit with seed 42 equals the stored labels), three clusters, cluster-to-pattern mapping, and labels joined to the right villages using the separate `edureach_ml_clusters.csv`; scenario maths, baseline preservation (input frame and the CSV file hash unchanged), 0% = baseline, invalid slider values rejected; filters, subsets and the empty-filter case; map markers (count, latitude/longitude order, popup and tooltip name the correct village, colours, legend); app start-up, empty-filter message and simulator update; required files exist.

Tests recompute values from the data; they do not copy dashboard numbers.

**Sanity check that tests can fail:** changing the proximity weight from 0.40 to 0.30 made 6 tests fail; changing the Higher boundary to `<=` made the boundary test fail. Both changes were reverted and the suite passed again.

## Final run

`python -m pytest tests -q` -> **55 passed, 1 warning in 5.52s**

One warning appears: an Altair message ("can't infer vegalite type from 'empty'") from the empty-filter test, where a chart receives no rows. It is harmless.

## Manual and browser checks

| Check | Status |
|---|---|
| Top of page, KPI cards (equal height, definitions), sidebar readability, 1440 px | Done, screenshot viewed |
| ML Pattern chart labels readable | Done, screenshot viewed after fix |
| ML diagnostics panel | Done, screenshot viewed |
| Simulator controls and assumption box | Done, screenshot viewed |
| Village explanation panel (upper part) | Partly viewed |
| Baseline-vs-scenario chart and village-wise table (visual) | Seen in the author's screenshots; chart replaced afterwards (see below) and re-checked in the sandbox browser |
| 1280 px layout | Page loaded in the sandbox; **not inspected**. The author's screenshots were taken at a wider window |
| **Village map rendering** | Not visible in the sandbox (no internet). **Confirmed on the author's machine from screenshots:** map tiles, red and green markers and the legend (index < 40, index >= 70) render. A later screenshot from the author shows the popup for one village (Manwariya Diwan: index 35.92, Potential Gap, 0.34 km, no local school, school count 0, ML pattern) with a matching hover tooltip; other villages were not clicked by hand, but all popups are covered by unit tests. |
| Filter interactions in the browser | Author's screenshots with the filter "No Local School Record": Total Villages 36 (of 115), Potential Gap Candidates 36, average index 20.34, ML Patterns 1, status chart Higher 0 / Potential Gap 36, only red markers and a one-item legend. Other filter combinations were tested through AppTest only |

## Run on the author's machine (reported by the author)

Windows, Python 3.11, streamlit 1.65.0, pandas 3.0.6, numpy 2.4.6, scikit-learn 1.9.1, folium 0.20.0, streamlit-folium 0.27.4.

- `python -m pytest tests -q` -> **55 passed, 1 warning in 173.65s** (the same Altair warning as above). This run was made before the light/dark theme work below; the suite now has 58 tests and has been run only in the sandbox since then.
- Screenshots (13-10-2026) of the running app showed: header and KPI cards, sidebar, village map with legend, analytics charts, ML diagnostics panel, dataset table, "Why Is This Village Flagged?" breakdown (reconstructed 91.00 equals stored 91.00), simulator controls and metrics (67.25 -> 68.79, +1.54, 36 of 115 villages affected).
- Not shown in those screenshots: marker popup click, filter interactions, the village-wise table with its checkbox, the 1280 px layout.

## Issues found from those screenshots and the changes made

| Issue seen | Change |
|---|---|
| In the author's screenshots the "Baseline vs Hypothetical Scenario" and "Weighted contribution" bar charts looked clipped at the top (axis stopped at 40 while values were about 67 and 40), and the x-axis labels were rotated and cut ("Hypothetical Sce..."). The same chart rendered correctly in the sandbox browser, so the exact cause on the author's machine is not established. | The status, weighted-contribution and scenario charts now use explicit Altair charts with a fixed axis (0 to 100 for the index, 0 to 46 for points), horizontal labels and value labels. Re-checked in the sandbox browser; **not yet re-checked on the author's machine**. |
| Dataset table showed mixed decimals (86 vs 19.33) and "None" for missing Panchayat. | Two decimals for index and distance, "-" for missing Panchayat (display only; the data is unchanged). |
| Reconstructed index showed a green up-arrow for a +0.00 difference. | Arrow and colour removed for that metric. |

After these changes the suite was run again in the sandbox: 55 passed.

## Light and dark theme checks (sandbox browser)

| Check | Result |
|---|---|
| Browser/OS set to light, default Streamlit theme | Page and cards light; screenshot viewed |
| Browser/OS set to dark, default Streamlit theme | Page background (14, 17, 23), cards (22, 29, 43), text light; screenshots viewed (top, dataset table, simulator, charts) |
| Streamlit theme forced to dark in config while the browser is light | Page and cards dark, so the styles follow Streamlit's theme, not just the operating system (computed colours read from the page) |
| `st.context.theme.type` in that mismatch case | Reported "light" while the page was dark, so it is **not** used for styling. It is only a hint for which map base layer starts visible |
| Chart value labels in dark mode | Were black on dark; values are now part of the category labels and follow the theme text colour. Viewed in light and dark |
| Dark base map | Not seen (no internet in the sandbox). Only the generated map HTML is tested |
| Switching theme from Streamlit's ⋮ menu (System / Light / Dark) | Browser light then menu Dark: page and cards turned dark. Browser dark then menu Light: page and cards turned light (computed colours read). The "System" option and repeated switching in one session were not tested |

New tests: both map base layers exist and use no third-party key; the app source has no light-only inline colours; the Streamlit config does not force one theme. After the theme work the sandbox run gives **58 passed, 1 warning**.

## Second round on the author's machine (13-10-2026, screenshots)

The author ran the theme build on port 8510 (the first attempt on 8502 showed the old UI because the update had not been applied). Screenshots showed: dark theme (dark cards, readable sidebar title, blue chips, dark banner), light theme, the map with a Light map / Dark map switch, popup and tooltip, the filter checks above, the village-wise table with its checkbox, and the methodology note. The author's `pytest` result for the 58-test suite was not reported.

After those screenshots the KPI and dataset cards were changed to a responsive grid (equal height, wraps to 2 x 2 on narrow windows; measured card heights 152 px at both 1067 px and 1500 px window widths in the sandbox) and the map popup spacing was tightened. The popup spacing change was **not** seen in a browser (the sandbox cannot load the map). The suite still gives 58 passed in the sandbox.

## Known unresolved issues

- Map not visually verified (above).
- Data-preparation scripts were read but **not re-run end-to-end**; the app was verified from `edureach_dashboard.csv`.
- `Has_PS` substring issue affects one village (Dadaura) and the dataset was intentionally not changed.
- Source, year and extraction date of the raw files are not confirmed.
- No on-ground validation of any result.

## Limits of this validation

Passing tests show the code does what it is designed to do. They do not show that the index or the clusters reflect real-world accessibility.

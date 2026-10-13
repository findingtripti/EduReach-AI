# EduReach AI: Identifying Possible Government-School Accessibility Gaps with an Explainable Index, Unsupervised Clustering and GIS

**Author:** Tripti Singh, B.Tech Computer Science and Engineering
**Study area:** Jamunaha block, Shravasti district, Uttar Pradesh, India
**Status:** early-stage academic prototype; results are exploratory and not field-validated

## 1. Abstract

A school that is near a village on a map is not necessarily accessible, and some villages have no recorded local school at all. EduReach AI is a Python/Streamlit dashboard that combines a transparent, project-defined Accessibility Index (availability, proximity, school-level coverage), an unsupervised Gaussian Mixture Model, an interactive map, village-level score explanations and a hypothetical intervention simulator for 115 villages in Jamunaha block. In the current data 79 villages have a recorded local school and 36 do not; the mean index is 67.25 on a 0-100 scale. The index and clusters are descriptive. Distances are straight-line proxies and no on-ground validation has been done.

## 2. Problem statement

Planners need to know which villages deserve a closer look for school access. Counting schools per village hides villages with none, and straight distance alone says little about real access. The project asks: using the available school and village data, which villages show possible accessibility gaps, why are they flagged, and how might hypothetical changes alter the picture?

## 3. Motivation and SDG relevance

The work relates to **Sustainable Development Goal 4 (Quality Education)**: inclusive and equitable access to education. A transparent screening tool can help prioritise where to collect better evidence. It does not by itself show that any village is deprived.

## 4. Objectives and scope

1. Flag villages that may need further accessibility investigation.
2. Analyse school availability, a proximity proxy and school-level indicators.
3. Show results on an interactive map.
4. Use an explainable score and unsupervised clustering.
5. Explain each village's score.
6. Simulate hypothetical interventions with clearly stated assumptions.
7. Report limitations openly.

Scope: one block, 115 villages, government schools listed in the source report. Out of scope: road networks, travel time, school quality, capacity, enrolment, private schools, demographics.

## 5. Study area

Jamunaha block in Shravasti district, Uttar Pradesh. The village list extracted for the block has 115 villages, all with coordinates.

## 6. Dataset and sources

| Data | Project file | Use |
|---|---|---|
| School list (170 school rows for Jamunaha, 79 villages with at least one) | `Reports (1).xlsx` | availability, school types, counts |
| Water-supply (JJM-style) village report | `Reports.xlsx` | contextual indicators only |
| Village boundaries | `vb_soi_up.GeoJSON/KML` (not included in the submission ZIP because of size) | village points |

**To be confirmed by the author:** the publishing body, release year and download date of each file. The files do not state them, so this report does not name them. Candidate public portals include UDISE+ and the Jal Jeevan Mission dashboard (see References), but this is not asserted for these particular files. No synthetic data is used. Derived fields and assumptions are listed in `DATA_DICTIONARY.md`.

## 7. Preprocessing and feature engineering

Villages and schools are matched by lower-cased, trimmed name. School type strings are turned into 0/1 flags (primary, upper primary, composite, secondary). Each village point is the representative point of its polygon (converted from the projected CRS to WGS84). The nearest school is found by haversine distance. 63 villages did not match the JJM report and keep empty JJM fields. No values were invented. Known issue: the primary-school flag uses a substring test that also matches "UPS", which affects one village (Dadaura; index 96 instead of 91). The dataset was left unchanged.

## 8. Accessibility scoring

```
Index = 0.40 x Availability + 0.40 x Proximity + 0.20 x Coverage      (0-100)
```

Availability is 0 or 100. Proximity = 100 x (1 - distance / maximum distance in the dataset). Coverage = 25 x PS + 25 x UPS + 30 x Composite + 20 x Madhyamik, capped at 100. Status: below 40 Potential Gap, 40 to below 70 Moderate (internal), 70 and above Higher. The weights and thresholds are the author's design choices. Mean component scores: availability 68.70, proximity 84.61, coverage 29.65.

## 9. GIS implementation

Folium map with one circle marker per village, coloured by status, with tooltip and popup. Coordinates use [latitude, longitude]. Tests confirm that every marker's popup names the village at that location. Distances are straight-line and are labelled as such wherever they appear.

## 10. Machine-learning methodology

Gaussian Mixture Model (3 components, seed 42) on seven standardised features: nearest-school distance, has-school, four school-type flags and school count. It is unsupervised because there is no ground-truth label. The three patterns are: no local school with high travel burden (36 villages), local school with basic coverage (30) and local school with broader coverage (49). BIC and AIC kept falling up to k = 5 but are unreliable here (components reach the covariance floor because most features are binary); k = 3 was kept for interpretability, not because it is statistically optimal. Because `Has_School` is an input, the first group is exactly the no-school group. Four of five tested seeds give the identical grouping; one differs (ARI 0.56).

## 11. Dashboard architecture

`edureach_core.py` (logic, no UI) -> `edureach_map.py` (map) -> `app.py` (Streamlit layout). The model is not refitted in the app; labels come from the stored CSV, so cluster ids do not change when filters change. Diagnostics are computed live from the same features.

## 12. Explainability

For a selected village the app shows raw score, weight, weighted points and maximum points for each component and sums them to the stored index (maximum difference 0.005, tested for all villages). A note states that "Potential Gap" currently coincides with "no recorded local school" and what the index does not measure.

## 13. Intervention simulation

Two hypothetical scenarios with a user-set percentage: *connectivity improvement* (closes part of the proximity gap) and *hypothetical new local school* (closes part of the availability and proximity gaps; coverage constant). Baseline, scenario, change and Potential-Gap counts are shown, with a village-wise table. See `METHODOLOGY.md` section 6. Capacity, staffing, cost and feasibility are not modelled.

## 14. Results (generated by the code)

- 115 villages; 79 with a recorded local school; 36 without.
- 36 villages are Potential Gap; 79 are Higher; no village is Moderate.
- Mean Accessibility Index 67.25. The 36 no-school villages have a mean index of 20.34 and a mean straight-line distance of 1.62 km to the nearest school location (range 0.07 to 3.3 km).

Scenario arithmetic (villages without a recorded school are changed):

| Scenario | Assumption | Baseline mean | Scenario mean | Change | Potential Gap villages |
|---|---|---|---|---|---|
| Connectivity improvement | 25% | 67.25 | 68.79 | +1.54 | 36 -> 36 |
| Connectivity improvement | 50% | 67.25 | 70.33 | +3.08 | 36 -> 36 |
| Connectivity improvement | 100% | 67.25 | 73.41 | +6.16 | 36 -> 19 |
| Hypothetical new local school | 25% | 67.25 | 71.92 | +4.67 | 36 -> 24 |
| Hypothetical new local school | 50% | 67.25 | 76.59 | +9.34 | 36 -> 0 |
| Hypothetical new local school | 100% | 67.25 | 85.93 | +18.68 | 36 -> 0 |

These are consequences of assumptions, not predictions.

## 15. Testing and validation

An automated pytest suite checks loading, validation, duplicates, invalid coordinates, formula and score bounds, explanation reconstruction, threshold boundaries, ML reproducibility and label joins, scenario maths, filters, the empty-filter case, map markers and popups, and the app's start-up and simulator behaviour. The dashboard was also opened in a real browser. Details and limits are in `TESTING_REPORT.md`. There has been **no validation against field data**.

## 16. Limitations and ethical considerations

- Straight-line distance is not travel time; roads, rivers, terrain, seasons and safety are not measured.
- Schools are placed at village points, and villages with a school get distance 0 by construction.
- Name-based matching can miss villages or schools.
- The index is project-defined; changing the weights changes the results.
- Clusters are descriptive; the no-school cluster repeats an input feature.
- Scenarios are assumptions.
- Data completeness and freshness are not confirmed.
- Ethics: labels such as "Potential Gap" can stigmatise places if over-read. Outputs should prompt local verification, not decide funding. Only public, village-level data are used; no personal data.

## 17. Future scope

Road-network travel time (for example from OpenStreetMap), surveyed school coordinates, enrolment and distance-to-school evidence, sensitivity analysis of the weights, correction of the primary/upper-primary flag, comparison with field visits, and a feasibility layer for new-school scenarios.

## 18. Conclusion

EduReach AI shows how an open, explainable index, an honest unsupervised model and a clearly labelled simulator can support screening for school-access gaps. In its current form it identifies 36 villages with no recorded local school as candidates for closer review. It does not prove inaccessibility and needs field validation and better distance data before any real planning use.

## 19. References

- United Nations, Sustainable Development Goal 4: https://sdgs.un.org/goals/goal4
- scikit-learn, Gaussian mixture models: https://scikit-learn.org/stable/modules/mixture.html
- scikit-learn, Adjusted Rand Index: https://scikit-learn.org/stable/modules/clustering.html#adjusted-rand-index
- Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
- Streamlit documentation: https://docs.streamlit.io
- folium documentation: https://python-visualization.github.io/folium/
- Candidate data portals, to be confirmed against the files used: UDISE+ https://udiseplus.gov.in and Jal Jeevan Mission https://jaljeevanmission.gov.in

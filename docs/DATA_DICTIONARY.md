# Data Dictionary

File: `edureach_dashboard.csv` (one row per village). `Dashboard_Status` is added at load time by `edureach_core.py` and is not stored in the CSV.

Rows: 115. Columns in file: 35.

| Column | Meaning | Type in file | Unit / values | Source or derivation | Missing values | Role |
|---|---|---|---|---|---|---|
| `Village` | Village name | text | text | Village polygon attributes in the KML/GeoJSON (vb_soi_up); publisher to be confirmed | 0 missing | Input id / display |
| `Village_Code` | Village code from the boundary file | int64 | integer | Boundary file attribute | 0 missing | Identifier (unique) |
| `Latitude` | Village representative point, WGS84 | float64 | decimal degrees | Shapely representative_point() of the village polygon (create_coordinates.py); not a surveyed school location | 0 missing | Input / map |
| `Longitude` | Village representative point, WGS84 | float64 | decimal degrees | As Latitude | 0 missing | Input / map |
| `Panchayat` | Gram panchayat name | text | text | Joined from the JJM village report by exact lower-case name match; empty for unmatched villages | 63 missing (kept as empty, not filled) | Display |
| `Has_School` | 1 if the school list has at least one school whose VillageName matches this village | int64 | 0/1 | Reports (1).xlsx school list, name-matched (create_village_dataset.py) | 0 missing | Input feature (ML, score) |
| `School_Count` | Number of schools recorded for the village | int64 | integer | Count of matched school rows | 0 missing | Input feature (ML) |
| `School_Types` | School types recorded, joined with ' | ' | text | text | School Type column of the school list | 0 missing | Display |
| `School_Water_Yes` | Schools whose water-connection status is 'Yes' | int64 | integer | Water Connection Status column | 0 missing | Contextual |
| `Water_Connected_School_Count` | Schools with water connection | int64 | integer | add_school_indicators.py | 0 missing | Contextual |
| `Has_PS` | 1 if a Primary-type school is recorded | int64 | 0/1 | Substring test 'PS' on School Type (add_school_indicators.py). KNOWN ISSUE: also matches 'UPS' | 0 missing | Input feature (ML, coverage score) |
| `Has_UPS` | 1 if an Upper-Primary-type school is recorded | int64 | 0/1 | Substring test 'UPS' | 0 missing | Input feature |
| `Has_Composite` | 1 if a Composite school is recorded | int64 | 0/1 | Substring test 'Composite' | 0 missing | Input feature |
| `Has_Madhyamik` | 1 if a Madhyamik (secondary) school is recorded | int64 | 0/1 | Substring test 'Madhyamik' | 0 missing | Input feature |
| `Nearest_School_Distance_km` | Straight-line (haversine) distance to the nearest school location | float64 | km | calculate_nearest_school.py; school location = its village's representative point. 0 when the village itself has a school | 0 missing | Input feature / proximity |
| `Availability_Score` | 100 if Has_School = 1, else 0 | int64 | 0 or 100 | calculate_improved_accessibility.py | 0 missing | Derived (40% weight) |
| `Proximity_Score` | 100 x (1 - distance / maximum observed distance), clipped to 0-100 | float64 | 0-100 | Maximum observed distance in this dataset (about 3.3 km) | 0 missing | Derived (40% weight) |
| `School_Level_Coverage_Score` | 25 x PS + 25 x UPS + 30 x Composite + 20 x Madhyamik, capped at 100 | int64 | 0-100 | calculate_improved_accessibility.py | 0 missing | Derived (20% weight) |
| `Accessibility_Index` | 0.40 x Availability + 0.40 x Proximity + 0.20 x Coverage, rounded to 2 decimals | float64 | 0-100 | Project-defined exploratory indicator | 0 missing | Derived metric |
| `Accessibility_Status` | Potential Gap (<40), Moderate (40 to <70), Higher (>=70) | text | text | Stored by the pipeline; dashboard recomputes the same rule (Dashboard_Status) | 0 missing | Derived label |
| `Potential_Gap_Candidate` | 1 if Accessibility_Index < 40 | int64 | 0/1 | Pipeline flag | 0 missing | Derived flag |
| `ML_Cluster` | Gaussian Mixture cluster id (0, 1, 2) | int64 | integer | run_accessibility_clustering.py: StandardScaler + GaussianMixture(3, random_state=42) | 0 missing | Model output (unsupervised, no true label) |
| `ML_Pattern` | Human-readable name given to a cluster after inspecting its profile | text | text | Manual naming in run_accessibility_clustering.py | 0 missing | Display |
| `Travel_Indicator` | Distance band: none / moderate / high / very high travel burden | text | text | Rules in create_why_analysis.py (>= 0.75, 1.5, 2.5 km) | 0 missing | Display (rule-based) |
| `Gap_Indicators` | Rule-based text listing observed gap signals | text | text | create_why_analysis.py | 0 missing | Display (rule-based) |
| `Overall_Interpretation` | Short label derived from ML_Cluster | text | text | create_why_analysis.py | 0 missing | Display |
| `JJM_Households` | Households in the JJM village record | float64 | count | Reports.xlsx (JJM report), exact name match; missing for unmatched villages | 63 missing (kept as empty, not filled) | Contextual only (not in score) |
| `JJM_FHTC_Households` | Households with functional tap connection | float64 | count | Reports.xlsx | 63 missing (kept as empty, not filled) | Contextual only |
| `JJM_Water_Completion` | Water-supply completion share | float64 | fraction 0-1 | Reports.xlsx 'Complete %' | 63 missing (kept as empty, not filled) | Contextual only |
| `JJM_Certified` | JJM village certification flag | text | Yes/No | Reports.xlsx 'Is Certified' | 63 missing (kept as empty, not filled) | Contextual only |
| `JJM_FHTC_Coverage` | FHTC households / households | float64 | fraction | integrate_jjm_indicators.py | 63 missing (kept as empty, not filled) | Contextual only |
| `JJM_Context` | Text summary of the JJM fields | text | text | create_why_analysis.py | 0 missing | Display |
| `Combined_Accessibility_Index` | Index if every no-school village had a school at distance 0 (precomputed what-if) | float64 | 0-100 | simulate_combined_intervention.py; precomputed, not used by the interactive simulator | 0 missing | Scenario output (hypothetical) |
| `Combined_Improvement` | Combined_Accessibility_Index minus Accessibility_Index | float64 | points | simulate_combined_intervention.py | 0 missing | Scenario output (hypothetical) |
| `Intervention_Combined` | Label of the precomputed scenario | text | text | simulate_combined_intervention.py | 0 missing | Display |

Notes

- **Provenance still to be confirmed by the author:** the exact publisher, year and extraction date of the school list (`Reports (1).xlsx`), the JJM report (`Reports.xlsx`) and the village boundary files (`vb_soi_up.GeoJSON/KML`). The project files do not state them, so they are not asserted here.
- The 63 empty `Panchayat` and JJM values are villages that did not match the JJM report by exact name. They are left empty.
- `School` locations are not independent coordinates: a school is placed at its village's representative point.
- Known data-preparation issue: `Has_PS` uses a substring test, so a school typed `UPS` also sets `Has_PS`. One village (Dadaura, type `Composite | UPS`) is affected: its coverage score is 80 instead of 55 (index 96 instead of 91). The dataset was not changed; fix `add_school_indicators.py` and re-run the pipeline if you want the corrected value.

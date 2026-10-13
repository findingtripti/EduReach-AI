"""EduReach AI - core logic (data loading, validation, scoring, scenarios).

This module contains the pure, testable logic that the Streamlit app
(app.py) uses. Nothing here depends on Streamlit.

Important: the Accessibility Index is a PROJECT-DEFINED exploratory
indicator, not a validated official metric, and distances are
straight-line (haversine) proxies between village-level coordinates.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Constants (single source of truth for the scoring framework)
# ---------------------------------------------------------------------
DATA_FILE = "edureach_dashboard.csv"

W_AVAILABILITY = 0.40
W_PROXIMITY = 0.40
W_COVERAGE = 0.20

GAP_THRESHOLD = 40.0     # index < 40            -> "Potential Gap"
HIGHER_THRESHOLD = 70.0  # index >= 70           -> "Higher"
                         # 40 <= index < 70      -> "Moderate" (internal)

STATUS_GAP = "Potential Gap"
STATUS_MODERATE = "Moderate"
STATUS_HIGHER = "Higher"

REQUIRED_COLUMNS = [
    "Village", "Village_Code", "Latitude", "Longitude",
    "Has_School", "School_Count", "Nearest_School_Distance_km",
    "Availability_Score", "Proximity_Score", "School_Level_Coverage_Score",
    "Accessibility_Index", "Accessibility_Status", "Potential_Gap_Candidate",
    "ML_Cluster", "ML_Pattern",
]

NUMERIC_COLUMNS = [
    "Latitude", "Longitude", "Has_School", "School_Count",
    "Nearest_School_Distance_km", "Availability_Score", "Proximity_Score",
    "School_Level_Coverage_Score", "Accessibility_Index",
    "Potential_Gap_Candidate", "ML_Cluster",
]

GMM_FEATURES = [
    "Nearest_School_Distance_km", "Has_School", "Has_PS", "Has_UPS",
    "Has_Composite", "Has_Madhyamik", "School_Count",
]

SCOPE_NO_SCHOOL = "Villages without a recorded local school"
SCOPE_ALL = "All villages in the current selection"
INTERVENTION_CONNECTIVITY = "Connectivity improvement"
INTERVENTION_NEW_SCHOOL = "Hypothetical new local school"


def default_data_path() -> Path:
    """CSV path relative to this file, so the app runs from any folder."""
    return Path(__file__).resolve().parent / DATA_FILE


# ---------------------------------------------------------------------
# Loading and validation
# ---------------------------------------------------------------------
def load_dashboard_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the dashboard CSV, coerce numeric columns, add Dashboard_Status.

    Missing values are NOT silently replaced; use validate_dataset() to
    find them.
    """
    path = Path(path) if path else default_data_path()
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} was not found at {path}. Keep app.py and "
            f"{DATA_FILE} in the same folder."
        )
    df = pd.read_csv(path)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Accessibility_Index" in df.columns:
        df["Dashboard_Status"] = df["Accessibility_Index"].apply(classify_status)
    return df


def validate_dataset(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Return a list of (severity, message). severity is 'error' or 'warning'."""
    issues: list[tuple[str, str]] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        issues.append(("error", "Missing required columns: " + ", ".join(missing)))
        return issues  # nothing else can be checked reliably

    if df["Village_Code"].duplicated().any():
        issues.append(("error", "Duplicate Village_Code values found."))
    if df["Village"].duplicated().any():
        issues.append(("warning", "Duplicate village names found."))

    for col in ["Latitude", "Longitude", "Has_School", "School_Count", "Accessibility_Index",
                "Availability_Score", "Proximity_Score",
                "School_Level_Coverage_Score"]:
        if df[col].isna().any():
            issues.append(("error", f"{col} has {int(df[col].isna().sum())} missing/non-numeric value(s)."))

    lat_bad = ~df["Latitude"].between(-90, 90)
    lon_bad = ~df["Longitude"].between(-180, 180)
    if (lat_bad | lon_bad).any():
        issues.append(("error", f"{int((lat_bad | lon_bad).sum())} record(s) have invalid coordinates."))

    if not df["Has_School"].isin([0, 1]).all():
        issues.append(("error", "Has_School must be 0 or 1."))

    idx = df["Accessibility_Index"]
    if ((idx < 0) | (idx > 100)).any():
        issues.append(("error", "Accessibility_Index must lie between 0 and 100."))

    recon = score_from_components(
        df["Availability_Score"], df["Proximity_Score"],
        df["School_Level_Coverage_Score"],
    )
    if ((recon - idx).abs() > 0.5).any():
        issues.append(("warning", "Stored Accessibility_Index differs from the weighted component score by more than 0.5 for some villages."))

    if (df["Accessibility_Status"] != idx.apply(classify_status)).any():
        issues.append(("warning", "Stored Accessibility_Status disagrees with the current threshold rule for some villages."))

    if df.groupby("ML_Cluster")["ML_Pattern"].nunique().max() > 1:
        issues.append(("warning", "An ML_Cluster id maps to more than one ML_Pattern label."))
    return issues


# ---------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------
def score_from_components(availability, proximity, coverage):
    """Accessibility Index = 0.40*Availability + 0.40*Proximity + 0.20*Coverage."""
    return (
        W_AVAILABILITY * availability
        + W_PROXIMITY * proximity
        + W_COVERAGE * coverage
    )


def classify_status(score) -> str:
    """Classify an index value. Boundaries: <40 Gap, [40,70) Moderate, >=70 Higher."""
    if score is None or pd.isna(score):
        return "Unclassified"
    if score < GAP_THRESHOLD:
        return STATUS_GAP
    if score < HIGHER_THRESHOLD:
        return STATUS_MODERATE
    return STATUS_HIGHER


def explain_score(row) -> dict:
    """Break one village's stored index into weighted component contributions."""
    comps = [
        ("Availability", W_AVAILABILITY, float(row["Availability_Score"])),
        ("Proximity", W_PROXIMITY, float(row["Proximity_Score"])),
        ("School-level coverage", W_COVERAGE, float(row["School_Level_Coverage_Score"])),
    ]
    rows = [
        {"Component": f"{name} ({int(w * 100)}%)", "Raw Score": raw,
         "Weighted Points": w * raw, "Maximum Points": w * 100}
        for name, w, raw in comps
    ]
    reconstructed = sum(r["Weighted Points"] for r in rows)
    stored = float(row["Accessibility_Index"])
    return {"components": rows, "reconstructed": reconstructed,
            "stored": stored, "difference": reconstructed - stored}


# ---------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------
def apply_filters(df: pd.DataFrame, statuses, school_filter: str) -> pd.DataFrame:
    """Filter by Dashboard_Status and local-school record. Never mutates df."""
    out = df.copy()
    if statuses:
        out = out[out["Dashboard_Status"].isin(statuses)]
    if school_filter == "School Available":
        out = out[out["Has_School"] == 1]
    elif school_filter == "No Local School Record":
        out = out[out["Has_School"] == 0]
    return out


# ---------------------------------------------------------------------
# Intervention scenarios (hypothetical)
# ---------------------------------------------------------------------
def simulate_scenario(df: pd.DataFrame, intervention: str, gap_closed_pct: float,
                      scope: str = SCOPE_NO_SCHOOL) -> pd.DataFrame:
    """Apply an ASSUMED component change and return a new DataFrame.

    - Connectivity improvement: closes `gap_closed_pct`% of the remaining
      gap in the Proximity component only.
    - Hypothetical new local school: closes `gap_closed_pct`% of the
      remaining gap in Availability and Proximity. Coverage is held
      constant (school type/level of a new school is not modelled).
    - The input DataFrame is never modified, and the original dataset is
      never written to.
    """
    if gap_closed_pct is None or pd.isna(gap_closed_pct) or not (0 <= gap_closed_pct <= 100):
        raise ValueError("gap_closed_pct must be a number between 0 and 100.")
    if intervention not in (INTERVENTION_CONNECTIVITY, INTERVENTION_NEW_SCHOOL):
        raise ValueError(f"Unknown intervention: {intervention!r}")
    if scope not in (SCOPE_NO_SCHOOL, SCOPE_ALL):
        raise ValueError(f"Unknown scope: {scope!r}")

    sim = df.copy()
    f = gap_closed_pct / 100.0
    avail = sim["Availability_Score"].clip(0, 100)
    prox = sim["Proximity_Score"].clip(0, 100)
    cov = sim["School_Level_Coverage_Score"].clip(0, 100)

    if scope == SCOPE_NO_SCHOOL:
        affected = sim["Has_School"] == 0
    else:
        affected = pd.Series(True, index=sim.index)

    new_prox = prox.where(~affected, prox + f * (100 - prox))
    if intervention == INTERVENTION_NEW_SCHOOL:
        new_avail = avail.where(~affected, avail + f * (100 - avail))
    else:
        new_avail = avail

    sim["Baseline_Index"] = sim["Accessibility_Index"]
    sim["Scenario_Availability"] = new_avail
    sim["Scenario_Proximity"] = new_prox
    sim["Scenario_Coverage"] = cov
    sim["Scenario_Index"] = (
        sim["Accessibility_Index"]
        + W_AVAILABILITY * (new_avail - sim["Availability_Score"])
        + W_PROXIMITY * (new_prox - sim["Proximity_Score"])
        + W_COVERAGE * (cov - sim["School_Level_Coverage_Score"])
    ).clip(0, 100)
    sim["Scenario_Change"] = sim["Scenario_Index"] - sim["Baseline_Index"]
    sim["Scenario_Status"] = sim["Scenario_Index"].apply(classify_status)
    sim["Affected_By_Scenario"] = affected
    return sim


def scenario_summary(sim: pd.DataFrame) -> dict:
    """Headline numbers for a scenario DataFrame from simulate_scenario()."""
    return {
        "villages": int(len(sim)),
        "affected": int(sim["Affected_By_Scenario"].sum()),
        "baseline_avg": float(sim["Baseline_Index"].mean()),
        "scenario_avg": float(sim["Scenario_Index"].mean()),
        "avg_change": float(sim["Scenario_Change"].mean()),
        "gap_before": int((sim["Baseline_Index"] < GAP_THRESHOLD).sum()),
        "gap_after": int((sim["Scenario_Index"] < GAP_THRESHOLD).sum()),
    }


# ---------------------------------------------------------------------
# ML diagnostics (unsupervised GMM)
# ---------------------------------------------------------------------
def gmm_diagnostics(df: pd.DataFrame, seeds=(0, 7, 21, 42, 99), ks=(2, 3, 4, 5)) -> dict:
    """BIC/AIC per k, seed stability (ARI) and a covariance-degeneracy flag.

    Uses the same features, scaling and random_state=42 as the published
    clustering. These are unsupervised diagnostics, NOT accuracy scores.
    """
    from sklearn.metrics import adjusted_rand_score
    from sklearn.mixture import GaussianMixture
    from sklearn.preprocessing import StandardScaler

    X = StandardScaler().fit_transform(df[GMM_FEATURES])
    rows = []
    for k in ks:
        m = GaussianMixture(n_components=k, random_state=42).fit(X)
        floor = min(float(np.diag(c).min()) for c in m.covariances_)
        rows.append({"k": k, "BIC": m.bic(X), "AIC": m.aic(X),
                     "Converged": bool(m.converged_),
                     "At_covariance_floor": bool(floor <= 1.5 * m.reg_covar)})
    labels = {s: GaussianMixture(n_components=3, random_state=s).fit_predict(X) for s in seeds}
    published = GaussianMixture(n_components=3, random_state=42).fit_predict(X)
    ari = {s: float(adjusted_rand_score(labels[s], published)) for s in seeds}
    return {
        "model_selection": pd.DataFrame(rows),
        "seed_ari_vs_published": ari,
        "published_matches_stored": bool(
            adjusted_rand_score(published, df["ML_Cluster"]) == 1.0
        ) if "ML_Cluster" in df.columns else None,
    }

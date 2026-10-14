"""Behavioural tests for EduReach AI.

They check real behaviour (formulas, boundaries, reproducibility,
scenario maths, filters) against the actual dataset. Dashboard numbers are
recomputed, not copied.
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import edureach_core as core

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def df():
    return core.load_dashboard_data()


# ---------------------------------------------------------------- data
def test_dataset_loads_with_required_columns(df):
    assert not df.empty
    assert set(core.REQUIRED_COLUMNS).issubset(df.columns)
    assert df["Village_Code"].is_unique


def test_clean_dataset_has_no_validation_issues(df):
    assert core.validate_dataset(df) == []


def test_missing_file_gives_friendly_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="edureach_dashboard.csv"):
        core.load_dashboard_data(tmp_path / "edureach_dashboard.csv")


def test_missing_required_column_is_reported(df):
    issues = core.validate_dataset(df.drop(columns=["Accessibility_Index"]))
    assert issues and issues[0][0] == "error"
    assert "Accessibility_Index" in issues[0][1]


def test_duplicate_village_records_are_flagged(df):
    dup = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    assert any("Duplicate Village_Code" in m for _, m in core.validate_dataset(dup))


@pytest.mark.parametrize("column,bad", [("Latitude", 95.0), ("Longitude", -200.0)])
def test_invalid_coordinates_are_flagged(df, column, bad):
    broken = df.copy()
    broken.loc[0, column] = bad
    assert any("invalid coordinates" in m for _, m in core.validate_dataset(broken))


def test_missing_values_are_not_silently_filled(df):
    broken = df.copy()
    broken.loc[0, "Accessibility_Index"] = np.nan
    assert any("Accessibility_Index" in m for _, m in core.validate_dataset(broken))


# ------------------------------------------------------------- scoring
def test_formula_corner_cases():
    assert core.score_from_components(100, 100, 100) == pytest.approx(100)
    assert core.score_from_components(0, 0, 0) == 0
    assert core.score_from_components(100, 0, 0) == pytest.approx(40)
    assert core.score_from_components(0, 100, 0) == pytest.approx(40)
    assert core.score_from_components(0, 0, 100) == pytest.approx(20)
    assert core.W_AVAILABILITY + core.W_PROXIMITY + core.W_COVERAGE == pytest.approx(1.0)


def test_stored_index_matches_weighted_components_and_is_bounded(df):
    recon = core.score_from_components(
        df["Availability_Score"], df["Proximity_Score"], df["School_Level_Coverage_Score"]
    )
    assert (recon - df["Accessibility_Index"]).abs().max() <= 0.51  # stored index is rounded
    assert df["Accessibility_Index"].between(0, 100).all()


def test_explanation_reconstructs_score_for_every_village(df):
    for _, row in df.iterrows():
        e = core.explain_score(row)
        assert abs(e["difference"]) <= 0.51
        assert sum(c["Weighted Points"] for c in e["components"]) == pytest.approx(e["reconstructed"])
        assert sum(c["Maximum Points"] for c in e["components"]) == pytest.approx(100)


def test_explanation_edge_cases(df):
    low = df.loc[df["Accessibility_Index"].idxmin()]
    high = df.loc[df["Accessibility_Index"].idxmax()]
    no_school = df[df["Has_School"] == 0].iloc[0]
    for row in (low, high, no_school):
        assert abs(core.explain_score(row)["difference"]) <= 0.51


@pytest.mark.parametrize("score,expected", [
    (0, "Potential Gap"), (39.99, "Potential Gap"), (40, "Moderate"),
    (69.99, "Moderate"), (70, "Higher"), (100, "Higher"),
])
def test_status_threshold_boundaries(score, expected):
    assert core.classify_status(score) == expected


def test_nan_score_is_unclassified_not_a_gap():
    assert core.classify_status(float("nan")) == "Unclassified"


def test_every_village_is_classified_consistently(df):
    assert df["Dashboard_Status"].isin(["Potential Gap", "Moderate", "Higher"]).all()
    assert (df["Dashboard_Status"] == df["Accessibility_Status"]).all()
    assert ((df["Accessibility_Index"] < core.GAP_THRESHOLD).astype(int) == df["Potential_Gap_Candidate"]).all()


# ------------------------------------------------------------------ ML
def test_gmm_labels_are_reproducible_from_features(df):
    from sklearn.mixture import GaussianMixture
    from sklearn.preprocessing import StandardScaler

    X = StandardScaler().fit_transform(df[core.GMM_FEATURES])
    labels = GaussianMixture(n_components=3, random_state=42).fit_predict(X)
    assert (labels == df["ML_Cluster"].to_numpy()).all()


def test_cluster_count_and_label_mapping(df):
    assert df["ML_Cluster"].nunique() == 3
    assert df.groupby("ML_Cluster")["ML_Pattern"].nunique().max() == 1
    assert df.groupby("ML_Pattern")["ML_Cluster"].nunique().max() == 1


def test_cluster_labels_join_to_the_correct_villages(df):
    source = ROOT / "edureach_ml_clusters.csv"
    if not source.exists():
        pytest.skip("edureach_ml_clusters.csv not present")
    src = pd.read_csv(source)[["Village_Code", "ML_Cluster", "ML_Pattern"]]
    merged = df[["Village_Code", "ML_Cluster", "ML_Pattern"]].merge(src, on="Village_Code", suffixes=("", "_src"))
    assert len(merged) == len(df)
    assert (merged["ML_Cluster"] == merged["ML_Cluster_src"]).all()
    assert (merged["ML_Pattern"] == merged["ML_Pattern_src"]).all()


def test_diagnostics_structure(df):
    d = core.gmm_diagnostics(df, seeds=(42, 7), ks=(2, 3))
    assert list(d["model_selection"]["k"]) == [2, 3]
    assert d["seed_ari_vs_published"][42] == pytest.approx(1.0)
    assert d["published_matches_stored"] is True


# ------------------------------------------------------------ scenarios
def test_scenario_never_mutates_input_or_source_file(df):
    path = core.default_data_path()
    before_file = hashlib.sha256(path.read_bytes()).hexdigest()
    before_df = df.copy(deep=True)
    for kind in (core.INTERVENTION_CONNECTIVITY, core.INTERVENTION_NEW_SCHOOL):
        core.simulate_scenario(df, kind, 60)
    pd.testing.assert_frame_equal(df, before_df)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before_file


@pytest.mark.parametrize("kind", [core.INTERVENTION_CONNECTIVITY, core.INTERVENTION_NEW_SCHOOL])
def test_zero_percent_reproduces_baseline(df, kind):
    sim = core.simulate_scenario(df, kind, 0)
    assert (sim["Scenario_Change"].abs() < 1e-9).all()
    assert core.scenario_summary(sim)["avg_change"] == pytest.approx(0)


def test_connectivity_changes_only_proximity(df):
    sim = core.simulate_scenario(df, core.INTERVENTION_CONNECTIVITY, 50)
    assert (sim["Scenario_Availability"] == sim["Availability_Score"].clip(0, 100)).all()
    assert (sim["Scenario_Coverage"] == sim["School_Level_Coverage_Score"].clip(0, 100)).all()
    assert (sim["Scenario_Proximity"] >= sim["Proximity_Score"]).all()
    expected = 0.4 * (sim["Scenario_Proximity"] - sim["Proximity_Score"])
    assert (sim["Scenario_Change"] - expected).abs().max() < 1e-9


def test_new_school_updates_availability_and_proximity_not_coverage(df):
    sim = core.simulate_scenario(df, core.INTERVENTION_NEW_SCHOOL, 50)
    affected = sim["Affected_By_Scenario"]
    assert (sim.loc[~affected, "Scenario_Change"] == 0).all()
    assert (sim.loc[affected, "Scenario_Availability"] > sim.loc[affected, "Availability_Score"]).all()
    assert (sim["Scenario_Coverage"] == sim["School_Level_Coverage_Score"].clip(0, 100)).all()


def test_scope_default_touches_only_villages_without_a_school(df):
    sim = core.simulate_scenario(df, core.INTERVENTION_NEW_SCHOOL, 100)
    assert (sim["Affected_By_Scenario"] == (sim["Has_School"] == 0)).all()
    assert (sim.loc[sim["Has_School"] == 1, "Scenario_Index"] == sim.loc[sim["Has_School"] == 1, "Baseline_Index"]).all()


def test_scenario_scores_are_bounded_and_monotonic(df):
    previous = None
    for pct in (0, 25, 50, 75, 100):
        sim = core.simulate_scenario(df, core.INTERVENTION_NEW_SCHOOL, pct, core.SCOPE_ALL)
        assert sim["Scenario_Index"].between(0, 100).all()
        avg = sim["Scenario_Index"].mean()
        if previous is not None:
            assert avg >= previous
        previous = avg


@pytest.mark.parametrize("bad", [-1, 101, float("nan"), None])
def test_invalid_slider_values_are_rejected(df, bad):
    with pytest.raises(ValueError):
        core.simulate_scenario(df, core.INTERVENTION_CONNECTIVITY, bad)


def test_unknown_intervention_is_rejected(df):
    with pytest.raises(ValueError):
        core.simulate_scenario(df, "Build a bridge", 10)


# -------------------------------------------------------------- filters
def test_status_and_school_filters_return_valid_subsets(df):
    gap = core.apply_filters(df, ["Potential Gap"], "All Villages")
    assert set(gap["Dashboard_Status"]) == {"Potential Gap"}
    assert len(gap) == int((df["Dashboard_Status"] == "Potential Gap").sum())
    has = core.apply_filters(df, [], "School Available")
    assert (has["Has_School"] == 1).all()
    none = core.apply_filters(df, [], "No Local School Record")
    assert (none["Has_School"] == 0).all()
    assert len(has) + len(none) == len(df)


def test_no_selection_means_no_status_filter_and_input_unchanged(df):
    before = df.copy(deep=True)
    assert len(core.apply_filters(df, [], "All Villages")) == len(df)
    pd.testing.assert_frame_equal(df, before)


def test_contradictory_filters_give_empty_result_without_error(df):
    empty = core.apply_filters(df, ["Higher"], "No Local School Record")
    assert empty.empty


# ------------------------------------------------- app smoke (UI logic)
def _run_app():
    from streamlit.testing.v1 import AppTest
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=180).run()


def test_app_starts_without_exceptions(df):
    at = _run_app()
    assert not at.exception
    labels = {m.label: m.value for m in at.metric}
    assert labels["Baseline Avg. Index"] == f"{df['Accessibility_Index'].mean():.2f}"


def test_app_empty_filter_shows_message_not_crash():
    at = _run_app()
    at.multiselect[0].set_value(["Higher"]).run()
    next(s for s in at.selectbox if s.label == "Local School Record").select("No Local School Record").run()
    assert not at.exception
    assert any("No villages match" in w.value for w in list(at.warning) + list(at.info))


def test_app_simulator_updates_with_slider(df):
    at = _run_app()
    at.slider(key="edureach_gap_closed_pct").set_value(60).run()
    assert not at.exception
    scen = next(m for m in at.metric if m.label == "Hypothetical Scenario Avg.")
    expected = core.scenario_summary(core.simulate_scenario(df, core.INTERVENTION_CONNECTIVITY, 60))["scenario_avg"]
    assert scen.value == f"{expected:.2f}"


# -------------------------------------------- required output files/docs
@pytest.mark.parametrize("name", [
    "README.md", "requirements.txt", "docs/PROJECT_REPORT.md", "docs/METHODOLOGY.md",
    "docs/DATA_DICTIONARY.md", "docs/TESTING_REPORT.md",
    "docs/VIVA_QUESTIONS_AND_ANSWERS.md", "docs/LEAN_CANVAS.md",
    
])
def test_required_files_exist_and_are_not_empty(name):
    path = ROOT / name
    assert path.exists() and path.stat().st_size > 200, f"{name} missing or too small"


# ------------------------------------------------------------------ GIS
def _markers(m):
    import folium
    return [x for x in m._children.values() if isinstance(x, folium.CircleMarker)]


def _tooltip_and_popup(marker):
    import folium
    kids = list(marker._children.values())
    tip = next(k for k in kids if isinstance(k, folium.Tooltip)).text
    pop = next(k for k in kids if isinstance(k, folium.Popup))
    return tip, str(list(pop.html._children.values())[0].data)


def test_map_has_one_marker_per_village_with_lat_lon_order(df):
    from edureach_map import build_village_map
    markers = _markers(build_village_map(df))
    assert len(markers) == len(df)
    pairs = {(round(m.location[0], 6), round(m.location[1], 6)) for m in markers}
    expected = {(round(r.Latitude, 6), round(r.Longitude, 6)) for r in df.itertuples()}
    assert pairs == expected
    assert all(-90 <= m.location[0] <= 90 and -180 <= m.location[1] <= 180 for m in markers)
    # study area is in northern India: latitude ~27-28, longitude ~81-82 (not swapped)
    assert all(m.location[0] < m.location[1] for m in markers)


def test_map_tooltip_and_popup_refer_to_the_correct_village(df):
    from edureach_map import build_village_map
    lookup = {(round(r.Latitude, 6), round(r.Longitude, 6)): r for r in df.itertuples()}
    for marker in _markers(build_village_map(df)):
        row = lookup[(round(marker.location[0], 6), round(marker.location[1], 6))]
        tip, popup = _tooltip_and_popup(marker)
        assert row.Village in tip and row.Village in popup
        assert f"{row.Accessibility_Index:.2f}" in popup
        assert row.Dashboard_Status in popup
        assert "straight-line" in popup


def test_map_colours_follow_status(df):
    from edureach_map import STATUS_COLORS, build_village_map
    lookup = {(round(r.Latitude, 6), round(r.Longitude, 6)): r.Dashboard_Status for r in df.itertuples()}
    for marker in _markers(build_village_map(df)):
        status = lookup[(round(marker.location[0], 6), round(marker.location[1], 6))]
        assert marker.options["color"] == STATUS_COLORS[status]


def test_map_legend_lists_only_present_statuses(df):
    from edureach_map import build_village_map
    html = build_village_map(df[df["Dashboard_Status"] == "Potential Gap"]).get_root().render()
    assert "Potential Gap (index" in html and "Higher (index" not in html


def test_map_rejects_empty_selection(df):
    from edureach_map import build_village_map
    with pytest.raises(ValueError):
        build_village_map(df.iloc[0:0])


# ---------------------------------------------------------------- theme
def test_map_offers_light_and_dark_base_maps_without_third_party_keys(df):
    from edureach_map import build_village_map
    for dark in (False, True):
        html = build_village_map(df.head(5), dark=dark).get_root().render()
        assert "er-dark-tiles" in html and "L.control.layers" in html
        assert html.count("L.tileLayer(") == 2
        assert "carto" not in html.lower()


def test_app_has_no_light_only_inline_colours():
    """All colours must live in the theme-aware stylesheet, not inline."""
    import re
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "light-dark(" in src
    outside_style = re.sub(r"<style>.*?</style>", "", src, flags=re.S)
    assert not re.search(r"(?:color|background)\s*:\s*#", outside_style)


def test_streamlit_config_does_not_force_one_theme():
    import tomllib
    cfg = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert "base" not in cfg.get("theme", {})
    assert "light" in cfg["theme"] and "dark" in cfg["theme"]


# --------------------------------------------------------------- charts
def test_chart_axis_is_fixed_starts_at_zero_and_shows_values():
    from edureach_charts import labelled_bar_chart
    for horizontal in (False, True):
        spec = labelled_bar_chart(["A", "B"], [30, 49], "Group", "Villages", y_max=60,
                                  value_format=".0f", horizontal=horizontal).to_dict()
        enc = spec["layer"][0]["encoding"] if "layer" in spec else spec["encoding"]
        value_axis = enc["x"] if horizontal else enc["y"]
        assert value_axis["scale"]["domain"] == [0, 60]
        labels = [row["label"] for row in next(iter(spec["datasets"].values()))]
        assert labels == ["A: 30", "B: 49"]


def test_chart_uses_a_single_theme_safe_bar_colour():
    from edureach_charts import BAR_COLOR, labelled_bar_chart
    spec = labelled_bar_chart(["A"], [5], "G", "V", y_max=10).to_dict()
    mark = spec["mark"] if "mark" in spec else spec["layer"][0]["mark"]
    assert mark["color"] == BAR_COLOR


def test_app_header_is_not_transparent():
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "stHeader" in src and "backdrop-filter" in src
    assert "background: transparent" not in src.split("stHeader")[1].split("}")[0]

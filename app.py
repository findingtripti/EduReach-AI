import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from edureach_charts import labelled_bar_chart
from edureach_map import build_village_map
from edureach_core import (
    GAP_THRESHOLD, INTERVENTION_CONNECTIVITY, INTERVENTION_NEW_SCHOOL,
    SCOPE_ALL, SCOPE_NO_SCHOOL, apply_filters, gmm_diagnostics,
    load_dashboard_data, simulate_scenario, scenario_summary,
    validate_dataset,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EduReach AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    /* Theme-aware palette: light-dark() follows the active Streamlit theme
       (light, dark or "use system setting"), not just the operating system. */
    .stApp {
        --er-card-bg: light-dark(#ffffff, #161d2b);
        --er-soft-bg: light-dark(#f8fafc, #121926);
        --er-card-border: light-dark(#e2e8f0, #2a3547);
        --er-text: light-dark(#0f172a, #f1f5f9);
        --er-muted: light-dark(#475569, #94a3b8);
        --er-alert: light-dark(#dc2626, #f87171);
        --er-shadow: light-dark(0 5px 18px rgba(15,23,42,0.07), 0 5px 18px rgba(0,0,0,0.45));
    }

    .block-container { padding-top: 1.8rem; padding-bottom: 3rem; }
    header[data-testid="stHeader"] {
        background: light-dark(rgba(255,255,255,0.94), rgba(14,17,23,0.94));
        backdrop-filter: blur(6px);
    }
    h1, h2, h3 { font-weight: 700 !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid var(--er-card-border); }
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    hr { margin-top: 1.5rem; margin-bottom: 1.5rem; }

    /* Hero banner */
    .er-hero {
        padding: 34px 40px; border-radius: 22px; margin-bottom: 24px;
        background: linear-gradient(135deg, light-dark(#0f172a, #1e3a5f) 0%, light-dark(#1e3a5f, #2b5282) 100%);
        border: 1px solid light-dark(transparent, #3b4a63);
        box-shadow: var(--er-shadow);
    }
    .er-hero-title { font-size: 42px; font-weight: 750; color: #ffffff; margin-bottom: 8px; line-height: 1.1; }
    .er-hero-sub { font-size: 22px; font-weight: 600; color: #dbeafe; margin-bottom: 12px; }
    .er-hero-desc { font-size: 15px; color: #cbd5e1; line-height: 1.6; }

    /* Cards */
    .er-card {
        background: var(--er-card-bg); padding: 22px; border-radius: 16px; min-height: 140px;
        border: 1px solid var(--er-card-border); box-shadow: var(--er-shadow);
    }
    .er-card.compact { padding: 16px; border-radius: 12px; min-height: 0; box-shadow: none; background: var(--er-soft-bg); }
    .er-label { font-size: 14px; color: var(--er-muted); font-weight: 600; margin-bottom: 9px; }
    .er-card.compact .er-label { font-weight: 500; margin-bottom: 6px; }
    .er-value { font-size: 32px; font-weight: 750; color: var(--er-text); }
    .er-card.compact .er-value { font-size: 28px; }
    .er-value.alert { color: var(--er-alert); }
    .er-sub { font-size: 12px; color: var(--er-muted); margin-top: 4px; }

    .er-grid { display: grid; gap: 16px; align-items: stretch; }
    .er-grid-4 { grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }
    .er-grid-3 { grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }
    .er-grid .er-card { height: 100%; box-sizing: border-box; }

    /* Sidebar */
    .er-side-title { font-size: 24px; font-weight: 750; color: var(--er-text); margin-bottom: 4px; }
    .er-side-sub { font-size: 13px; color: var(--er-muted); margin-bottom: 22px; }
    .er-side-block { font-size: 13px; line-height: 1.7; padding-top: 4px; }
    .er-side-label { color: var(--er-muted); font-weight: 600; margin-bottom: 2px; }
    .er-side-text { color: var(--er-text); line-height: 1.5; margin-bottom: 18px; }
    .er-side-big { color: var(--er-text); font-size: 18px; font-weight: 700; margin-bottom: 18px; }

    /* Methodology note */
    .er-note {
        padding: 18px 20px; border-radius: 14px; font-size: 13px; line-height: 1.7;
        background: var(--er-soft-bg); border: 1px solid var(--er-card-border); color: var(--er-muted);
    }
    .er-note b { color: var(--er-text); }
    </style>
    """,
    unsafe_allow_html=True
)


def _prefers_dark_theme():
    """Best-effort choice of the initial map style (the map also has a layer switch)."""
    try:
        base = st.get_option("theme.base")
        if base in ("light", "dark"):
            return base == "dark"
    except Exception:
        pass
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


# =========================================================
# LOAD DATA
# =========================================================

try:
    df = load_dashboard_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

# Data validation: show problems instead of silently filling values.
_data_issues = validate_dataset(df)
for _severity, _message in _data_issues:
    (st.error if _severity == "error" else st.warning)(
        f"Data check: {_message}"
    )
if any(_severity == "error" for _severity, _ in _data_issues):
    st.stop()

df["School_Count"] = df["School_Count"].astype(int)
df["Has_School"] = df["Has_School"].astype(int)
df["Potential_Gap_Candidate"] = df["Potential_Gap_Candidate"].astype(int)

# Dashboard_Status is created in edureach_core.classify_status():
# index < 40 Potential Gap, 40-<70 Moderate (internal), >= 70 Higher.

# =========================================================
# HERO HEADER
# =========================================================

st.html(
    """
    <div class="er-hero">
        <div class="er-hero-title">EduReach AI</div>
        <div class="er-hero-sub">From School Availability to Actual Accessibility</div>
        <div class="er-hero-desc">
            AI/ML &amp; GIS-based decision-support system for
            government-school accessibility analysis
        </div>
    </div>
    """
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="er-side-title">EduReach AI</div>'
        '<div class="er-side-sub">Accessibility Intelligence Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown("### Filters")

    status_options = [
        s for s in ["Higher", "Moderate", "Potential Gap"]
        if s in set(df["Dashboard_Status"])
    ]
    accessibility_filter = st.multiselect(
        "Accessibility Status",
        options=status_options,
        default=status_options,
        help="Project-defined categories from the Accessibility Index."
    )
    st.markdown("")

    school_filter = st.selectbox(
        "Local School Record",
        [
            "All Villages",
            "School Available",
            "No Local School Record"
        ]
    )

    st.markdown("---")

    st.html(
        f"""
        <div class="er-side-block">
            <div class="er-side-label">Study Area</div>
            <div class="er-side-text">Shravasti - Jamunaha</div>
            <div class="er-side-label">Village Records</div>
            <div class="er-side-big">{len(df)}</div>
            <div class="er-side-label">ML Method</div>
            <div class="er-side-text">Unsupervised Gaussian<br>Mixture Model</div>
        </div>
        """
    )
    st.caption("Theme: follows your device by default. Switch System / Light / Dark from the \u22ee menu (top right).")
    

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = apply_filters(df, accessibility_filter, school_filter)

# =========================================================
# KPI CALCULATIONS
# =========================================================

# KPIs describe the villages in the current selection
# (with the default filters this is the complete study area).
total_villages = len(filtered_df)
potential_gaps = int((filtered_df["Dashboard_Status"] == "Potential Gap").sum())
average_accessibility = (
    filtered_df["Accessibility_Index"].mean()
    if len(filtered_df) > 0
    else 0.0
)
ml_patterns = (
    filtered_df["ML_Pattern"].nunique()
    if len(filtered_df) > 0
    else 0
)

# =========================================================
# KPI CARDS
# =========================================================

def _kpi_card(label, value, sub, alert=False):
    value_class = "er-value alert" if alert else "er-value"
    return (
        f'<div class="er-card"><div class="er-label">{label}</div>'
        f'<div class="{value_class}">{value}</div>'
        f'<div class="er-sub">{sub}</div></div>'
    )


st.html(
    '<div class="er-grid er-grid-4">'
    + _kpi_card("Total Villages", f"{total_villages}", f"of {len(df)} in study area")
    + _kpi_card("Potential Gap Candidates", f"{potential_gaps}",
                "Index below 40 (project threshold)", alert=True)
    + _kpi_card("Avg. Accessibility", f"{average_accessibility:.2f}", "Mean index, 0-100 scale")
    + _kpi_card("ML Patterns", f"{ml_patterns}", "Unsupervised GMM groups")
    + "</div>"
)

st.markdown("<br>", unsafe_allow_html=True)

st.divider()


# =========================================================
# GIS MAP SECTION
# =========================================================

st.subheader("Village Accessibility Map")

st.caption(
    "Interactive spatial view of village-level accessibility "
    "patterns in the EduReach study area."
)


if len(filtered_df) > 0:

    m = build_village_map(filtered_df, dark=_prefers_dark_theme())


    # -----------------------------------------------------
    # DISPLAY MAP
    # -----------------------------------------------------

    st_folium(
        m,
        width=None,
        height=560,
        returned_objects=[]
    )
    st.caption(
        "Distances behind these markers are straight-line (haversine) "
        "estimates between village-level coordinates, not road distance "
        "or travel time. Click a marker for village details."
    )

else:

    st.warning(
        "No villages match the selected filters."
    )


# =========================================================
# ANALYTICS SECTION
# =========================================================

st.divider()

st.subheader("Accessibility Analytics")


chart_col1, chart_col2 = st.columns(2)


# =========================================================
# ACCESSIBILITY STATUS
# =========================================================


with chart_col1:
    st.markdown("#### Accessibility Status")

    status_order = [
        s for s in ["Higher", "Moderate", "Potential Gap"]
        if s in set(df["Dashboard_Status"])
    ]

    status_counts = (
        filtered_df["Dashboard_Status"]
        .value_counts()
        .reindex(status_order, fill_value=0)
    )

    st.altair_chart(
        labelled_bar_chart(
            status_counts.index, status_counts.values,
            "Accessibility status", "Number of villages",
            y_max=max(float(status_counts.max()) * 1.2, 5), value_format=".0f",
        ),
        width="stretch",
    )


# =========================================================
# ML PATTERNS
# =========================================================
with chart_col2:

    st.markdown("#### ML Pattern Distribution")

    pattern_label_map = {
        "High Travel-Burden / No Local School": "No Local School — High Travel Burden",
        "Local School - Basic Coverage": "Local School — Basic Coverage",
        "Local School - Broader Coverage": "Local School — Broader Coverage",
    }

    pattern_counts = filtered_df["ML_Pattern"].map(
        lambda value: pattern_label_map.get(value, value)
    ).value_counts()

    _short_labels = {
        "No Local School — High Travel Burden": "No local school",
        "Local School — Basic Coverage": "Basic coverage",
        "Local School — Broader Coverage": "Broader coverage",
    }
    _pc = pattern_counts.rename(index=_short_labels)
    st.altair_chart(
        labelled_bar_chart(
            _pc.index, _pc.values, "ML pattern", "Number of villages",
            y_max=max(float(_pc.max()) * 1.2, 5), value_format=".0f", horizontal=True,
        ),
        width="stretch",
    )

    st.caption(
        "Patterns identified by unsupervised Gaussian Mixture Model (GMM). "
        "These are descriptive groups, not predictions of school absence."
    )

    st.dataframe(
        pattern_counts.rename_axis("ML Pattern").reset_index(name="Village Count"),
        width="stretch",
        hide_index=True
    )

# =========================================================
# ML DIAGNOSTICS (UNSUPERVISED)
# =========================================================

@st.cache_data(show_spinner=False)
def _cached_gmm_diagnostics(data):
    return gmm_diagnostics(data)


with st.expander("ML model diagnostics - how to read the patterns", expanded=False):
    _diag = _cached_gmm_diagnostics(df)
    _ms = _diag["model_selection"].copy()
    _ms["BIC"] = _ms["BIC"].round(1)
    _ms["AIC"] = _ms["AIC"].round(1)
    _ms = _ms.rename(columns={"k": "Clusters (k)", "At_covariance_floor": "Component at covariance floor"})
    st.dataframe(_ms, width="stretch", hide_index=True)
    _ari = _diag["seed_ari_vs_published"]
    _same = sum(1 for v in _ari.values() if v == 1.0)
    st.write(
        f"**Reproducibility:** the stored cluster labels "
        f"{'are' if _diag['published_matches_stored'] else 'are NOT'} "
        f"reproduced exactly by refitting the same features with random_state=42."
    )
    st.write(
        f"**Seed stability:** {_same} of {len(_ari)} tested random seeds gave exactly the "
        f"published grouping; the lowest agreement (Adjusted Rand Index) was {min(_ari.values()):.2f}."
    )
    if _ms["Component at covariance floor"].any():
        st.warning(
            "Most model inputs are 0/1 flags, so some Gaussian components shrink to the "
            "covariance floor. BIC/AIC then keep falling as k grows and cannot, on their "
            "own, show that any particular k is best. k=3 is kept because it is easy to interpret."
        )
    _no_school_cluster = df.loc[df["Has_School"] == 0, "ML_Cluster"].unique()
    if len(_no_school_cluster) == 1 and (
        (df["ML_Cluster"] == _no_school_cluster[0]) == (df["Has_School"] == 0)
    ).all():
        st.info(
            "Has_School is one of the model inputs, so the no-local-school pattern mirrors that "
            "flag by construction. The unsupervised model mainly adds the split between "
            "'basic' and 'broader' school coverage among villages that have a recorded school."
        )
    st.caption(
        "These are unsupervised diagnostics. There is no ground-truth label, so accuracy, "
        "precision or recall do not apply, and the patterns are not validated predictions "
        "of real-world educational deprivation."
    )

# =========================================================
# DATASET SECTION
# =========================================================

st.divider()

st.subheader("EduReach Dataset")

st.caption(
    "Village-level accessibility, school, GIS, ML "
    "and contextual indicators."
)


# =========================================================
# DATASET SUMMARY
# =========================================================

def _summary_card(label, value, alert=False):
    value_class = "er-value alert" if alert else "er-value"
    return (
        f'<div class="er-card compact"><div class="er-label">{label}</div>'
        f'<div class="{value_class}">{value}</div></div>'
    )


schools_present = int(filtered_df["Has_School"].sum())
no_school = int((filtered_df["Has_School"] == 0).sum())
st.html(
    '<div class="er-grid er-grid-3">'
    + _summary_card("Records", f"{len(filtered_df)}")
    + _summary_card("Villages with Local School Record", f"{schools_present}")
    + _summary_card("No Local School Record", f"{no_school}", alert=True)
    + "</div>"
)

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# DATA TABLE
# =========================================================

display_columns = [
    "Village",
    "Panchayat",
    "Accessibility_Index",
    "Dashboard_Status",
    "Nearest_School_Distance_km",
    "Has_School",
    "School_Count",
    "ML_Pattern",
    "Travel_Indicator",
    "Gap_Indicators"
]

available_display_columns = [
    col
    for col in display_columns
    if col in filtered_df.columns
]


display_df = filtered_df[
    available_display_columns
].copy()


# Rename for professional display

rename_map = {
    "Village": "Village",
    "Panchayat": "Panchayat",
    "Accessibility_Index": "Accessibility Index",
    "Dashboard_Status": "Accessibility Status",
    "Nearest_School_Distance_km":
        "Nearest School Distance (km)",
    "Has_School": "Local School Record",
    "School_Count": "School Count",
    "ML_Pattern": "ML Pattern",
    "Travel_Indicator": "Travel Indicator",
    "Gap_Indicators": "Gap Indicators"
}

display_df = display_df.rename(
    columns=rename_map
)


if "Local School Record" in display_df.columns:

    display_df[
        "Local School Record"
    ] = display_df[
        "Local School Record"
    ].map(
        {
            1: "Yes",
            0: "No"
        }
    )


if "Accessibility Index" in display_df.columns:

    display_df[
        "Accessibility Index"
    ] = display_df[
        "Accessibility Index"
    ].round(2)


if "Nearest School Distance (km)" in display_df.columns:

    display_df[
        "Nearest School Distance (km)"
    ] = display_df[
        "Nearest School Distance (km)"
    ].round(2)


if "Panchayat" in display_df.columns:
    display_df["Panchayat"] = display_df["Panchayat"].fillna("-")
st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
    column_config={
        "Accessibility Index": st.column_config.NumberColumn(format="%.2f"),
        "Nearest School Distance (km)": st.column_config.NumberColumn(format="%.2f"),
    },
)


# =========================================================
# EXPLAINABLE ACCESSIBILITY ANALYSIS
# =========================================================

st.divider()
st.subheader("Why Is This Village Flagged?")
st.caption(
    "Understand the observed indicators behind a village's "
    "accessibility status. These are rule-based explanations, "
    "not causal claims or individual model predictions."
)

if filtered_df.empty:
    st.info("No villages match the current filters.")

else:
    village_options = sorted(
        filtered_df["Village"].dropna().unique().tolist()
    )

    selected_village = st.selectbox(
        "Select a village to explain",
        options=village_options,
        key="explainability_village"
    )

    village_row = filtered_df[
        filtered_df["Village"] == selected_village
    ].iloc[0]

    score = float(village_row["Accessibility_Index"])
    has_school = int(village_row["Has_School"])
    school_count = int(village_row["School_Count"])
    distance = village_row["Nearest_School_Distance_km"]

    availability = village_row["Availability_Score"]
    proximity = village_row["Proximity_Score"]
    coverage = village_row["School_Level_Coverage_Score"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Accessibility Index", f"{score:.2f}/100")
    col2.metric(
        "Local School Record",
        "Available" if has_school == 1 else "Not recorded"
    )
    col3.metric(
        "School Count",
        f"{school_count}"
    )

    
    st.markdown("#### Score contribution breakdown")

    availability = float(availability)
    proximity = float(proximity)
    coverage = float(coverage)

    contribution_data = pd.DataFrame({
        "Component": [
            "Availability (40%)",
            "Proximity (40%)",
            "School-level coverage (20%)",
        ],
        "Raw Score": [
            availability,
            proximity,
            coverage,
        ],
        "Weighted Points": [
            0.40 * availability,
            0.40 * proximity,
            0.20 * coverage,
        ],
        "Maximum Points": [
            40,
            40,
            20,
        ],
    })

    st.dataframe(
        contribution_data.round(2),
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Weighted contribution chart")

    chart_data = contribution_data.set_index("Component")[
        ["Weighted Points"]
    ]

    st.altair_chart(
        labelled_bar_chart(
            chart_data.index, chart_data["Weighted Points"],
            "Component (weight)", "Weighted points",
            y_max=46, value_format=".1f", height=300,
        ),
        width="stretch",
    )

    calculated_score = contribution_data["Weighted Points"].sum()

    st.metric(
        "Reconstructed Accessibility Index",
        f"{calculated_score:.2f}/100",
        delta=f"{calculated_score - score:+.2f} vs stored index",
        delta_color="off",
        delta_arrow="off",
    )

    st.caption(
        "Weighted points are calculated using the project's "
        "40% availability, 40% proximity and 20% coverage weights. "
        "The reconstructed score should match the stored index "
        "apart from small rounding differences."
    )
    
    st.markdown("#### Explanation")

    if has_school == 0:
        st.warning(
            "No local school record is present for this village "
            "in the current dataset. This does not prove that "
            "no school physically exists."
        )
    else:
        st.success(
            f"The dataset records {school_count} school(s) "
            "for this village."
        )

    if pd.notna(distance):
        st.write(
            f"**Nearest-school distance proxy:** {distance:.2f} km. "
            "This is a straight-line estimate based on village-level "
            "coordinates, not road travel distance or travel time."
        )
    else:
        st.write(
            "**Nearest-school distance proxy:** unavailable "
            "in the current dataset."
        )

    if pd.notna(availability):
        st.write(f"**Availability score:** {float(availability):.2f}")

    if pd.notna(proximity):
        st.write(f"**Proximity score:** {float(proximity):.2f}")

    if pd.notna(coverage):
        st.write(
            f"**School-level coverage score:** {float(coverage):.2f}"
        )

    if score < 40:
        st.warning(
            "The village is in the Potential Gap category "
            "because its current Accessibility Index is below 40. "
            "Review the indicators above to understand its profile."
        )
    else:
        st.info(
            "The village is in the Higher category under the "
            "current dashboard's visual rule (index of 70 or above). "
            "This label is not a formal government classification."
        )

    if "ML_Pattern" in village_row.index:
        st.write(
            f"**Unsupervised ML pattern:** {village_row['ML_Pattern']}"
        )

    if "Gap_Indicators" in village_row.index:
        st.write(
            f"**Recorded gap indicators:** {village_row['Gap_Indicators']}"
        )

    st.caption(
        "The displayed indicators describe the dataset and the "
        "current scoring rules. They do not establish why a village "
        "has its observed accessibility level in a causal sense."
    )

# =========================================================
# HOW TO READ THE SCORE (LIMITATIONS)
# =========================================================
with st.expander("How to read the Accessibility Index - and its limits", expanded=False):
    _gap_mask = df["Dashboard_Status"] == "Potential Gap"
    _gap_is_no_school = bool(((df["Has_School"] == 0) == _gap_mask).all())
    st.write(
        "The index is a **project-defined exploratory indicator** "
        "(0.40 x availability + 0.40 x proximity + 0.20 x school-level coverage). "
        "It is not an official or validated government metric."
    )
    if _gap_is_no_school:
        st.info(
            f"In the current data, all {int(_gap_mask.sum())} Potential Gap villages have no "
            "recorded local school, and every village with a recorded school scores above 40. "
            "So the Potential Gap label currently coincides with 'no local school record'; "
            "the index adds a finer ranking within each group rather than a separate verdict."
        )
    st.write(
        "Proximity is a straight-line distance between village-level coordinates, scaled by the "
        "largest distance in this dataset. A village that has its own school gets distance 0 by "
        "construction. Road quality, terrain, rivers, school capacity and travel time are not "
        "measured, and no field validation has been performed."
    )

# -------------------------------
# INTERACTIVE INTERVENTION SCENARIO SIMULATOR
# -------------------------------
st.markdown("---")
st.markdown("## Interactive Intervention Scenario Simulator")
st.write(
    "Explore how explicitly assumed changes to accessibility "
    "components could affect village-level index scores. "
    "These are hypothetical scenarios, not real-world predictions. "
    "The original dataset is never modified."
)

if filtered_df.empty:
    st.info("No villages match the current filters.")
else:
    st.markdown("### Configure your hypothetical scenario")
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        intervention = st.selectbox(
            "Select intervention",
            [INTERVENTION_CONNECTIVITY, INTERVENTION_NEW_SCHOOL],
            key="edureach_intervention_type",
        )
        scope = st.selectbox(
            "Apply the assumption to",
            [SCOPE_NO_SCHOOL, SCOPE_ALL],
            key="edureach_scenario_scope",
        )
    with sim_col2:
        gap_closed_pct = st.slider(
            "Assumed percentage of component gap closed",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            help=(
                "This is a user-selected assumption, not an "
                "estimated real-world intervention effect. 0% reproduces the baseline."
            ),
            key="edureach_gap_closed_pct",
        )

    sim = simulate_scenario(filtered_df, intervention, gap_closed_pct, scope)
    summary = scenario_summary(sim)

    if intervention == INTERVENTION_CONNECTIVITY:
        scenario_description = (
            f"Connectivity scenario: assumed {gap_closed_pct}% of the remaining "
            "proximity-score gap is closed (for example, a better road or transport link). "
            "Only the Proximity component changes; availability and coverage are held constant."
        )
    else:
        scenario_description = (
            f"New-school scenario: assumed {gap_closed_pct}% of the remaining availability and "
            "proximity gaps are closed. The percentage is a stand-in for uncertainty about whether "
            "a school is built, staffed and actually used. Coverage is held constant because the "
            "school level of a new school is not modelled."
        )
    st.info(scenario_description)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Baseline Avg. Index", f"{summary['baseline_avg']:.2f}")
    m2.metric(
        "Hypothetical Scenario Avg.",
        f"{summary['scenario_avg']:.2f}",
        delta=f"{summary['scenario_avg'] - summary['baseline_avg']:+.2f}",
    )
    m3.metric("Average Assumed Change", f"{summary['avg_change']:+.2f}")
    m4.metric(
        "Villages Affected",
        f"{summary['affected']} of {summary['villages']}",
    )
    st.caption(
        f"Villages below the Potential Gap threshold ({GAP_THRESHOLD:.0f}): "
        f"baseline {summary['gap_before']} -> hypothetical {summary['gap_after']}. "
        "The threshold is this project's own cut-off."
    )
    st.warning(
        "Interpretation limits: the slider controls an assumed component change, not a measured "
        "intervention effect. The new-school scenario does not model school capacity, staffing, "
        "site suitability, construction feasibility, or actual road-network travel. "
        "Index changes use the 40% availability, 40% proximity and 20% coverage weights."
    )

    st.markdown("### Baseline vs Hypothetical Scenario")
    chart_data = pd.DataFrame(
        {
            "Average Accessibility Index": [
                summary["baseline_avg"],
                summary["scenario_avg"],
            ]
        },
        index=["Baseline", "Hypothetical Scenario"],
    )
    st.altair_chart(
        labelled_bar_chart(
            chart_data.index, chart_data["Average Accessibility Index"],
            "Scenario", "Average index (0-100)",
            y_max=100, value_format=".2f",
        ),
        width="stretch",
    )

    st.markdown("### Village-wise Scenario Comparison")
    only_changed = st.checkbox(
        "Show only villages whose index changes",
        value=True,
        key="edureach_only_changed",
    )
    scenario_display = sim[
        [
            "Village",
            "Baseline_Index",
            "Scenario_Index",
            "Scenario_Change",
            "Dashboard_Status",
            "Scenario_Status",
        ]
    ].rename(
        columns={
            "Baseline_Index": "Baseline Index",
            "Scenario_Index": "Hypothetical Index",
            "Scenario_Change": "Assumed Change",
            "Dashboard_Status": "Baseline Status",
            "Scenario_Status": "Hypothetical Status",
        }
    )
    if only_changed:
        scenario_display = scenario_display[scenario_display["Assumed Change"] > 0]
    scenario_display = scenario_display.sort_values("Assumed Change", ascending=False)
    if scenario_display.empty:
        st.info("No village index changes under the current assumptions (try a higher percentage).")
    else:
        st.dataframe(
            scenario_display.round(2),
            width="stretch",
            hide_index=True,
            column_config={
                "Baseline Index": st.column_config.NumberColumn(format="%.2f"),
                "Hypothetical Index": st.column_config.NumberColumn(format="%.2f"),
                "Assumed Change": st.column_config.NumberColumn(format="%.2f"),
            },
        )

# =========================================================
# FOOTNOTE / METHODOLOGY NOTE
# =========================================================

st.divider()

st.html(
    """
    <div class="er-note">
        <b>Methodology Note</b>
        <br>
        The EduReach Exploratory Accessibility Index combines
        school availability, proximity and observed school-level
        coverage indicators.
        <br><br>
        Nearest-school distance is calculated using
        village-level coordinate proxies and straight-line
        distance. The index is intended for exploratory
        accessibility analysis rather than a direct measurement
        of actual travel time or road-network accessibility.
        <br><br>
        The ML layer uses an unsupervised Gaussian Mixture Model
        to identify naturally occurring accessibility and
        school-coverage patterns.
    </div>
    """
)


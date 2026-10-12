import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium


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

    /* Main page */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    /* Remove excessive top spacing */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* General headings */
    h1, h2, h3 {
        font-weight: 700 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e2e8f0;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = "edureach_dashboard.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(
        "edureach_dashboard.csv not found. "
        "Please keep app.py and edureach_dashboard.csv in the same folder."
    )
    st.stop()


# =========================================================
# BASIC DATA CLEANING
# =========================================================

numeric_columns = [
    "Latitude",
    "Longitude",
    "Has_School",
    "School_Count",
    "Nearest_School_Distance_km",
    "Accessibility_Index",
    "Potential_Gap_Candidate",
    "ML_Cluster",
    "JJM_Water_Completion",
    "JJM_FHTC_Coverage",
    "Combined_Accessibility_Index",
    "Combined_Improvement"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


df["Has_School"] = df["Has_School"].fillna(0).astype(int)

df["School_Count"] = df["School_Count"].fillna(0)

df["Accessibility_Index"] = df[
    "Accessibility_Index"
].fillna(0)

df["Potential_Gap_Candidate"] = df[
    "Potential_Gap_Candidate"
].fillna(0).astype(int)

# =========================================================
# DASHBOARD VISUAL ACCESSIBILITY CLASSIFICATION
# =========================================================

def get_visual_status(score):

    if score < 40:
        return "Potential Gap"

    return "Higher"


df["Dashboard_Status"] = df[
    "Accessibility_Index"
].apply(get_visual_status)

# =========================================================
# HERO HEADER
# =========================================================

st.html(
    """
    <div style="
        padding: 34px 40px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e3a5f 100%
        );
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.16);
    ">

        <div style="
            font-size: 42px;
            font-weight: 750;
            color: #ffffff;
            margin-bottom: 8px;
            line-height: 1.1;
        ">
            🎓 EduReach AI
        </div>

        <div style="
            font-size: 22px;
            font-weight: 600;
            color: #dbeafe;
            margin-bottom: 12px;
        ">
            From School Availability to Actual Accessibility
        </div>

        <div style="
            font-size: 15px;
            color: #cbd5e1;
            line-height: 1.6;
        ">
            AI/ML & GIS-based decision-support system for
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
        """
        <div style="
            font-size:24px;
            font-weight:750;
            color:#0f172a;
            margin-bottom:4px;
        ">
            🎓 EduReach AI
        </div>

        <div style="
            font-size:13px;
            color:#64748b;
            margin-bottom:22px;
        ">
            Accessibility Intelligence Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔎 Filters")

    accessibility_filter = st.multiselect(
         "Accessibility Status",
         options=[
            "Higher",
            "Potential Gap"],
        default=["Higher",
                 "Potential Gap"]

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
        """
        <div style="
            font-size:13px;
            color:#94a3b8;
            line-height:1.7;
         padding-top:4px;
        "> 

           <div style="
              color:#64748b;
              font-weight:600;
              margin-bottom:2px;
           ">
                Study Area
            </div>

            <div style="margin-bottom:18px;">
             Shravasti — Jamunaha
            </div>


            <div style="
                color:#64748b;
                font-weight:600;
                margin-bottom:2px;
            ">
                 Village Records
            </div>

            <div style="
                color:#e2e8f0;
                font-size:18px;
                font-weight:700;
                margin-bottom:18px;
            ">
                  115
            </div>


            <div style="
                color:#64748b;
                font-weight:600;
                margin-bottom:2px;
            ">
                ML Method
            </div>

            <div style="
                color:#e2e8f0;
                line-height:1.5;
            ">
             Unsupervised Gaussian<br>
             Mixture Model
            </div>

         </div>
    """
)
    

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if accessibility_filter:
    filtered_df = filtered_df[
        filtered_df["Dashboard_Status"].isin(
            accessibility_filter
        )
    ]

if school_filter == "School Available":
    filtered_df = filtered_df[
        filtered_df["Has_School"] == 1
    ]

elif school_filter == "No Local School Record":
    filtered_df = filtered_df[
        filtered_df["Has_School"] == 0
    ]


# =========================================================
# KPI CALCULATIONS
# =========================================================

# Overall study-area metrics: use the complete dataset
total_villages = len(df)

potential_gaps = int(
    df["Potential_Gap_Candidate"].sum()
)

average_accessibility = (
    df["Accessibility_Index"].mean()
    if len(filtered_df) > 0
    else 0
)

ml_patterns = (
    df["ML_Pattern"].nunique()
    if not df.empty
    else 0
)


# =========================================================
# KPI CARDS
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.html(
        f"""
        <div style="
            background:#ffffff;
            padding:22px;
            border-radius:16px;
            border:1px solid #e2e8f0;
            box-shadow:0 5px 18px rgba(0,0,0,0.07);
            min-height:112px;
        ">

            <div style="
                font-size:14px;
                color:#475569;
                font-weight:600;
                margin-bottom:9px;
            ">
                🏘️ Total Villages
            </div>

            <div style="
                font-size:32px;
                font-weight:750;
                color:#0f172a;
            ">
                {total_villages}
            </div>

        </div>
        """
    )


with kpi2:

    st.html(
        f"""
        <div style="
            background:#ffffff;
            padding:22px;
            border-radius:16px;
            border:1px solid #e2e8f0;
            box-shadow:0 5px 18px rgba(0,0,0,0.07);
            min-height:112px;
        ">

            <div style="
                font-size:14px;
                color:#475569;
                font-weight:600;
                margin-bottom:9px;
            ">
                ⚠️ Potential Gap Candidates
            </div>

            <div style="
                font-size:32px;
                font-weight:750;
                color:#dc2626;
            ">
                {potential_gaps}
            </div>

        </div>
        """
    )


with kpi3:

    st.html(
        f"""
        <div style="
            background:#ffffff;
            padding:22px;
            border-radius:16px;
            border:1px solid #e2e8f0;
            box-shadow:0 5px 18px rgba(0,0,0,0.07);
            min-height:112px;
        ">

            <div style="
                font-size:14px;
                color:#475569;
                font-weight:600;
                margin-bottom:9px;
            ">
                📊 Avg. Accessibility
            </div>

            <div style="
                font-size:32px;
                font-weight:750;
                color:#0f172a;
            ">
                {average_accessibility:.2f}
            </div>

        </div>
        """
    )


with kpi4:

    st.html(
        f"""
        <div style="
            background:#ffffff;
            padding:22px;
            border-radius:16px;
            border:1px solid #e2e8f0;
            box-shadow:0 5px 18px rgba(0,0,0,0.07);
            min-height:112px;
        ">

            <div style="
                font-size:14px;
                color:#475569;
                font-weight:600;
                margin-bottom:9px;
            ">
                🤖 ML Patterns
            </div>

            <div style="
                font-size:32px;
                font-weight:750;
                color:#0f172a;
            ">
                {ml_patterns}
            </div>

        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)

st.divider()


# =========================================================
# GIS MAP SECTION
# =========================================================

st.subheader("🗺️ Village Accessibility Map")

st.caption(
    "Interactive spatial view of village-level accessibility "
    "patterns in the EduReach study area."
)


if len(filtered_df) > 0:

    # -----------------------------------------------------
    # MAP BOUNDS
    # -----------------------------------------------------

    min_lat = filtered_df["Latitude"].min()
    max_lat = filtered_df["Latitude"].max()

    min_lon = filtered_df["Longitude"].min()
    max_lon = filtered_df["Longitude"].max()

    center_lat = (
        min_lat + max_lat
    ) / 2

    center_lon = (
        min_lon + max_lon
    ) / 2


    # -----------------------------------------------------
    # CREATE MAP
    # -----------------------------------------------------

    m = folium.Map(
        location=[
            center_lat,
            center_lon
        ],
        zoom_start=10,
        tiles="OpenStreetMap",
        control_scale=True
    )


    # -----------------------------------------------------
    # ADD VILLAGE MARKERS
    # -----------------------------------------------------
    
    for _, row in filtered_df.iterrows():

        accessibility = float(
            row["Accessibility_Index"]
        )


        # Marker classification

        if accessibility < 40:

            marker_color = "red"

        elif accessibility <= 70:

            marker_color = "orange"

        else:

            marker_color = "green"


        # School status

        school_status = (
            "Yes"
            if row["Has_School"] == 1
            else "No"
        )


        # Distance

        distance = row[
            "Nearest_School_Distance_km"
        ]

        if pd.notna(distance):

            distance_text = (
                f"{distance:.2f} km"
            )

        else:

            distance_text = "N/A"


        # -------------------------------------------------
        # POPUP
        # -------------------------------------------------

        popup_html = f"""
        <div style="
            font-family:Arial;
            width:260px;
            line-height:1.5;
        ">

            <div style="
                font-size:18px;
                font-weight:700;
                margin-bottom:8px;
            ">
                {row['Village']}
            </div>

            <hr>

            <b>Accessibility Index:</b>
            {accessibility:.2f}

            <br>

            <b>Status:</b>
            {row['Dashboard_Status']}

            <br>

            <b>Nearest School Distance:</b>
            {distance_text}

            <br>

            <b>Local School Record:</b>
            {school_status}

            <br>

            <b>School Count:</b>
            {int(row['School_Count'])}

            <br>

            <b>ML Pattern:</b>
            {row['ML_Pattern']}

            <br><br>

            <span style="
                color:#64748b;
                font-size:12px;
            ">
                Distance uses a village-level
                coordinate proxy.
            </span>

        </div>
        """


        # -------------------------------------------------
        # MARKER
        # -------------------------------------------------

        folium.CircleMarker(
            location=[
                row["Latitude"],
                row["Longitude"]
            ],

            radius=6,

            popup=folium.Popup(
                popup_html,
                max_width=320
            ),

            tooltip=(
                f"{row['Village']} — "
                f"Accessibility: "
                f"{accessibility:.1f}"
            ),

            color=marker_color,

            fill=True,

            fill_color=marker_color,

            fill_opacity=0.78,

            weight=1.5

        ).add_to(m)


    # -----------------------------------------------------
    # FIT MAP TO ALL VILLAGES
    # -----------------------------------------------------

    m.fit_bounds(
        [
            [min_lat, min_lon],
            [max_lat, max_lon]
        ],
        padding=(25, 25)
    )


    # -----------------------------------------------------
    # MAP LEGEND
    # -----------------------------------------------------

    legend_html = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 9999;
        background: white;
        padding: 14px 16px;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.20);
        font-family: Arial;
        font-size: 13px;
        color: #1e293b;
    ">

        <div style="
            font-size:14px;
            font-weight:700;
            margin-bottom:9px;
        ">
            Accessibility
        </div>

        <div style="margin-bottom:6px;">
            <span style="
                display:inline-block;
                width:12px;
                height:12px;
                background:red;
                border-radius:50%;
                margin-right:7px;
            "></span>
            Potential Gap (&lt; 40)
        </div>

        <div>
            <span style="
                display:inline-block;
                width:12px;
                height:12px;
                background:green;
                border-radius:50%;
                margin-right:7px;
            "></span>
            Higher (≥ 40)
        </div>

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend_html)
    )


    # -----------------------------------------------------
    # DISPLAY MAP
    # -----------------------------------------------------

    st_folium(
        m,
        width=None,
        height=560,
        returned_objects=[]
    )

else:

    st.warning(
        "No villages match the selected filters."
    )


# =========================================================
# ANALYTICS SECTION
# =========================================================

st.divider()

st.subheader("📈 Accessibility Analytics")


chart_col1, chart_col2 = st.columns(2)


# =========================================================
# ACCESSIBILITY STATUS
# =========================================================


with chart_col1:
    st.markdown("#### Accessibility Status")

    status_order = ["Higher", "Potential Gap"]

    status_counts = (
        filtered_df["Dashboard_Status"]
        .value_counts()
        .reindex(status_order, fill_value=0)
    )

    st.bar_chart(status_counts)


# =========================================================
# ML PATTERNS
# =========================================================
with chart_col2:

    st.markdown("#### ML Pattern Distribution")

    pattern_counts = (
        filtered_df[
            "ML_Pattern"
        ]
        .value_counts()
    )

    pattern_counts.index = (
        pattern_counts.index
        .str.replace(
            "High Travel-Burden / No Local School",
            "High Travel Burden",
            regex=False
        )
        .str.replace(
            "Local School - Basic Coverage",
            "Basic School Coverage",
            regex=False
        )
        .str.replace(
            "Local School - Broader Coverage",
            "Broader School Coverage",
            regex=False
        )
    )

    st.bar_chart(
        pattern_counts,
        horizontal=True
    )

# =========================================================
# DATASET SECTION
# =========================================================

st.divider()

st.subheader("📊 EduReach Dataset")

st.caption(
    "Village-level accessibility, school, GIS, ML "
    "and contextual indicators."
)


# =========================================================
# DATASET SUMMARY
# =========================================================

summary_col1, summary_col2, summary_col3 = st.columns(3)


with summary_col1:

    st.html(
        f"""
        <div style="
            padding:16px;
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:12px;
        ">

            <div style="
                font-size:13px;
                color:#64748b;
            ">
                Records
            </div>

            <div style="
                font-size:24px;
                font-weight:700;
                color:#0f172a;
            ">
                {len(filtered_df)}
            </div>

        </div>
        """
    )


with summary_col2:

    schools_present = int(
        filtered_df["Has_School"].sum()
    )

    st.html(
        f"""
        <div style="
            padding:16px;
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:12px;
        ">

            <div style="
                font-size:13px;
                color:#64748b;
            ">
                Villages with Local School Record
            </div>

            <div style="
                font-size:24px;
                font-weight:700;
                color:#0f172a;
            ">
                {schools_present}
            </div>

        </div>
        """
    )


with summary_col3:

    no_school = int(
        (filtered_df["Has_School"] == 0).sum()
    )

    st.html(
        f"""
        <div style="
            padding:16px;
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:12px;
        ">

            <div style="
                font-size:13px;
                color:#64748b;
            ">
                No Local School Record
            </div>

            <div style="
                font-size:24px;
                font-weight:700;
                color:#dc2626;
            ">
                {no_school}
            </div>

        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# DATA TABLE
# =========================================================

display_columns = [
    "Village",
    "Panchayat",
    "Accessibility_Index",
    "Accessibility_Status",
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


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# EXPLAINABLE ACCESSIBILITY ANALYSIS
# =========================================================

st.divider()
st.subheader("🔍 Why Is This Village Flagged?")
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

    st.markdown("#### Observed indicators")

    indicator_data = pd.DataFrame({
        "Indicator": [
            "Availability Score",
            "Proximity Score",
            "School-Level Coverage Score"
        ],
        "Score": [
            availability,
            proximity,
            coverage
        ]
    })

    st.bar_chart(
        indicator_data.set_index("Indicator")
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
            "current dashboard's visual rule (index ≥ 40). "
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
# -------------------------------
# INTERVENTION SCENARIO SIMULATOR
# -------------------------------

st.markdown("---")
st.markdown("## 🛠️ Intervention Scenario Simulator")

st.write(
    "Compare the current accessibility scores with a pre-modelled "
    "hypothetical intervention scenario for the selected villages."
)

required_cols = [
    "Accessibility_Index",
    "Combined_Accessibility_Index",
    "Combined_Improvement",
    "Intervention_Combined",
]

missing_cols = [
    col for col in required_cols
    if col not in filtered_df.columns
]

if missing_cols:
    st.warning(
        "Simulator cannot run. Missing columns: "
        + ", ".join(missing_cols)
    )

elif filtered_df.empty:
    st.info("No villages match the current filters.")

else:
    scenario_df = filtered_df.copy()

    scenario_df["Accessibility_Index"] = pd.to_numeric(
        scenario_df["Accessibility_Index"], errors="coerce"
    )
    scenario_df["Combined_Accessibility_Index"] = pd.to_numeric(
        scenario_df["Combined_Accessibility_Index"], errors="coerce"
    )
    scenario_df["Combined_Improvement"] = pd.to_numeric(
        scenario_df["Combined_Improvement"], errors="coerce"
    )

    scenario_df = scenario_df.dropna(
        subset=[
            "Accessibility_Index",
            "Combined_Accessibility_Index",
            "Combined_Improvement",
        ]
    )

    if scenario_df.empty:
        st.warning("No valid scenario scores are available.")
    else:
        baseline_avg = scenario_df["Accessibility_Index"].mean()
        scenario_avg = scenario_df[
            "Combined_Accessibility_Index"
        ].mean()
        improvement_avg = scenario_df[
            "Combined_Improvement"
        ].mean()

        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            "Baseline Avg. Index",
            f"{baseline_avg:.2f}"
        )

        kpi2.metric(
            "Modelled Scenario Avg.",
            f"{scenario_avg:.2f}",
            delta=f"{scenario_avg - baseline_avg:+.2f}"
        )

        kpi3.metric(
            "Average Modelled Change",
            f"{improvement_avg:+.2f}"
        )

        st.caption(
            "These are pre-modelled scenario values from the dataset, "
            "not real-world outcomes or guaranteed improvements."
        )

        chart_data = pd.DataFrame({
            "Baseline": scenario_df[
                "Accessibility_Index"
            ].mean(),
            "Modelled Scenario": scenario_df[
                "Combined_Accessibility_Index"
            ].mean(),
        }, index=["Average Accessibility Index"])

        st.markdown("### 📊 Baseline vs Modelled Scenario")
        st.bar_chart(chart_data.T)

        st.markdown("### 🏘️ Village-wise Scenario Comparison")

        scenario_display = scenario_df[
            [
                "Village",
                "Accessibility_Index",
                "Combined_Accessibility_Index",
                "Combined_Improvement",
                "Intervention_Combined",
            ]
        ].rename(columns={
            "Accessibility_Index": "Baseline Index",
            "Combined_Accessibility_Index": "Modelled Index",
            "Combined_Improvement": "Modelled Change",
            "Intervention_Combined": "Scenario Description",
        })

        st.dataframe(
            scenario_display,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# FOOTNOTE / METHODOLOGY NOTE
# =========================================================

st.divider()

st.html(
    """
    <div style="
        padding:18px 20px;
        border-radius:14px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        color:#475569;
        font-size:13px;
        line-height:1.7;
    ">

        <b style="color:#0f172a;">
            Methodology Note
        </b>

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
import pandas as pd

# Load ML-enhanced EduReach dataset
df = pd.read_csv("edureach_ml_clusters.csv")


def get_travel_indicator(distance):
    if distance >= 2.5:
        return "Very High Travel Burden"
    elif distance >= 1.5:
        return "High Travel Burden"
    elif distance >= 0.75:
        return "Moderate Travel Burden"
    elif distance > 0:
        return "Low Travel Burden"
    else:
        return "No Travel Burden (Local School Record)"


def identify_gap_indicators(row):
    indicators = []

    # 1. Local school availability
    if row["Has_School"] == 0:
        indicators.append("No Local School Record")

    # 2. Travel burden
    distance = row["Nearest_School_Distance_km"]

    if distance >= 2.5:
        indicators.append("Very High Travel Burden")
    elif distance >= 1.5:
        indicators.append("High Travel Burden")
    elif distance >= 0.75:
        indicators.append("Moderate Travel Burden")

    # 3. School-level coverage
    if row["Has_School"] == 0:
        indicators.append("No Observed School-Level Coverage")
    else:
        school_level_count = sum([
            row["Has_PS"],
            row["Has_UPS"],
            row["Has_Composite"],
            row["Has_Madhyamik"]
        ])

        if school_level_count == 1:
            indicators.append("Limited Observed School-Level Coverage")

    # 4. No major gap indicator
    if not indicators:
        return "No major gap indicator detected"

    return " | ".join(indicators)


def create_jjm_context(row):
    context = []

    # JJM data availability
    if pd.notna(row["Water_Completion"]):

        completion = row["Water_Completion"]

        # JJM completion is stored as a fraction
        # Example: 0.9905 = 99.05%
        completion_percent = (
            completion * 100
            if completion <= 1
            else completion
        )

        context.append(
            f"JJM household water completion: {completion_percent:.1f}%"
        )

        # JJM certification is contextual only
        if str(row["JJM_Certified"]).strip().lower() == "yes":
            context.append("JJM village certification: Yes")

        elif str(row["JJM_Certified"]).strip().lower() == "no":
            context.append("JJM village certification: No")

    else:
        context.append("JJM village data unavailable")

    return " | ".join(context)


def create_overall_interpretation(row):

    if row["ML_Cluster"] == 0:
        return "Potential accessibility gap pattern"

    elif row["ML_Cluster"] == 1:
        return "Local school with basic coverage pattern"

    elif row["ML_Cluster"] == 2:
        return "Local school with broader coverage pattern"

    return "Pattern not classified"


# ---------------------------------------
# CREATE REFINED ANALYSIS COLUMNS
# ---------------------------------------

df["Travel_Indicator"] = df[
    "Nearest_School_Distance_km"
].apply(get_travel_indicator)

df["Gap_Indicators"] = df.apply(
    identify_gap_indicators,
    axis=1
)

df["JJM_Context"] = df.apply(
    create_jjm_context,
    axis=1
)

df["Overall_Interpretation"] = df.apply(
    create_overall_interpretation,
    axis=1
)


# ---------------------------------------
# SAVE REFINED OUTPUT
# ---------------------------------------

output_file = "edureach_refined_why_analysis.csv"

df.to_csv(
    output_file,
    index=False
)


# ---------------------------------------
# VALIDATION / OUTPUT
# ---------------------------------------

print("Refined Why Analysis completed.")
print(f"Output file: {output_file}")
print(f"Total villages analysed: {len(df)}")

print("\nML Pattern Distribution:")

print(
    df["Overall_Interpretation"]
    .value_counts()
    .to_string()
)

print("\nSample Refined Analysis:")

print(
    df[
        [
            "Village",
            "Accessibility_Index",
            "ML_Pattern",
            "Travel_Indicator",
            "Gap_Indicators",
            "JJM_Context",
            "Overall_Interpretation"
        ]
    ]
    .head(15)
    .to_string(index=False)
)
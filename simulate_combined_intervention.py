import pandas as pd

df = pd.read_csv("edureach_refined_why_analysis.csv")

MAX_DISTANCE = df["Nearest_School_Distance_km"].max()


def calculate_accessibility(
    has_school,
    distance,
    has_ps,
    has_ups,
    has_composite,
    has_madhyamik
):
    availability_score = 100 if has_school == 1 else 0

    proximity_score = 100 * (1 - distance / MAX_DISTANCE)
    proximity_score = max(0, min(100, proximity_score))

    school_level_score = (
        has_ps * 25
        + has_ups * 25
        + has_composite * 30
        + has_madhyamik * 20
    )

    school_level_score = min(100, school_level_score)

    accessibility_index = (
        0.40 * availability_score
        + 0.40 * proximity_score
        + 0.20 * school_level_score
    )

    return round(accessibility_index, 2)


# --------------------------------------------------
# CORRECTED COMBINED INTERVENTION
# --------------------------------------------------

df["Combined_Has_School"] = df["Has_School"]

df["Combined_Distance_km"] = df["Nearest_School_Distance_km"]

gap_mask = df["Has_School"] == 0

# For villages without a local school:
# hypothetical suitable school is introduced locally.
# Therefore village-level proximity proxy becomes 0 km.

df.loc[gap_mask, "Combined_Has_School"] = 1
df.loc[gap_mask, "Combined_Distance_km"] = 0


# --------------------------------------------------
# Calculate combined accessibility
# --------------------------------------------------

df["Combined_Accessibility_Index"] = df.apply(
    lambda row: calculate_accessibility(
        row["Combined_Has_School"],
        row["Combined_Distance_km"],
        row["Has_PS"],
        row["Has_UPS"],
        row["Has_Composite"],
        row["Has_Madhyamik"]
    ),
    axis=1
)


# --------------------------------------------------
# Additional connectivity benefit
# --------------------------------------------------

# Connectivity improvement is represented separately
# rather than incorrectly changing the local-school
# distance proxy.

df["Connectivity_Improvement_Potential"] = 0.0

# For villages that already have a local school,
# there is no observed travel distance in this
# village-level proxy, so no additional distance
# reduction is applied.

# For villages without a local school, the new-school
# intervention already creates local access.


df["Combined_Improvement"] = (
    df["Combined_Accessibility_Index"]
    - df["Accessibility_Index"]
)

df["Intervention_Combined"] = (
    "New Suitable School + Improved Connectivity - "
    "Modelled Scenario"
)


output_file = "edureach_combined_intervention_corrected.csv"

df.to_csv(output_file, index=False)


print("Corrected Combined Intervention Simulation completed.")
print(f"Output file: {output_file}")
print(f"Total villages: {len(df)}")
print(
    f"Villages affected by combined scenario: "
    f"{gap_mask.sum()}"
)

print("\nAverage Accessibility:")

print(
    f"Baseline: "
    f"{df['Accessibility_Index'].mean():.2f}"
)

print(
    f"Combined Scenario: "
    f"{df['Combined_Accessibility_Index'].mean():.2f}"
)

print(
    f"Average Improvement: "
    f"{df['Combined_Improvement'].mean():.2f}"
)


print("\nTop 15 affected villages:")

print(
    df[gap_mask][
        [
            "Village",
            "Nearest_School_Distance_km",
            "Accessibility_Index",
            "Combined_Accessibility_Index",
            "Combined_Improvement"
        ]
    ]
    .sort_values(
        "Combined_Improvement",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)
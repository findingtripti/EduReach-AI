import pandas as pd

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("edureach_refined_why_analysis.csv")

# Maximum observed distance used by the existing index
MAX_DISTANCE = df["Nearest_School_Distance_km"].max()


# --------------------------------------------------
# ACCESSIBILITY CALCULATION
# --------------------------------------------------

def calculate_accessibility(
    has_school,
    distance,
    has_ps,
    has_ups,
    has_composite,
    has_madhyamik
):
    # 40% Availability
    availability_score = 100 if has_school == 1 else 0

    # 40% Proximity
    proximity_score = 100 * (
        1 - distance / MAX_DISTANCE
    )

    proximity_score = max(
        0,
        min(100, proximity_score)
    )

    # 20% School-level coverage
    school_level_score = (
        has_ps * 25
        + has_ups * 25
        + has_composite * 30
        + has_madhyamik * 20
    )

    school_level_score = min(
        100,
        school_level_score
    )

    # Final index
    accessibility_index = (
        0.40 * availability_score
        + 0.40 * proximity_score
        + 0.20 * school_level_score
    )

    return round(accessibility_index, 2)


# --------------------------------------------------
# SCENARIO 2:
# NEW SUITABLE SCHOOL ACCESS
# --------------------------------------------------

# Apply the scenario only to villages
# without a local school record.

df["Scenario2_Has_School"] = df["Has_School"]
df["Scenario2_Distance_km"] = df["Nearest_School_Distance_km"]

gap_mask = df["Has_School"] == 0

df.loc[gap_mask, "Scenario2_Has_School"] = 1
df.loc[gap_mask, "Scenario2_Distance_km"] = 0


# --------------------------------------------------
# CALCULATE SCENARIO INDEX
# --------------------------------------------------

df["Scenario2_Accessibility_Index"] = df.apply(
    lambda row: calculate_accessibility(
        row["Scenario2_Has_School"],
        row["Scenario2_Distance_km"],
        row["Has_PS"],
        row["Has_UPS"],
        row["Has_Composite"],
        row["Has_Madhyamik"]
    ),
    axis=1
)


# --------------------------------------------------
# BEFORE vs AFTER
# --------------------------------------------------

df["Scenario2_Improvement"] = (
    df["Scenario2_Accessibility_Index"]
    - df["Accessibility_Index"]
)

df["Scenario2_Distance_Reduction_km"] = (
    df["Nearest_School_Distance_km"]
    - df["Scenario2_Distance_km"]
)


# --------------------------------------------------
# SCENARIO LABEL
# --------------------------------------------------

df["Intervention_Scenario_2"] = (
    "New Suitable School Access - Modelled Scenario"
)


# --------------------------------------------------
# SAVE OUTPUT
# --------------------------------------------------

output_file = "edureach_new_school_simulation.csv"

df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("New School Access Simulation completed.")
print(f"Output file: {output_file}")
print(f"Total villages: {len(df)}")
print(f"Villages affected by scenario: {gap_mask.sum()}")

print("\nAverage Accessibility:")
print(
    f"Baseline: "
    f"{df['Accessibility_Index'].mean():.2f}"
)

print(
    f"Modelled Scenario: "
    f"{df['Scenario2_Accessibility_Index'].mean():.2f}"
)

print(
    f"Average Improvement: "
    f"{df['Scenario2_Improvement'].mean():.2f}"
)

print("\nTop 15 affected villages:")

print(
    df[gap_mask][
        [
            "Village",
            "Nearest_School_Distance_km",
            "Accessibility_Index",
            "Scenario2_Accessibility_Index",
            "Scenario2_Improvement"
        ]
    ]
    .sort_values(
        "Scenario2_Improvement",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)
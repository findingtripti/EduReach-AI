import pandas as pd

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("edureach_refined_why_analysis.csv")


# --------------------------------------------------
# BASELINE VALUES
# --------------------------------------------------

# Maximum observed nearest-school distance
MAX_DISTANCE = df["Nearest_School_Distance_km"].max()


# --------------------------------------------------
# FUNCTION: CALCULATE ACCESSIBILITY INDEX
# --------------------------------------------------

def calculate_accessibility(
    has_school,
    distance,
    has_ps,
    has_ups,
    has_composite,
    has_madhyamik
):
    # Availability component
    availability_score = 100 if has_school == 1 else 0

    # Proximity component
    proximity_score = (
        100 * (1 - distance / MAX_DISTANCE)
    )

    proximity_score = max(
        0,
        min(100, proximity_score)
    )

    # School-level coverage component
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

    # Final EduReach Accessibility Index
    accessibility_index = (
        0.40 * availability_score
        + 0.40 * proximity_score
        + 0.20 * school_level_score
    )

    return round(accessibility_index, 2)


# --------------------------------------------------
# SCENARIO 1:
# IMPROVED CONNECTIVITY
# --------------------------------------------------

# Modelled assumption:
# Travel distance is reduced by 50%.
# This is a hypothetical scenario, NOT a real prediction.

df["Scenario_Distance_km"] = (
    df["Nearest_School_Distance_km"] * 0.50
)

df["Scenario_Accessibility_Index"] = df.apply(
    lambda row: calculate_accessibility(
        row["Has_School"],
        row["Scenario_Distance_km"],
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

df["Accessibility_Improvement"] = (
    df["Scenario_Accessibility_Index"]
    - df["Accessibility_Index"]
)

df["Distance_Reduction_km"] = (
    df["Nearest_School_Distance_km"]
    - df["Scenario_Distance_km"]
)


# --------------------------------------------------
# SCENARIO LABEL
# --------------------------------------------------

df["Intervention_Scenario"] = (
    "Improved Connectivity - 50% Travel Burden Reduction"
)


# --------------------------------------------------
# SAVE RESULT
# --------------------------------------------------

output_file = "edureach_intervention_simulation.csv"

df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# VALIDATION OUTPUT
# --------------------------------------------------

print("Intervention Simulation completed.")
print(f"Output file: {output_file}")
print(f"Total villages: {len(df)}")

print("\nAverage Accessibility:")
print(
    f"Baseline: {df['Accessibility_Index'].mean():.2f}"
)

print(
    f"Modelled Scenario: "
    f"{df['Scenario_Accessibility_Index'].mean():.2f}"
)

print(
    f"Average Improvement: "
    f"{df['Accessibility_Improvement'].mean():.2f}"
)

print("\nTop 15 villages by modelled improvement:")

print(
    df[
        [
            "Village",
            "Nearest_School_Distance_km",
            "Scenario_Distance_km",
            "Accessibility_Index",
            "Scenario_Accessibility_Index",
            "Accessibility_Improvement"
        ]
    ]
    .sort_values(
        "Accessibility_Improvement",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)
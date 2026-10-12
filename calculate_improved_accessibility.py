import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. Load integrated EduReach dataset
# --------------------------------------------------

df = pd.read_csv("edureach_jjm_integrated.csv")

# --------------------------------------------------
# 2. School Availability Score
# --------------------------------------------------

df["Availability_Score"] = np.where(
    df["Has_School"] == 1,
    100,
    0
)

# --------------------------------------------------
# 3. Proximity Score
# --------------------------------------------------
# Lower distance = better proximity
# Uses observed maximum distance in the pilot dataset.

max_distance = df["Nearest_School_Distance_km"].max()

if max_distance > 0:
    df["Proximity_Score"] = (
        100
        * (1 - df["Nearest_School_Distance_km"] / max_distance)
    ).clip(0, 100)
else:
    df["Proximity_Score"] = 100

# --------------------------------------------------
# 4. School-Level Coverage Score
# --------------------------------------------------
# We use presence of school categories, not school count.
#
# PS          = 25 points
# UPS         = 25 points
# Composite   = 30 points
# Madhyamik   = 20 points
#
# Maximum = 100
#
# Raw categories are preserved.
# Composite is NOT artificially split into PS + UPS.

df["School_Level_Coverage_Score"] = (
    df["Has_PS"] * 25
    + df["Has_UPS"] * 25
    + df["Has_Composite"] * 30
    + df["Has_Madhyamik"] * 20
).clip(0, 100)

# --------------------------------------------------
# 5. Final EduReach Accessibility Index
# --------------------------------------------------

df["Accessibility_Index"] = (
    0.40 * df["Availability_Score"]
    + 0.40 * df["Proximity_Score"]
    + 0.20 * df["School_Level_Coverage_Score"]
)

# Round for readability
df["Accessibility_Index"] = df["Accessibility_Index"].round(2)

# --------------------------------------------------
# 6. Exploratory status categories
# --------------------------------------------------
# These are analytical categories, NOT government thresholds.

def classify_accessibility(score):
    if score < 40:
        return "Potential Gap"
    elif score < 70:
        return "Moderate"
    else:
        return "Higher"

df["Accessibility_Status"] = df["Accessibility_Index"].apply(
    classify_accessibility
)

# --------------------------------------------------
# 7. Gap candidate flag
# --------------------------------------------------

df["Potential_Gap_Candidate"] = np.where(
    df["Accessibility_Index"] < 40,
    1,
    0
)

# --------------------------------------------------
# 8. Save final dataset
# --------------------------------------------------

output_file = "edureach_improved_accessibility.csv"

df.to_csv(
    output_file,
    index=False
)

# --------------------------------------------------
# 9. Verification
# --------------------------------------------------

print("Improved Accessibility Index completed.")

print("\nTotal villages:", len(df))

print("\nAccessibility Index statistics:")
print(
    df["Accessibility_Index"]
    .describe()
    .round(2)
    .to_string()
)

print("\nAccessibility Status:")
print(
    df["Accessibility_Status"]
    .value_counts()
    .to_string()
)

print(
    "\nPotential Gap Candidates:",
    df["Potential_Gap_Candidate"].sum()
)

print("\nLowest accessibility villages:")

print(
    df[
        [
            "Village",
            "Nearest_School_Distance_km",
            "Availability_Score",
            "Proximity_Score",
            "School_Level_Coverage_Score",
            "Accessibility_Index",
            "Accessibility_Status"
        ]
    ]
    .sort_values("Accessibility_Index")
    .head(10)
    .to_string(index=False)
)

print("\nOutput saved as:", output_file)
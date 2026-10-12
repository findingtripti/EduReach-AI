import pandas as pd
import numpy as np

# Load accessibility base dataset
df = pd.read_csv("edureach_accessibility_base.csv")

# ---------------------------------------------------
# 1. Distance component
# ---------------------------------------------------
# Maximum observed distance in the pilot dataset
max_distance = df["Nearest_School_Distance_km"].max()

# Convert distance into a 0-100 accessibility component.
# 0 km = 100, maximum observed distance = 0.
df["Distance_Access_Score"] = (
    100 * (1 - df["Nearest_School_Distance_km"] / max_distance)
).clip(0, 100)

# ---------------------------------------------------
# 2. School availability component
# ---------------------------------------------------
df["School_Availability_Score"] = np.where(
    df["Has_School"] == 1,
    100,
    0
)

# ---------------------------------------------------
# 3. Baseline Accessibility Score
# ---------------------------------------------------
# Equal weighting for this MVP baseline.
df["Accessibility_Score"] = (
    0.50 * df["School_Availability_Score"]
    + 0.50 * df["Distance_Access_Score"]
).round(2)

# ---------------------------------------------------
# 4. Exploratory status
# ---------------------------------------------------
# These labels are NOT policy thresholds.
# They are only for exploratory visualization.
df["Accessibility_Status"] = pd.cut(
    df["Accessibility_Score"],
    bins=[-1, 40, 70, 100],
    labels=[
        "Lower Accessibility",
        "Moderate Accessibility",
        "Higher Accessibility"
    ]
)

# ---------------------------------------------------
# Save output
# ---------------------------------------------------
output_file = "edureach_accessibility_score.csv"
df.to_csv(output_file, index=False)

print("======================================")
print("EDUREACH ACCESSIBILITY SCORE")
print("======================================")

print("Total villages:", len(df))

print("\nAccessibility score statistics:")
print(df["Accessibility_Score"].describe().round(2))

print("\nStatus distribution:")
print(df["Accessibility_Status"].value_counts())

print("\nLowest accessibility villages:")
print(
    df[
        [
            "Village",
            "Has_School",
            "Nearest_School_Distance_km",
            "Accessibility_Score",
            "Accessibility_Status"
        ]
    ]
    .sort_values("Accessibility_Score")
    .head(10)
    .to_string(index=False)
)

print("\nSaved:", output_file)
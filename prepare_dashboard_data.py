import pandas as pd

# Verified master analytical dataset
input_file = "edureach_combined_intervention_corrected.csv"

# Dashboard-ready output
output_file = "edureach_dashboard.csv"

df = pd.read_csv(input_file)

dashboard_columns = [
    # Location
    "Village",
    "Village_Code",
    "Latitude",
    "Longitude",
    "Panchayat",

    # School availability & coverage
    "Has_School",
    "School_Count",
    "School_Types",
    "School_Water_Yes",
    "Water_Connected_School_Count",
    "Has_PS",
    "Has_UPS",
    "Has_Composite",
    "Has_Madhyamik",

    # Accessibility
    "Nearest_School_Distance_km",
    "Availability_Score",
    "Proximity_Score",
    "School_Level_Coverage_Score",
    "Accessibility_Index",
    "Accessibility_Status",
    "Potential_Gap_Candidate",

    # ML
    "ML_Cluster",
    "ML_Pattern",

    # Why Analysis
    "Travel_Indicator",
    "Gap_Indicators",
    "Overall_Interpretation",

    # JJM contextual indicators
    "JJM_Households",
    "JJM_FHTC_Households",
    "JJM_Water_Completion",
    "JJM_Certified",
    "JJM_FHTC_Coverage",
    "JJM_Context",

    # Intervention
    "Combined_Accessibility_Index",
    "Combined_Improvement",
    "Intervention_Combined"
]

# Check that all required columns exist
missing_columns = [
    col for col in dashboard_columns
    if col not in df.columns
]

if missing_columns:
    print("ERROR: Missing columns:")
    for col in missing_columns:
        print("-", col)
    raise SystemExit(1)

# Create dashboard dataset
dashboard_df = df[dashboard_columns].copy()

# Save
dashboard_df.to_csv(output_file, index=False)

print("Dashboard dataset created successfully.")
print(f"Output file: {output_file}")
print(f"Rows: {len(dashboard_df)}")
print(f"Columns: {len(dashboard_df.columns)}")

print("\nDashboard columns:")
print(dashboard_df.columns.tolist())
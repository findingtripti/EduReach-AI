import pandas as pd

# Load existing EduReach village + school dataset
df = pd.read_csv("edureach_school_indicators.csv")

# Load JJM data
jjm = pd.read_excel("Reports.xlsx", sheet_name="Posts")

# Filter Shravasti + Jamunaha
jjm = jjm[
    (jjm["District Name"].astype(str).str.strip().str.lower() == "shravasti")
    & (jjm["Block Name"].astype(str).str.strip().str.lower() == "jamunaha")
].copy()

# Keep only required JJM indicators
jjm = jjm[
    [
        "Village Name",
        "households",
        "FHTC",
        "Complete %",
        "Is Certified"
    ]
].copy()

# Clean village names
df["Village"] = df["Village"].astype(str).str.strip()
jjm["Village Name"] = jjm["Village Name"].astype(str).str.strip()

# Create normalized names for case-insensitive matching
df["_Village_Match"] = df["Village"].str.lower()
jjm["_Village_Match"] = jjm["Village Name"].str.lower()
# Remove old JJM indicator columns if already present
old_jjm_columns = [
    "JJM_Households",
    "JJM_FHTC_Households",
    "JJM_Water_Completion",
    "JJM_Certified",
    "JJM_FHTC_Coverage"
]

df = df.drop(
    columns=[c for c in old_jjm_columns if c in df.columns],
    errors="ignore"
)


# Remove old JJM indicator columns if already present
old_jjm_columns = [
    "JJM_Households",
    "JJM_FHTC_Households",
    "JJM_Water_Completion",
    "JJM_Certified",
    "JJM_FHTC_Coverage"
]

df = df.drop(
    columns=[c for c in old_jjm_columns if c in df.columns],
    errors="ignore"
)

# Rename JJM columns
jjm = jjm.rename(
    columns={
        "Village Name": "JJM_Village",
        "households": "JJM_Households",
        "FHTC": "JJM_FHTC_Households",
        "Complete %": "JJM_Water_Completion",
        "Is Certified": "JJM_Certified"
    }
)
# Merge using village name
result = df.merge(
    jjm,
    on="_Village_Match",
    how="left"
)
# Remove helper column
result.drop(
    columns=["_Village_Match", "JJM_Village"],
    inplace=True,
    errors="ignore"
)

# Convert numeric fields
result["JJM_Households"] = pd.to_numeric(
    result["JJM_Households"], errors="coerce"
)

result["JJM_FHTC_Households"] = pd.to_numeric(
    result["JJM_FHTC_Households"], errors="coerce"
)

result["JJM_Water_Completion"] = pd.to_numeric(
    result["JJM_Water_Completion"], errors="coerce"
)

# Calculate FHTC coverage percentage
result["JJM_FHTC_Coverage"] = (
    result["JJM_FHTC_Households"]
    / result["JJM_Households"]
    * 100
)

# Save integrated dataset
result.to_csv(
    "edureach_jjm_integrated.csv",
    index=False
)

# Verification
print("JJM integration completed.")
print("Total villages:", len(result))

print(
    "Villages with JJM data:",
    result["JJM_Households"].notna().sum()
)

print(
    "Villages without JJM data:",
    result["JJM_Households"].isna().sum()
)

print(
    "JJM households represented:",
    result["JJM_Households"].sum()
)

print(
    "JJM FHTC households represented:",
    result["JJM_FHTC_Households"].sum()
)

print("\nSample integrated records:")
print(
    result[
        [
            "Village",
            "School_Count",
            "Has_PS",
            "Has_UPS",
            "Has_Composite",
            "JJM_Households",
            "JJM_FHTC_Households",
            "JJM_Water_Completion",
            "JJM_FHTC_Coverage",
            "JJM_Certified"
        ]
    ].head(10).to_string(index=False)
)

print("\nOutput saved as: edureach_jjm_integrated.csv")
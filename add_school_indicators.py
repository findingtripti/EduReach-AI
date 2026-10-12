import pandas as pd

# ---------------------------------------------------
# Load datasets
# ---------------------------------------------------

villages = pd.read_csv("edureach_accessibility_base.csv")
schools = pd.read_csv("jamunaha_schools_with_coordinates.csv")

# ---------------------------------------------------
# Remove old school-indicator columns from village file
# ---------------------------------------------------

columns_to_remove = [
    "School_Count",
    "School_Types",
    "Has_PS",
    "Has_UPS",
    "Has_Composite",
    "Has_Madhyamik",
    "Water_Connected_School_Count"
]

villages = villages.drop(
    columns=[
        col for col in columns_to_remove
        if col in villages.columns
    ]
)

# ---------------------------------------------------
# Clean school data
# ---------------------------------------------------

schools["VillageName"] = (
    schools["VillageName"]
    .astype(str)
    .str.strip()
)

schools["School Type"] = (
    schools["School Type"]
    .astype(str)
    .str.strip()
)

schools["Water Connection Status"] = (
    schools["Water Connection Status"]
    .astype(str)
    .str.strip()
)

# ---------------------------------------------------
# Create school-type indicators
# ---------------------------------------------------

schools["Is_PS"] = schools["School Type"].str.contains(
    "PS", case=False, na=False
).astype(int)

schools["Is_UPS"] = schools["School Type"].str.contains(
    "UPS", case=False, na=False
).astype(int)

schools["Is_Composite"] = schools["School Type"].str.contains(
    "Composite", case=False, na=False
).astype(int)

schools["Is_Madhyamik"] = schools["School Type"].str.contains(
    "Madhyamik", case=False, na=False
).astype(int)

schools["Has_Water"] = (
    schools["Water Connection Status"]
    .str.lower()
    .eq("yes")
    .astype(int)
)

# ---------------------------------------------------
# Aggregate school data by village
# ---------------------------------------------------

school_indicators = (
    schools
    .groupby("VillageName")
    .agg(
        School_Count=("School Name", "count"),
        School_Types=(
            "School Type",
            lambda x: " | ".join(sorted(set(x)))
        ),
        Has_PS=("Is_PS", "max"),
        Has_UPS=("Is_UPS", "max"),
        Has_Composite=("Is_Composite", "max"),
        Has_Madhyamik=("Is_Madhyamik", "max"),
        Water_Connected_School_Count=("Has_Water", "sum")
    )
    .reset_index()
)

school_indicators = school_indicators.rename(
    columns={"VillageName": "Village"}
)

# ---------------------------------------------------
# Merge
# ---------------------------------------------------

df = villages.merge(
    school_indicators,
    on="Village",
    how="left"
)

# ---------------------------------------------------
# Fill missing values
# ---------------------------------------------------

df["School_Count"] = (
    df["School_Count"]
    .fillna(0)
    .astype(int)
)

df["School_Types"] = (
    df["School_Types"]
    .fillna("No school record")
)

for col in [
    "Has_PS",
    "Has_UPS",
    "Has_Composite",
    "Has_Madhyamik",
    "Water_Connected_School_Count"
]:
    df[col] = (
        df[col]
        .fillna(0)
        .astype(int)
    )

# ---------------------------------------------------
# Save
# ---------------------------------------------------

output_file = "edureach_school_indicators.csv"

df.to_csv(
    output_file,
    index=False
)

# ---------------------------------------------------
# Verification
# ---------------------------------------------------

print("======================================")
print("EDUREACH SCHOOL INDICATORS")
print("======================================")

print("Total villages:", len(df))

print(
    "Villages with school indicators:",
    (df["School_Count"] > 0).sum()
)

print(
    "Villages without school records:",
    (df["School_Count"] == 0).sum()
)

print(
    "Total schools represented:",
    df["School_Count"].sum()
)

print("\nSchool type coverage:")

print(
    "Villages with PS:",
    df["Has_PS"].sum()
)

print(
    "Villages with UPS:",
    df["Has_UPS"].sum()
)

print(
    "Villages with Composite:",
    df["Has_Composite"].sum()
)

print(
    "Villages with Madhyamik:",
    df["Has_Madhyamik"].sum()
)

print(
    "Water-connected schools:",
    df["Water_Connected_School_Count"].sum()
)

print("\nSample:")
print(
    df[
        [
            "Village",
            "School_Count",
            "School_Types",
            "Has_PS",
            "Has_UPS",
            "Has_Composite",
            "Has_Madhyamik",
            "Water_Connected_School_Count"
        ]
    ]
    .head(15)
    .to_string(index=False)
)

print("\nSaved:", output_file)
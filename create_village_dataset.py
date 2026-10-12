import pandas as pd

# ==========================================
# 1. Village master - all 115 Jamunaha villages
# ==========================================
villages = pd.read_csv("jamunaha_villages.csv")


def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("  ", " ")
    )


villages["match_name"] = villages["village_name"].apply(normalize)


# ==========================================
# 2. School data - 170 schools
# ==========================================
schools = pd.read_csv("jamunaha_schools_with_coordinates.csv")

schools["match_name"] = schools["VillageName"].apply(normalize)


# Count schools per village
school_counts = (
    schools.groupby("match_name")
    .agg(
        School_Count=("School Name", "count"),
        School_Water_Yes=(
            "Water Connection Status",
            lambda x: (x.astype(str).str.lower() == "yes").sum()
        )
    )
    .reset_index()
)


# School type information
school_types = (
    schools.groupby("match_name")["School Type"]
    .apply(lambda x: " | ".join(sorted(set(x.astype(str)))))
    .reset_index(name="School_Types")
)


# ==========================================
# 3. Combine school information with 115 villages
# ==========================================
village_df = villages.merge(
    school_counts,
    on="match_name",
    how="left"
)

village_df = village_df.merge(
    school_types,
    on="match_name",
    how="left"
)


# ==========================================
# 4. Fill villages having no school record
# ==========================================
village_df["School_Count"] = (
    village_df["School_Count"]
    .fillna(0)
    .astype(int)
)

village_df["School_Water_Yes"] = (
    village_df["School_Water_Yes"]
    .fillna(0)
    .astype(int)
)

village_df["Has_School"] = (
    village_df["School_Count"] > 0
).astype(int)

village_df["School_Types"] = (
    village_df["School_Types"]
    .fillna("No school record")
)


# ==========================================
# 5. Add JJM Village Information
# ==========================================
jjm = pd.read_excel("Reports.xlsx")

jjm = jjm[
    (jjm["District Name"].astype(str).str.strip().str.lower() == "shravasti") &
    (jjm["Block Name"].astype(str).str.strip().str.lower() == "jamunaha")
].copy()

jjm["match_name"] = jjm["Village Name"].apply(normalize)

jjm = jjm[
    [
        "match_name",
        "Panchayat Name",
        "IMIS Village Code",
        "households",
        "FHTC",
        "Complete %",
        "Is Certified"
    ]
]


village_df = village_df.merge(
    jjm,
    on="match_name",
    how="left"
)


# ==========================================
# 6. Rename columns
# ==========================================
village_df = village_df.rename(
    columns={
        "village_name": "Village",
        "village_code": "Village_Code",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "Panchayat Name": "Panchayat",
        "IMIS Village Code": "JJM_IMIS_Code",
        "FHTC": "FHTC_Households",
        "Complete %": "Water_Completion",
        "Is Certified": "JJM_Certified"
    }
)


# ==========================================
# 7. Arrange final columns
# ==========================================
columns = [
    "Village",
    "Village_Code",
    "Latitude",
    "Longitude",
    "Panchayat",
    "School_Count",
    "Has_School",
    "School_Types",
    "School_Water_Yes",
    "JJM_IMIS_Code",
    "households",
    "FHTC_Households",
    "Water_Completion",
    "JJM_Certified"
]

village_df = village_df[columns]


# ==========================================
# 8. Quality checks
# ==========================================
print("\n========== VILLAGE DATASET ==========")

print("Total villages:", len(village_df))

print(
    "Villages with school:",
    village_df["Has_School"].sum()
)

print(
    "Villages without school:",
    (village_df["Has_School"] == 0).sum()
)

print(
    "Villages with JJM data:",
    village_df["JJM_IMIS_Code"].notna().sum()
)

print(
    "Villages without JJM data:",
    village_df["JJM_IMIS_Code"].isna().sum()
)

print(
    "Missing coordinates:",
    village_df["Latitude"].isna().sum()
)


# ==========================================
# 9. Save
# ==========================================
village_df.to_csv(
    "edureach_village_master.csv",
    index=False
)

print("\nSaved: edureach_village_master.csv")

print("\nFirst 10 villages:")
print(village_df.head(10).to_string(index=False))
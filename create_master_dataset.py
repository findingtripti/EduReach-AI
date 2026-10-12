import pandas as pd

# -----------------------------
# 1. Load JJM Village Details
# -----------------------------
jjm = pd.read_excel("Reports.xlsx")

# Keep only Shravasti -> Jamunaha
jjm = jjm[
    (jjm["District Name"].astype(str).str.strip().str.lower() == "shravasti") &
    (jjm["Block Name"].astype(str).str.strip().str.lower() == "jamunaha")
].copy()

# Normalize village name
def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("  ", " ")
    )

jjm["match_name"] = jjm["Village Name"].apply(normalize)


# -----------------------------
# 2. Load Village Coordinates
# -----------------------------
villages = pd.read_csv("jamunaha_villages.csv")

villages["match_name"] = villages["village_name"].apply(normalize)

villages = villages[
    ["match_name", "village_code", "latitude", "longitude"]
]


# -----------------------------
# 3. Load School Data
# -----------------------------
schools = pd.read_csv("jamunaha_schools_with_coordinates.csv")

# Only required school fields
schools = schools[
    [
        "VillageName",
        "School Name",
        "School Type",
        "UDISE Code",
        "Water Connection Status"
    ]
].copy()

schools["match_name"] = schools["VillageName"].apply(normalize)


# -----------------------------
# 4. Attach Village Coordinates
# -----------------------------
schools = schools.merge(
    villages,
    on="match_name",
    how="left"
)


# -----------------------------
# 5. Attach JJM Village Data
# -----------------------------
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

master = schools.merge(
    jjm,
    on="match_name",
    how="left"
)


# -----------------------------
# 6. Rename Columns
# -----------------------------
master = master.rename(
    columns={
        "VillageName": "Village",
        "School Name": "School",
        "School Type": "School_Type",
        "UDISE Code": "UDISE_Code",
        "Water Connection Status": "School_Water_Connection",
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


# -----------------------------
# 7. Quality Checks
# -----------------------------
print("\n========== MASTER DATASET ==========")
print("Total school records:", len(master))
print("Missing latitude:", master["Latitude"].isna().sum())
print("Missing longitude:", master["Longitude"].isna().sum())
print("Missing JJM data:", master["JJM_IMIS_Code"].isna().sum())


# -----------------------------
# 8. Save
# -----------------------------
master.to_csv(
    "edureach_jamunaha_master.csv",
    index=False
)

print("\nSaved: edureach_jamunaha_master.csv")

print("\nColumns:")
print(list(master.columns))
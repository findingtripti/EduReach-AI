import pandas as pd

# School data
schools = pd.read_excel("Reports (1).xlsx")

# Only Shravasti -> Jamunaha
schools = schools[
    (schools["District Name"].astype(str).str.strip().str.lower() == "shravasti") &
    (schools["Block"].astype(str).str.strip().str.lower() == "jamunaha")
].copy()

# Village master with coordinates
villages = pd.read_csv("jamunaha_villages.csv")


def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("  ", " ")
    )


schools["match_name"] = schools["VillageName"].apply(normalize)
villages["match_name"] = villages["village_name"].apply(normalize)

# Match school village with KML village
matched = schools.merge(
    villages[["match_name", "village_code", "latitude", "longitude"]],
    on="match_name",
    how="left"
)

# Results
total = len(matched)
matched_count = matched["latitude"].notna().sum()
unmatched_count = matched["latitude"].isna().sum()

print("\nTotal Jamunaha schools:", total)
print("Schools with village coordinates:", matched_count)
print("Schools without village coordinates:", unmatched_count)

print("\n--- UNMATCHED SCHOOL VILLAGES ---")
print(
    matched.loc[
        matched["latitude"].isna(),
        ["VillageName", "School Name", "UDISE Code"]
    ].drop_duplicates().to_string(index=False)
)

# Save complete matched dataset
matched.to_csv("jamunaha_schools_with_coordinates.csv", index=False)

print("\nSaved: jamunaha_schools_with_coordinates.csv")
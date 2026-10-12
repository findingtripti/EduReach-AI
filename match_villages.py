import pandas as pd

# JJM Village Details
jjm = pd.read_excel("Reports.xlsx")

jjm = jjm[
    (jjm["District Name"].astype(str).str.strip().str.lower() == "shravasti") &
    (jjm["Block Name"].astype(str).str.strip().str.lower() == "jamunaha")
].copy()

# KML village master
kml = pd.read_csv("jamunaha_villages.csv")

# Normalize village names
def normalize(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("  ", " ")
    )

jjm["match_name"] = jjm["Village Name"].apply(normalize)
kml["match_name"] = kml["village_name"].apply(normalize)

# Match
merged = jjm.merge(
    kml,
    on="match_name",
    how="left",
    suffixes=("_jjm", "_kml")
)

# Show results
print("\nTotal JJM Jamunaha villages:", len(jjm))
print("Exact name matches:", merged["village_code"].notna().sum())
print("Unmatched:", merged["village_code"].isna().sum())

print("\n--- UNMATCHED JJM VILLAGES ---")
print(
    merged.loc[
        merged["village_code"].isna(),
        ["Village Name", "IMIS Village Code"]
    ].to_string(index=False)
)

# Save result
merged.to_csv("jamunaha_jjm_kml_matched.csv", index=False)

print("\nSaved: jamunaha_jjm_kml_matched.csv")
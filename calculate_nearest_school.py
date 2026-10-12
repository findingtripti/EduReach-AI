import pandas as pd
from sklearn.metrics import pairwise_distances
import numpy as np

# Load village master
villages = pd.read_csv("edureach_village_master.csv")

# Load school data
schools = pd.read_csv("jamunaha_schools_with_coordinates.csv")

# Convert coordinates to numeric
villages["Latitude"] = pd.to_numeric(villages["Latitude"], errors="coerce")
villages["Longitude"] = pd.to_numeric(villages["Longitude"], errors="coerce")

schools["latitude"] = pd.to_numeric(schools["latitude"], errors="coerce")
schools["longitude"] = pd.to_numeric(schools["longitude"], errors="coerce")

# Remove invalid coordinates
villages = villages.dropna(subset=["Latitude", "Longitude"]).copy()
schools = schools.dropna(subset=["latitude", "longitude"]).copy()

# Remove duplicate school locations
school_locations = schools[
    ["School Name", "VillageName", "latitude", "longitude"]
].drop_duplicates()

# Convert coordinates to radians
village_coords = np.radians(
    villages[["Latitude", "Longitude"]].values
)

school_coords = np.radians(
    school_locations[["latitude", "longitude"]].values
)

# Haversine distance
distance_matrix = pairwise_distances(
    village_coords,
    school_coords,
    metric="haversine"
)

# Convert radians to kilometres
EARTH_RADIUS_KM = 6371.0088
distance_km = distance_matrix * EARTH_RADIUS_KM

# Find nearest school
nearest_index = np.argmin(distance_km, axis=1)

villages["Nearest_School_Distance_km"] = np.min(
    distance_km, axis=1
).round(3)

villages["Nearest_School"] = [
    school_locations.iloc[i]["School Name"]
    for i in nearest_index
]

villages["Nearest_School_Village"] = [
    school_locations.iloc[i]["VillageName"]
    for i in nearest_index
]

# Save result
output_file = "edureach_accessibility_base.csv"
villages.to_csv(output_file, index=False)

print("====================================")
print("EDUREACH ACCESSIBILITY BASE DATA")
print("====================================")
print("Total villages:", len(villages))
print(
    "Villages with local school:",
    (villages["Has_School"] == 1).sum()
)
print(
    "Villages without local school:",
    (villages["Has_School"] == 0).sum()
)
print(
    "Average nearest-school distance:",
    round(villages["Nearest_School_Distance_km"].mean(), 3),
    "km"
)
print(
    "Maximum nearest-school distance:",
    round(villages["Nearest_School_Distance_km"].max(), 3),
    "km"
)
print("Saved:", output_file)
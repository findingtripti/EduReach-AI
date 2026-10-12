import ijson
import json

path = "vb_soi_up.GeoJSON"

with open(path, "rb") as f:
    features = ijson.items(f, "features.item")
    first = next(features)

print("\n--- Feature Keys ---")
print(first.keys())

print("\n--- Properties ---")
print(first["properties"])

print("\n--- Geometry Type ---")
print(first["geometry"]["type"])
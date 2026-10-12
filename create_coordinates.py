import json
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer

input_file = "jamunaha_villages.geojson"
output_file = "jamunaha_villages_coordinates.csv"

print("Loading village boundaries...")

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data["features"]

print("Villages loaded:", len(features))

# Source CRS: Survey of India India NSF LCC
# EPSG:7755
# Convert projected coordinates -> WGS84 latitude/longitude

to_wgs84 = Transformer.from_crs(
    "EPSG:7755",
    "EPSG:4326",
    always_xy=True
)

rows = []
skipped = []

for feature in features:

    properties = feature["properties"]
    village_name = properties.get("village", "")

    try:

        geom = shape(feature["geometry"])

        if geom.is_empty:
            skipped.append(village_name)
            continue

        # Convert geometry from EPSG:7755 to WGS84
        geom_wgs84 = transform(
            to_wgs84.transform,
            geom
        )

        # Representative point inside village boundary
        point = geom_wgs84.representative_point()

        longitude = point.x
        latitude = point.y

        rows.append({
            "village": village_name,
            "vlcode": properties.get("vlcode", ""),
            "district": properties.get("district", ""),
            "block": properties.get("block", ""),
            "population": properties.get(
                "total_population_village", ""
            ),
            "households": properties.get(
                "total_households", ""
            ),
            "latitude": latitude,
            "longitude": longitude
        })

    except Exception as e:

        print(
            "Skipped:",
            village_name,
            "|",
            str(e)
        )

        skipped.append(village_name)


# Create CSV
headers = [
    "village",
    "vlcode",
    "district",
    "block",
    "population",
    "households",
    "latitude",
    "longitude"
]

with open(
    output_file,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    f.write(",".join(headers) + "\n")

    for row in rows:

        values = [
            str(row["village"]).replace(",", " "),
            str(row["vlcode"]),
            str(row["district"]).replace(",", " "),
            str(row["block"]).replace(",", " "),
            str(row["population"]),
            str(row["households"]),
            str(row["latitude"]),
            str(row["longitude"])
        ]

        f.write(",".join(values) + "\n")


print("\n==============================")
print("DONE!")
print("==============================")

print("Total villages:", len(features))
print("Coordinates created:", len(rows))
print("Skipped:", len(skipped))

print("File:", output_file)

if skipped:

    print("\nSkipped villages:")

    for village in skipped:
        print("-", village)

print("\nFirst 5 coordinates:")

for row in rows[:5]:

    print(
        row["village"],
        "| Latitude:",
        row["latitude"],
        "| Longitude:",
        row["longitude"]
    )
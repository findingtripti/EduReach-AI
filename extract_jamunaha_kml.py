import xml.etree.ElementTree as ET
import csv

input_file = "vb_soi_up.kml"
output_file = "jamunaha_villages.csv"

print("Reading KML and extracting Shravasti -> Jamunaha villages...")
print("Please wait...")

results = []

for event, elem in ET.iterparse(input_file, events=("end",)):

    if not elem.tag.endswith("Placemark"):
        continue

    village_name = None
    village_code = None
    district = None
    block = None
    coordinates = None

    # Village name
    for child in elem.iter():
        if child.tag.endswith("name"):
            village_name = (child.text or "").strip()
            break

    # ExtendedData fields
    for child in elem.iter():
        if child.tag.endswith("SimpleData"):
            field_name = child.attrib.get("name", "").strip()
            value = (child.text or "").strip()

            if field_name == "vlcode":
                village_code = value
            elif field_name == "district":
                district = value
            elif field_name == "block":
                block = value

        # Polygon coordinates
        if child.tag.endswith("coordinates"):
            if child.text:
                coordinates = child.text.strip()

    # Exact filtering
    if (
        district
        and district.strip().lower() == "shravasti"
        and block
        and block.strip().lower() == "jamunaha"
        and coordinates
    ):

        # First coordinate = longitude,latitude
        first_coordinate = coordinates.split()[0]
        longitude, latitude = first_coordinate.split(",")[:2]

        results.append({
            "village_name": village_name,
            "village_code": village_code,
            "latitude": latitude,
            "longitude": longitude
        })

    elem.clear()

# Save CSV
with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "village_name",
            "village_code",
            "latitude",
            "longitude"
        ]
    )

    writer.writeheader()
    writer.writerows(results)

print()
print("Extraction complete!")
print("Jamunaha villages found:", len(results))
print("Output file:", output_file)

print()
print("First 10 villages:")

for row in results[:10]:
    print(
        row["village_name"],
        "|",
        row["village_code"],
        "|",
        row["latitude"],
        "|",
        row["longitude"]
    )
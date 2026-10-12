import ijson
import json

input_file = "vb_soi_up.GeoJSON"
output_file = "jamunaha_villages.geojson"

count = 0

with open(input_file, "rb") as infile, open(output_file, "w", encoding="utf-8") as outfile:

    outfile.write('{"type":"FeatureCollection","features":[')

    first_match = True

    for feature in ijson.items(infile, "features.item"):

        properties = feature.get("properties", {})

        district = str(properties.get("district", "")).strip().lower()
        block = str(properties.get("block", "")).strip().lower()

        if district == "shravasti" and block == "jamunaha":

            if not first_match:
                outfile.write(",")

            json.dump(
                feature,
                outfile,
                ensure_ascii=False,
                default=str
            )

            first_match = False
            count += 1

            print(
                count,
                "-",
                properties.get("village"),
                "|",
                properties.get("vlcode")
            )

    outfile.write("]}")

print("\nDONE!")
print("Total Jamunaha villages found:", count)
print("Output file:", output_file)
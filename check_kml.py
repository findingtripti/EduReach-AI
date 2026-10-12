import xml.etree.ElementTree as ET

file = "vb_soi_up.kml"

print("Reading KML...")

count = 0

for event, elem in ET.iterparse(file, events=("end",)):
    if elem.tag.endswith("Placemark"):
        count += 1

        if count <= 3:
            name = None

            for child in elem.iter():
                if child.tag.endswith("name"):
                    name = child.text
                    break

            print(f"Placemark {count}: {name}")

        elem.clear()

print("Total placemarks:", count)
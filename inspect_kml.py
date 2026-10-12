import xml.etree.ElementTree as ET

file = "vb_soi_up.kml"

print("Inspecting first Jamunaha-related placemarks...")

found = 0

for event, elem in ET.iterparse(file, events=("end",)):

    if not elem.tag.endswith("Placemark"):
        continue

    text = ET.tostring(elem, encoding="unicode")

    if "Jamunaha" in text or "JAMUNAHA" in text or "jamunaha" in text:
        print("\n========== PLACEMARK ==========")
        print(text[:8000])
        print("========== END ==========")

        found += 1

        if found == 2:
            break

    elem.clear()

print("\nTotal samples found:", found)
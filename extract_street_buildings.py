import json

def get_building_ids_for_street(geojson_path, street_name):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    selected_ids = []
    for feature in data["features"]:
        addresses = feature.get("adressen", [])
        for adr in addresses:
            street_val = adr.get("str")
            if street_val is None:
                continue  # Skip if no street string
            # Compare street names, ignoring case and leading/trailing spaces
            if street_val.strip().lower() == street_name.strip().lower():
                gebaeude = feature.get("gebaeude", {})
                oi = gebaeude.get("oi")
                if oi:
                    selected_ids.append(oi)
                break  # Move to next feature; no need to check other addresses
    return selected_ids

if __name__ == "__main__":
    geojson_file = "data/geojson/hausumringe_mit_adressenV3.geojson"
    street_name = "Parkstraße"  # <-- Change this!
    building_ids = get_building_ids_for_street(geojson_file, street_name)
    
    print(f"Building IDs for '{street_name}':")
    for bid in building_ids:
        print(bid)
    
    print("\nYAML array for selected_buildings:")
    print("selected_buildings:")
    for bid in building_ids:
        print(f"  - {bid}")

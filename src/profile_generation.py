import json
import os

def generate_electric_load_profiles(buildings, profile_type="H0", config=None):
    """
    Generate electric (and/or thermal) load profiles for each building.
    Args:
        buildings: GeoDataFrame of building info (must include building IDs).
        profile_type: "H0", "G0", "G5", etc. (can be extended)
        config: Optional, if test_mode/subsetting is needed inside this function.
    Returns:
        Dict mapping building IDs to profile arrays/data.
    """
    # --- Optional: Test-mode subsetting if buildings not filtered already ---
    if config and config.get("test_mode", False):
        selected = config.get("selected_buildings", [])
        if selected:
            if "GebaeudeID" in buildings.columns:
                buildings = buildings[buildings['GebaeudeID'].isin(selected)]
            elif "building_id" in buildings.columns:
                buildings = buildings[buildings['building_id'].isin(selected)]
            else:
                raise ValueError("No suitable building ID column found for filtering in test mode.")

    # --- Profile generator logic ---
    profiles = {}
    for idx, row in buildings.iterrows():
        bldg_id = row.get("GebaeudeID", None) or row.get("building_id", None)
        if not bldg_id:
            continue

        # Example: Flat (constant) profile for demonstration
        if profile_type == "H0":
            profile = [1.0 for _ in range(8760)]  # One year of hourly values
        elif profile_type == "G0":
            profile = [0.8 for _ in range(8760)]
        else:
            profile = [0.5 for _ in range(8760)]

        profiles[bldg_id] = profile

    return profiles

def validate_profiles(profiles, profile_type="H0"):
    """
    Dummy validation function—replace with your own!
    """
    valid = True
    for bldg_id, profile in profiles.items():
        if not isinstance(profile, list) or len(profile) != 8760:
            print(f"Profile for {bldg_id} invalid length: {len(profile)}")
            valid = False
    return valid

def export_profiles(profiles, out_file):
    """
    Save the generated profiles as JSON.
    """
    out_dir = os.path.dirname(out_file)
    os.makedirs(out_dir, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

if __name__ == "__main__":
    import argparse
    import geopandas as gpd

    parser = argparse.ArgumentParser(description="Generate electric load profiles for buildings.")
    parser.add_argument("--buildings", required=True, help="Input buildings file (GeoJSON)")
    parser.add_argument("--profile_type", default="H0", help="Profile type (H0, G0, G5, L0, etc.)")
    parser.add_argument("--output", default="results/building_load_profiles.json", help="Output JSON file")
    parser.add_argument("--test_mode", action="store_true", help="Use test mode subsetting")
    parser.add_argument("--selected_buildings", nargs='*', help="IDs of buildings to process (optional)")
    args = parser.parse_args()

    gdf = gpd.read_file(args.buildings)
    if args.test_mode and args.selected_buildings:
        if "GebaeudeID" in gdf.columns:
            gdf = gdf[gdf['GebaeudeID'].isin(args.selected_buildings)]
        elif "building_id" in gdf.columns:
            gdf = gdf[gdf['building_id'].isin(args.selected_buildings)]

    profiles = generate_electric_load_profiles(gdf, args.profile_type)
    valid = validate_profiles(profiles, args.profile_type)
    if not valid:
        print("Warning: Some profiles are invalid!")

    export_profiles(profiles, args.output)
    print(f"Saved profiles for {len(profiles)} buildings to {args.output}")

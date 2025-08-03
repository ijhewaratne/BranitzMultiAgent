# src/building_attributes.py

import argparse
import json
from pathlib import Path

def add_demographics(buildings, household_data):
    """
    Merge demographic/census info into the building dataset.
    Assumes:
        - buildings: GeoDataFrame with 'GebaeudeID' column
        - household_data: dict with GebaeudeID as key
    Returns updated buildings GeoDataFrame with demographic fields merged in.
    """
    import pandas as pd
    print("Building columns:", list(buildings.columns))
    print("Sample demographics keys:", list(household_data.keys())[:10])

    # Merge by GebaeudeID using map
    buildings['demographics'] = buildings['GebaeudeID'].map(household_data)

    # Expand demographics dict into separate columns
    # Only do this if at least one demographics field is not None
    if buildings['demographics'].notnull().any():
        demo_df = pd.json_normalize(buildings['demographics'])
        demo_df.index = buildings.index
        buildings = pd.concat([buildings, demo_df], axis=1)
        buildings.drop(columns=['demographics'], inplace=True)

    return buildings


if __name__ == "__main__":
    import geopandas as gpd
    import pandas as pd

    parser = argparse.ArgumentParser(description="Merge building dataset with demographic/census information.")
    parser.add_argument("--buildings", required=True, help="Path to buildings file (GeoJSON/JSON)")
    parser.add_argument("--demographics", required=True, help="Path to census/household JSON")
    parser.add_argument("--output", default="results/buildings_with_demographics.geojson", help="Output file path")
    args = parser.parse_args()

    # Load buildings (prefer GeoJSON, fallback to JSON)
    ext = Path(args.buildings).suffix.lower()
    try:
        if ext == ".geojson":
            buildings = gpd.read_file(args.buildings)
        elif ext == ".json":
            try:
                buildings = gpd.read_file(args.buildings)
            except Exception:
                with open(args.buildings, "r", encoding="utf-8") as f:
                    buildings = json.load(f)
        else:
            raise ValueError("Unsupported file extension for buildings.")
    except Exception as e:
        print(f"Error reading buildings file: {e}")
        exit(1)

    # Load household/demographic data
    try:
        with open(args.demographics, "r", encoding="utf-8") as f:
            household_data = json.load(f)
    except Exception as e:
        print(f"Error reading demographics file: {e}")
        exit(1)
    
    # Merge
    merged = add_demographics(buildings, household_data)

    # Output: save as GeoJSON if possible, else fallback to JSON
    Path("results").mkdir(exist_ok=True)
    try:
        if hasattr(merged, "to_file"):
            merged.to_file(args.output, driver="GeoJSON")
            print(f"Merged data written to {args.output}")
        else:
            with open(args.output.replace('.geojson', '.json'), "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)
            print(f"Merged data written to {args.output.replace('.geojson', '.json')}")
    except Exception as e:
        print(f"Error writing output: {e}")
        exit(1)

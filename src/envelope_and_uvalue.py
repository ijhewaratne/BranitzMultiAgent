# src/envelope_and_uvalue.py

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

# --- Constants (expand as needed or load from constants.py) ---
U_VALUE_DEFAULTS = {
    'unrenovated': {'wall': 1.3, 'roof': 1.0, 'floor': 1.0, 'window': 2.8},
    'partially_renovated': {'wall': 0.7, 'roof': 0.3, 'floor': 0.4, 'window': 1.8},
    'renovated': {'wall': 0.3, 'roof': 0.2, 'floor': 0.25, 'window': 1.0}
}
RENOVATION_AGE_THRESHOLDS = {
    'renovated': 2010,
    'partially_renovated': 1995
    # Everything older: unrenovated
}

def assign_renovation_state(buildings):
    """
    Assign renovation state based on construction year, explicit field, or heuristic.
    Adds 'renovation_state' column.
    """
    def get_state(row):
        # Check explicit renovation field
        if 'Sanierungszustand' in row and pd.notnull(row['Sanierungszustand']):
            val = str(row['Sanierungszustand']).lower()
            if "voll" in val: return "renovated"
            if "teil" in val: return "partially_renovated"
            if "unrenoviert" in val or "nicht" in val: return "unrenovated"
        # Check construction year if available
        year = None
        for key in ['Baujahr', 'year', 'BaujahrGebaeude', 'construction_year']:
            if key in row and pd.notnull(row[key]):
                try:
                    year = int(row[key])
                except Exception:
                    continue
        if year is not None:
            if year >= RENOVATION_AGE_THRESHOLDS['renovated']:
                return "renovated"
            elif year >= RENOVATION_AGE_THRESHOLDS['partially_renovated']:
                return "partially_renovated"
            else:
                return "unrenovated"
        # Fallback
        return "unrenovated"
    buildings['renovation_state'] = buildings.apply(get_state, axis=1)
    return buildings

def calculate_uvalues(buildings):
    """
    Assign typical U-values for each building based on renovation state.
    Adds u_wall, u_roof, u_floor, u_window columns.
    """
    def get_u(state, typ):
        if pd.isnull(state):
            state = 'unrenovated'
        if state not in U_VALUE_DEFAULTS:
            state = 'unrenovated'
        return U_VALUE_DEFAULTS[state][typ]
    for typ in ['wall', 'roof', 'floor', 'window']:
        buildings[f'u_{typ}'] = buildings['renovation_state'].apply(lambda s: get_u(s, typ))
    return buildings

def compute_building_envelope(buildings):
    """
    Compute envelope geometry: floor area, perimeter, surface areas, and volume.
    Adds: floor_area, wall_area, roof_area, volume
    Requires 'Gebaeudehoehe' or 'height' field for volume.
    """
    from shapely.geometry import Polygon, MultiPolygon
    def safe_area(geom):
        try:
            return geom.area
        except Exception:
            return 0.0
    def safe_length(geom):
        try:
            return geom.length
        except Exception:
            return 0.0
    def get_height(row):
        for key in ['Gebaeudehoehe', 'Gebäudehöhe', 'building_height', 'height']:
            if key in row and pd.notnull(row[key]):
                try:
                    return float(row[key])
                except Exception:
                    continue
        # Fallback: use # of stories * 2.6m
        n_etagen = row.get('Etagenzahl', None)
        try:
            return float(n_etagen) * 2.6 if pd.notnull(n_etagen) else 6.0
        except Exception:
            return 6.0

    buildings['floor_area'] = buildings['geometry'].apply(safe_area)
    buildings['perimeter'] = buildings['geometry'].apply(safe_length)
    buildings['height_m'] = buildings.apply(get_height, axis=1)
    # Wall area = perimeter * height
    buildings['wall_area'] = buildings['perimeter'] * buildings['height_m']
    # Roof area = assume flat = floor area (else can use roof geom if available)
    buildings['roof_area'] = buildings['floor_area']
    # Volume = floor area * height
    buildings['volume'] = buildings['floor_area'] * buildings['height_m']
    return buildings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assign renovation state, calculate U-values, and compute envelope geometry for each building.")
    parser.add_argument("--buildings", required=True, help="Path to buildings GeoJSON/JSON")
    parser.add_argument("--output", default="results/buildings_with_envelope.geojson", help="Output path")
    args = parser.parse_args()

    # Load buildings (prefer GeoJSON)
    ext = Path(args.buildings).suffix.lower()
    try:
        if ext == ".geojson":
            buildings = gpd.read_file(args.buildings)
        elif ext == ".json":
            try:
                buildings = gpd.read_file(args.buildings)
            except Exception:
                with open(args.buildings, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    buildings = gpd.GeoDataFrame(data)
                elif isinstance(data, dict):
                    if "features" in data:
                        buildings = gpd.GeoDataFrame.from_features(data["features"])
                    else:
                        records = [v for v in data.values()]
                        buildings = gpd.GeoDataFrame(records)
                else:
                    raise ValueError("Unrecognized JSON structure.")
        else:
            raise ValueError("Unsupported buildings file extension.")
    except Exception as e:
        print(f"Error loading buildings: {e}")
        exit(1)

    # 1. Assign renovation state
    buildings = assign_renovation_state(buildings)
    # 2. Assign U-values
    buildings = calculate_uvalues(buildings)
    # 3. Compute building envelope
    buildings = compute_building_envelope(buildings)

    # Save results
    Path("results").mkdir(exist_ok=True)
    buildings.to_file(args.output, driver="GeoJSON")
    print(f"Envelope-augmented buildings written to {args.output}")

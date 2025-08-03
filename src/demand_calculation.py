# src/demand_calculation.py

import argparse
import json
from pathlib import Path
import geopandas as gpd
import pandas as pd

# --- Degree day and temp constants (Berlin/Brandenburg) ---
# You can expand these or load from config as needed
T_INDOOR = 20        # [°C] Standard indoor setpoint
T_OUTDOOR_DESIGN = -12  # [°C] Typical for Cottbus (DIN EN 12831)
T_OUTDOOR_ANNUAL = 4.5  # [°C] Mean annual for region
DEGREE_DAYS = 3000      # Heating degree days per year (can refine!)
# Correction/efficiency factors
SYSTEM_EFFICIENCY = 0.85    # Typical for heating system (85% efficient)

def calculate_heating_load(buildings):
    """
    Calculate design (peak) heating load per building using transmission (simplified DIN EN 12831).
    Adds 'heating_load_kw' column (kW).
    Q_dot = U_wall*A_wall + U_roof*A_roof + U_floor*A_floor + U_window*A_window) * dT
    """
    # For this, window area is assumed as a share of wall area if not present (commonly ~15-25%)
    WINDOW_SHARE = 0.2

    def calc_row(row):
        dT = T_INDOOR - T_OUTDOOR_DESIGN
        wall_A = row.get('wall_area', 0)
        roof_A = row.get('roof_area', 0)
        floor_A = row.get('floor_area', 0)
        # Approximate window area if not present
        if 'window_area' in row and pd.notnull(row['window_area']):
            window_A = row['window_area']
        else:
            window_A = wall_A * WINDOW_SHARE

        # Get U-values (should be present from previous step)
        u_wall = row.get('u_wall', 1.3)
        u_roof = row.get('u_roof', 1.0)
        u_floor = row.get('u_floor', 1.0)
        u_window = row.get('u_window', 2.8)

        # Q = (U*A) * dT for each envelope part
        Q = (
            u_wall * (wall_A - window_A) +
            u_roof * roof_A +
            u_floor * floor_A +
            u_window * window_A
        ) * dT  # [W]
        Q = Q / 1000.0  # convert to kW

        # Safety/ventilation/internal gain fudge factor (10% up)
        return max(Q * 1.1, 2.0)  # Minimum 2 kW per building

    buildings['heating_load_kw'] = buildings.apply(calc_row, axis=1)
    return buildings

def calculate_annual_heat_demand(buildings):
    """
    Calculate annual heating demand per building [kWh/a] using degree days.
    Q_annual = (U_wall*A_wall + ...) * HDD * 24 / 1000 * correction
    Adds 'annual_heat_demand_kwh' column.
    """
    WINDOW_SHARE = 0.2

    def calc_annual(row):
        wall_A = row.get('wall_area', 0)
        roof_A = row.get('roof_area', 0)
        floor_A = row.get('floor_area', 0)
        if 'window_area' in row and pd.notnull(row['window_area']):
            window_A = row['window_area']
        else:
            window_A = wall_A * WINDOW_SHARE

        u_wall = row.get('u_wall', 1.3)
        u_roof = row.get('u_roof', 1.0)
        u_floor = row.get('u_floor', 1.0)
        u_window = row.get('u_window', 2.8)

        # Sum UA for all envelope parts
        UA = (
            u_wall * (wall_A - window_A) +
            u_roof * roof_A +
            u_floor * floor_A +
            u_window * window_A
        )  # [W/K]
        # Q_annual = UA * HDD * 24 / 1000 [kWh/a]
        Q_annual = UA * DEGREE_DAYS * 24 / 1000  # [kWh/a]
        # Divide by system efficiency
        Q_annual = Q_annual / SYSTEM_EFFICIENCY
        return max(Q_annual, 5000)  # Minimum annual demand 5 MWh

    buildings['annual_heat_demand_kwh'] = buildings.apply(calc_annual, axis=1)
    return buildings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate design heating load and annual heat demand for each building.")
    parser.add_argument("--buildings", required=True, help="Path to buildings GeoJSON/JSON (with envelope + U-values)")
    parser.add_argument("--output", default="results/buildings_with_demand.geojson", help="Output path")
    args = parser.parse_args()

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

    # Calculate design heating load
    buildings = calculate_heating_load(buildings)
    # Calculate annual heating demand
    buildings = calculate_annual_heat_demand(buildings)

    # Save results
    Path("results").mkdir(exist_ok=True)
    buildings.to_file(args.output, driver="GeoJSON")
    print(f"Demand-augmented buildings written to {args.output}")

# src/scenario_manager.py

import argparse
import json
from pathlib import Path
import geopandas as gpd

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

def generate_scenarios(buildings, network, config):
    """
    Generate scenario input files (JSON) for all batch runs.
    Each scenario is a combination of: supply tech, temp, demand factor, weather, etc.
    - buildings: GeoDataFrame of buildings (attributes + geometry)
    - network: pickled NetworkX graph, or network metadata as dict
    - config: scenario config (dict)
    Outputs scenario files (JSON) in scenarios/
    """
    Path("scenarios").mkdir(exist_ok=True)

    scenarios = config.get('scenarios', [])
    scenario_files = []
    for i, scenario in enumerate(scenarios):
        # Build scenario dict with all required info
        scenario_dict = {
            "name": scenario.get("name", f"scenario_{i+1}"),
            "description": scenario.get("description", ""),
            "type": scenario.get("type", "DH"),
            "params": scenario.get("params", {}),
            "weather": scenario.get("weather", {}),
            "network_file": scenario.get("network_file", None),
            "building_file": scenario.get("building_file", None)
        }

        # Optionally, filter buildings (e.g., by demand threshold, supply zone, etc.)
        if "building_filter" in scenario:
            filter_dict = scenario["building_filter"]
            buildings_filt = buildings.copy()
            for k, v in filter_dict.items():
                buildings_filt = buildings_filt[buildings_filt[k] == v]
        else:
            buildings_filt = buildings

        # Write buildings file for this scenario
        building_file = f"scenarios/buildings_{scenario_dict['name']}.geojson"
        buildings_filt.to_file(building_file, driver="GeoJSON")
        scenario_dict["building_file"] = building_file

        # Network file (can be same for all, or vary per scenario)
        network_file = scenario.get("network_file", "results/branitz_network.graphml")
        scenario_dict["network_file"] = network_file

        # Write scenario JSON
        scenario_file = f"scenarios/{scenario_dict['name']}_scenario.json"
        with open(scenario_file, "w", encoding="utf-8") as f:
            json.dump(scenario_dict, f, indent=2)
        scenario_files.append(scenario_file)
        print(f"Scenario '{scenario_dict['name']}' written to {scenario_file}")

    return scenario_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate scenario input files for simulation runs.")
    parser.add_argument("--buildings", required=True, help="Processed buildings GeoJSON")
    parser.add_argument("--network", required=True, help="Pickled NetworkX or GraphML file")
    parser.add_argument("--config", required=True, help="Scenario config file (YAML or JSON)")
    args = parser.parse_args()

    # Load buildings
    buildings = gpd.read_file(args.buildings)

    # Load scenario config
    ext = Path(args.config).suffix.lower()
    with open(args.config, "r", encoding="utf-8") as f:
        if ext in [".yaml", ".yml"]:
            if not YAML_AVAILABLE:
                raise ImportError("pyyaml is required for YAML configs. Install with `pip install pyyaml`.")
            config = yaml.safe_load(f)
        else:
            config = json.load(f)

    # For network, just save file path in scenario (do not need to parse for scenario setup)
    network = args.network

    scenario_files = generate_scenarios(buildings, network, config)
    print(f"\nAll scenario configs written: {scenario_files}")

# interactive_run.py

import json
import os
import subprocess
import sys
import yaml
import questionary # For creating the interactive user prompt

def get_all_street_names(geojson_path):
    """Scans the entire GeoJSON file and returns a sorted list of unique street names."""
    print(f"Reading all street names from {geojson_path}...")
    street_names = set()
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for feature in data["features"]:
        for adr in feature.get("adressen", []):
            street_val = adr.get("str")
            if street_val:
                street_names.add(street_val.strip())
    
    print(f"Found {len(street_names)} unique streets.")
    return sorted(list(street_names))

def get_building_ids_for_streets(geojson_path, selected_streets):
    """Gets all building IDs for a given list of street names."""
    print(f"Fetching building IDs for selected streets...")
    street_set = {s.lower() for s in selected_streets}
    selected_ids = []
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for feature in data["features"]:
        for adr in feature.get("adressen", []):
            street_val = adr.get("str")
            if street_val and street_val.strip().lower() in street_set:
                oi = feature.get("gebaeude", {}).get("oi")
                if oi:
                    selected_ids.append(oi)
                break # Found a matching street, move to the next building feature
    
    print(f"Found {len(selected_ids)} buildings.")
    return selected_ids

def main():
    """Main function to run the interactive pipeline."""
    
    # --- Configuration ---
    # Path to the main data file containing all buildings and addresses
    full_data_geojson = "data/geojson/hausumringe_mit_adressenV3.geojson"
    # Path to your template YAML configuration file
    base_config_path = "run_all_test.yaml"
    # Name for the new, dynamically generated config file
    dynamic_config_path = "config_interactive_run.yaml"

    # --- 1. User Street Selection ---
    try:
        all_streets = get_all_street_names(full_data_geojson)
        if not all_streets:
            print("Error: No street names found in the GeoJSON file.")
            return

        selected_streets = questionary.checkbox(
            "Select the streets you want to process (use space to select, enter to confirm):",
            choices=all_streets
        ).ask()

        if not selected_streets:
            print("No streets selected. Exiting.")
            return

    except FileNotFoundError:
        print(f"Error: The main data file was not found at '{full_data_geojson}'")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # --- 2. Generate Dynamic Configuration ---
    building_ids = get_building_ids_for_streets(full_data_geojson, selected_streets)
    if not building_ids:
        print("No buildings found for the selected streets. Exiting.")
        return

    print("\nCreating dynamic configuration file...")
    with open(base_config_path, "r") as f:
        config_data = yaml.safe_load(f)

    # Update the configuration with the selected buildings
    config_data["selected_buildings"] = building_ids

    # Save the new configuration to a temporary file
    with open(dynamic_config_path, "w") as f:
        yaml.dump(config_data, f, sort_keys=False)
    print(f"Dynamic configuration saved to '{dynamic_config_path}'")

    # --- 3. Run the Main Pipeline ---
    print("\n" + "="*50)
    print("STARTING MAIN PIPELINE (`main.py`)")
    print("="*50)
    try:
        # We use subprocess to call main.py, just like you would from the terminal
        subprocess.run([sys.executable, "main.py", "--config", dynamic_config_path], check=True)
        print("\nMain pipeline completed successfully.")
    except subprocess.CalledProcessError:
        print("\nError: The main pipeline failed. Please check the output above.")
        return
    except FileNotFoundError:
        print("Error: `main.py` not found. Make sure it's in the same directory.")
        return

    # --- 4. Run the Visualization ---
    print("\n" + "="*50)
    print("STARTING VISUALIZATION (`graph2.py`)")
    print("="*50)
    try:
        # Now, we call graph2.py to visualize the results
        subprocess.run([sys.executable, "graph2.py"], check=True)
        print("\nVisualization script completed.")
    except subprocess.CalledProcessError:
        print("\nError: The visualization script failed.")
    except FileNotFoundError:
        print("Error: `graph2.py` not found. Make sure it's in the same directory.")
        return

    print("\nInteractive run finished successfully!")


if __name__ == "__main__":
    main()
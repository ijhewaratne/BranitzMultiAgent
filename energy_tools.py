# energy_tools.py
import json
import os
import subprocess
import sys
import yaml
from adk.api.tool import tool
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
from shapely.geometry import LineString
import networkx as nx
from scipy.spatial import distance_matrix
import pandas as pd
import glob
#import adk.api.tool as tool

# This file contains the functions that our agents can use as tools.

@tool
def get_all_street_names() -> list[str]:
    """
    Returns a list of all available street names in the dataset.
    This tool helps users see what streets are available for analysis.
    """
    full_data_geojson = "data/geojson/hausumringe_mit_adressenV3.geojson"
    print(f"TOOL: Reading all street names from {full_data_geojson}...")
    
    try:
        with open(full_data_geojson, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ["Error: The main data file was not found at the specified path."]

    street_names = set()
    for feature in data["features"]:
        for adr in feature.get("adressen", []):
            street_val = adr.get("str")
            if street_val:
                street_names.add(street_val.strip())
    
    sorted_streets = sorted(list(street_names))
    print(f"TOOL: Found {len(sorted_streets)} unique streets.")
    return sorted_streets

@tool
def get_building_ids_for_street(street_name: str) -> list[str]:
    """
    Finds and returns a list of building IDs located on a specific street.
    This tool is used by the agent to know which buildings to include in the simulation.
    
    Args:
        street_name: The name of the street to search for.
    """
    full_data_geojson = "data/geojson/hausumringe_mit_adressenV3.geojson"
    print(f"TOOL: Searching for buildings on '{street_name}' in {full_data_geojson}...")
    
    try:
        with open(full_data_geojson, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ["Error: The main data file was not found at the specified path."]

    street_set = {street_name.strip().lower()}
    selected_ids = []
    for feature in data["features"]:
        for adr in feature.get("adressen", []):
            street_val = adr.get("str")
            if street_val and street_val.strip().lower() in street_set:
                oi = feature.get("gebaeude", {}).get("oi")
                if oi:
                    selected_ids.append(oi)
                break 
    
    print(f"TOOL: Found {len(selected_ids)} buildings.")
    return selected_ids

@tool
def create_network_graph(building_ids: list[str], output_dir: str = "results_test") -> str:
    """
    Creates a network graph from building IDs and exports it to JSON format.
    This tool creates building-to-building connections and building-to-street connections.
    
    Args:
        building_ids: A list of building IDs to include in the network graph.
        output_dir: Directory to save the output files (default: results_test).
        
    Returns:
        A success message with the path to the generated JSON file.
    """
    print(f"TOOL: Creating network graph for {len(building_ids)} buildings...")
    
    try:
        # Load the building footprints
        buildings_gdf = gpd.read_file(f"{output_dir}/buildings_prepared.geojson")
        
        # Filter buildings to only include the specified building IDs
        filtered_buildings = buildings_gdf[buildings_gdf['GebaeudeID'].isin(building_ids)]
        
        if filtered_buildings.empty:
            # If no buildings found, use all available buildings and inform the user
            print(f"TOOL: No buildings found with the specified IDs. Using all available buildings instead.")
            filtered_buildings = buildings_gdf
            actual_building_ids = buildings_gdf['GebaeudeID'].tolist()
        else:
            actual_building_ids = building_ids
        
        print(f"TOOL: Found {len(filtered_buildings)} buildings in the prepared data.")
        
        # Load street data
        street_filepath = f"{output_dir}/streets.geojson"
        try:
            street_gdf = gpd.read_file(street_filepath)
        except Exception as e:
            return f"Error loading street file: {e}"
        
        # Project both layers to the same projected CRS for accuracy
        utm_crs = filtered_buildings.estimate_utm_crs()
        buildings_proj = filtered_buildings.to_crs(utm_crs)
        street_proj = street_gdf.to_crs(utm_crs)
        
        # Combine all street segments into one continuous line for calculations
        street_line = street_proj.geometry.union_all()
        
        # Calculate the service line connections
        connection_lines = []
        building_street_connections = []
        
        for _, building in buildings_proj.iterrows():
            building_polygon = building.geometry
            building_id = building.get('GebaeudeID', building.get('oi', f'building_{_}'))
            
            # Find the two nearest points between the building edge and the street line
            p_building, p_street = nearest_points(building_polygon, street_line)
            
            # Create a line connecting these two points
            connection_line = LineString([p_building, p_street])
            connection_lines.append(connection_line)
            
            # Store connection info for JSON export
            building_street_connections.append({
                'building_id': building_id,
                'building_coords': [p_building.x, p_building.y],
                'street_coords': [p_street.x, p_street.y],
                'connection_length': connection_line.length
            })
        
        # Create building-to-building network using minimum spanning tree
        building_centroids = buildings_proj.geometry.centroid
        building_ids_list = buildings_proj.get('GebaeudeID', buildings_proj.get('oi', [f'building_{i}' for i in range(len(buildings_proj))]))
        
        # Create position dictionary
        pos = {building_id: (centroid.x, centroid.y) for building_id, centroid in zip(building_ids_list, building_centroids)}
        
        # Create complete graph
        coordinates = list(pos.values())
        complete_graph = nx.Graph()
        dist_matrix = distance_matrix(coordinates, coordinates)
        
        for i in range(len(building_ids_list)):
            for j in range(i + 1, len(building_ids_list)):
                id1 = building_ids_list[i]
                id2 = building_ids_list[j]
                dist = dist_matrix[i, j]
                complete_graph.add_edge(id1, id2, weight=dist)
        
        # Create minimum spanning tree
        mst_graph = nx.minimum_spanning_tree(complete_graph)
        
        # Prepare graph data for JSON export
        graph_data = {
            'metadata': {
                'total_buildings': len(buildings_proj),
                'total_connections': len(connection_lines),
                'graph_nodes': mst_graph.number_of_nodes(),
                'graph_edges': mst_graph.number_of_edges(),
                'crs': str(utm_crs),
                'requested_building_ids': building_ids,
                'actual_building_ids': actual_building_ids
            },
            'buildings': [],
            'building_connections': building_street_connections,
            'graph_nodes': [],
            'graph_edges': []
        }
        
        # Add building data
        for _, building in buildings_proj.iterrows():
            building_id = building.get('GebaeudeID', building.get('oi', f'building_{_}'))
            centroid = building.geometry.centroid
            building_data = {
                'id': building_id,
                'coordinates': [centroid.x, centroid.y],
                'properties': {
                    'area': building.geometry.area,
                    'perimeter': building.geometry.length
                }
            }
            graph_data['buildings'].append(building_data)
        
        # Add graph nodes
        for node in mst_graph.nodes():
            x, y = pos[node]
            graph_data['graph_nodes'].append({
                'id': node,
                'coordinates': [x, y]
            })
        
        # Add graph edges
        for edge in mst_graph.edges(data=True):
            graph_data['graph_edges'].append({
                'source': edge[0],
                'target': edge[1],
                'weight': edge[2]['weight']
            })
        
        # Export to JSON
        json_output_path = f"{output_dir}/network_graph_{len(building_ids)}_buildings.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        # Also export GeoJSON files for visualization
        connections_gdf = gpd.GeoDataFrame(geometry=connection_lines, crs=utm_crs)
        connections_gdf.to_file(f"{output_dir}/service_connections_{len(building_ids)}_buildings.geojson", driver="GeoJSON")
        buildings_proj.to_file(f"{output_dir}/buildings_projected_{len(building_ids)}_buildings.geojson", driver="GeoJSON")
        
        print(f"TOOL: Successfully created network graph with {mst_graph.number_of_nodes()} nodes and {mst_graph.number_of_edges()} edges.")
        
        if len(filtered_buildings) != len(building_ids):
            return f"Network graph created successfully! Note: Used {len(filtered_buildings)} available buildings instead of {len(building_ids)} requested buildings.\nFiles generated:\n- JSON Graph: {json_output_path}\n- Service Connections: {output_dir}/service_connections_{len(building_ids)}_buildings.geojson\n- Buildings: {output_dir}/buildings_projected_{len(building_ids)}_buildings.geojson"
        else:
            return f"Network graph created successfully! Files generated:\n- JSON Graph: {json_output_path}\n- Service Connections: {output_dir}/service_connections_{len(building_ids)}_buildings.geojson\n- Buildings: {output_dir}/buildings_projected_{len(building_ids)}_buildings.geojson"
        
    except Exception as e:
        return f"Error creating network graph: {str(e)}"

@tool
def create_network_visualization(output_dir: str = "results_test") -> str:
    """
    Creates a high-quality network visualization showing buildings, streets, and service connections.
    Saves the plot as both PNG and PDF formats.
    
    Args:
        output_dir: Directory containing the data files and where to save the visualization.
        
    Returns:
        A success message with the paths to the generated visualization files.
    """
    print(f"TOOL: Creating network visualization from {output_dir}...")
    
    try:
        # Load the building footprints
        buildings_file = os.path.join(output_dir, "buildings_prepared.geojson")
        if not os.path.exists(buildings_file):
            return f"Error: Buildings file not found at '{buildings_file}'"
        
        buildings_gdf = gpd.read_file(buildings_file)
        
        # Load the street map file
        street_filepath = os.path.join(output_dir, "streets.geojson")
        try:
            street_gdf = gpd.read_file(street_filepath)
        except Exception as e:
            return f"Error loading street file: {e}"

        if buildings_gdf.empty:
            return "Error: Buildings file is empty."

        # Project both layers to the same projected CRS for accuracy
        print(f"TOOL: Projecting layers to a suitable local CRS...")
        utm_crs = buildings_gdf.estimate_utm_crs()
        buildings_proj = buildings_gdf.to_crs(utm_crs)
        street_proj = street_gdf.to_crs(utm_crs)
        print(f"TOOL: Layers projected to: {utm_crs}")

        # Combine all street segments into one continuous line for calculations
        street_line = street_proj.geometry.union_all()
        
        # Calculate the service line connections
        connection_lines = []
        for _, building in buildings_proj.iterrows():
            building_polygon = building.geometry
            
            # Find the two nearest points between the building edge and the street line
            p_building, p_street = nearest_points(building_polygon, street_line)
            
            # Create a line connecting these two points
            connection_lines.append(LineString([p_building, p_street]))

        # Create a new GeoDataFrame for the connection lines
        connections_gdf = gpd.GeoDataFrame(geometry=connection_lines, crs=utm_crs)
        print(f"TOOL: Successfully calculated {len(connections_gdf)} service connections.")

        # Create the visualization
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Plot layers from bottom to top
        street_proj.plot(ax=ax, color="black", linewidth=3, label="Main Street")
        buildings_proj.plot(ax=ax, color="lightgrey", edgecolor="black")
        connections_gdf.plot(ax=ax, color="red", linewidth=1.5, label="Service Connections")

        ax.set_title("Network Connections from Buildings to Street")
        ax.set_axis_off()
        ax.set_aspect('equal', adjustable='box')
        plt.legend()
        plt.tight_layout()
        
        # Save the plot
        plot_filename = os.path.join(output_dir, "network_visualization.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        # Also save as PDF for vector format
        pdf_filename = os.path.join(output_dir, "network_visualization.pdf")
        plt.savefig(pdf_filename, bbox_inches='tight')
        
        plt.show()
        
        return f"Network visualization created successfully!\nFiles saved:\n- PNG: {plot_filename}\n- PDF: {pdf_filename}"
        
    except Exception as e:
        return f"Error creating visualization: {str(e)}"

@tool
def run_simulation_pipeline(building_ids: list[str], scenario_type: str) -> str:
    """
    Runs the entire energy simulation pipeline for a given list of buildings and a scenario type.
    
    Args:
        building_ids: A list of building IDs to be included in the simulation.
        scenario_type: The type of scenario to run. Must be either 'DH' for District Heating (centralized) or 'HP' for Heat Pumps (decentralized).
        
    Returns:
        A success or failure message, including the path to the final KPI report.
    """
    print(f"TOOL: Starting pipeline for {len(building_ids)} buildings. Scenario type: {scenario_type}")
    base_config_path = "run_all_test.yaml"
    dynamic_config_path = f"config_{scenario_type}_run.yaml"

    try:
        with open(base_config_path, "r") as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError:
        return f"Error: Base config file not found at '{base_config_path}'."

    # Update the configuration with the selected buildings
    config_data["selected_buildings"] = building_ids

    # IMPORTANT: Modify the scenario config based on the agent's specialty
    # This assumes you have a `branitz_scenarios.yaml` file that defines different scenarios.
    # We will tell the scenario manager which type to use.
    # A simple approach is to have different scenario config files.
    if scenario_type == "DH":
        config_data["scenario_config_file"] = "scenarios_dh.yaml" # A file configured for District Heating
    elif scenario_type == "HP":
        config_data["scenario_config_file"] = "scenarios_hp.yaml" # A file configured for Heat Pumps
    else:
        return "Error: Invalid scenario_type. Must be 'DH' or 'HP'."

    # Save the new dynamic configuration
    with open(dynamic_config_path, "w") as f:
        yaml.dump(config_data, f, sort_keys=False)
    print(f"TOOL: Dynamic configuration saved to '{dynamic_config_path}'")

    # Execute the main pipeline
    try:
        subprocess.run([sys.executable, "main.py", "--config", dynamic_config_path], check=True)
        kpi_path = os.path.join(config_data.get("output_dir", "results_test/"), "scenario_kpis.csv")
        return f"Pipeline completed successfully. KPI report is available at: {kpi_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: The main pipeline failed to execute. Return code: {e.returncode}"
    except FileNotFoundError:
        return "Error: `main.py` could not be found."

@tool
def run_complete_analysis(street_name: str, scenario_type: str) -> str:
    """
    Runs a complete analysis for a specific street and scenario type.
    This tool combines building extraction, network creation, simulation, and visualization.
    
    Args:
        street_name: The name of the street to analyze.
        scenario_type: The type of scenario to run ('DH' or 'HP').
        
    Returns:
        A comprehensive summary of the analysis results.
    """
    print(f"TOOL: Running complete analysis for '{street_name}' with {scenario_type} scenario...")
    
    try:
        # Step 1: Get building IDs
        building_ids = get_building_ids_for_street.func(street_name)
        if not building_ids or len(building_ids) == 0:
            return f"No buildings found for street '{street_name}'"
        
        # Step 2: Create network graph
        network_result = create_network_graph.func(building_ids, "results_test")
        
        # Step 3: Run simulation pipeline
        simulation_result = run_simulation_pipeline.func(building_ids, scenario_type)
        
        # Step 4: Create visualization
        viz_result = create_network_visualization.func("results_test")
        
        # Step 5: Analyze results
        kpi_path = "results_test/scenario_kpis.csv"
        if os.path.exists(kpi_path):
            analysis_result = analyze_kpi_report.func(kpi_path)
        else:
            analysis_result = "KPI analysis not available"
        
        # Compile comprehensive summary
        summary = f"""
=== COMPLETE ANALYSIS SUMMARY ===
Street: {street_name}
Scenario Type: {scenario_type}
Buildings Found: {len(building_ids)}

1. NETWORK CREATION:
{network_result}

2. SIMULATION PIPELINE:
{simulation_result}

3. VISUALIZATION:
{viz_result}

4. ANALYSIS:
{analysis_result}

=== ANALYSIS COMPLETE ===
"""
        return summary
        
    except Exception as e:
        return f"Error during complete analysis: {str(e)}"

@tool
def analyze_kpi_report(kpi_report_path: str) -> str:
    """
    Analyzes a Key Performance Indicator (KPI) report file and generates a natural language summary.
    
    Args:
        kpi_report_path: The file path to the KPI summary CSV file.
        
    Returns:
        A detailed, human-readable analysis of the simulation results.
    """
    print(f"TOOL: Analyzing KPI report at '{kpi_report_path}'...")
    try:
        # We reuse your existing llm_reporter logic by calling it via subprocess
        # This assumes your `run_all_test.yaml` contains the correct API key and model info.
        # NOTE: A more robust way would be to import `create_llm_report` directly.
        
        # We need to find the scenario and output file from a config.
        # For simplicity, we'll hardcode them here, but this could be improved.
        scenarios_file = "scenarios_dh.yaml" # Or dynamically determine this
        output_report_file = "results_test/llm_final_report.md"

        # Read the main config to get API key and model
        with open("run_all_test.yaml", "r") as f:
            main_config = yaml.safe_load(f)

        subprocess.run([
            sys.executable, "src/llm_reporter.py",
            "--kpis", kpi_report_path,
            "--scenarios", scenarios_file,
            "--output", output_report_file,
            "--model", main_config.get("llm_model", "gpt-4o"),
            "--api_key", main_config.get("openai_api_key", "")
        ], check=True)

        with open(output_report_file, "r", encoding="utf-8") as f:
            report_content = f.read()
            
        return f"KPI analysis complete. Here is the summary:\n\n{report_content}"
    except Exception as e:
        return f"Error: Failed to analyze KPI report. {str(e)}"

@tool
def list_available_results() -> str:
    """
    Lists all available result files and their locations.
    This tool helps users understand what data has been generated.
    
    Returns:
        A formatted list of all available result files.
    """
    print("TOOL: Scanning for available result files...")
    
    result_dirs = ["results_test", "results"]
    available_files = {}
    
    for result_dir in result_dirs:
        if os.path.exists(result_dir):
            files = {
                "Network Files": glob.glob(f"{result_dir}/network_graph_*.json"),
                "Service Connections": glob.glob(f"{result_dir}/service_connections_*.geojson"),
                "KPI Reports": glob.glob(f"{result_dir}/scenario_kpis.*"),
                "LLM Reports": glob.glob(f"{result_dir}/llm_*.md"),
                "Visualizations": glob.glob(f"{result_dir}/network_visualization.*"),
                "Building Data": glob.glob(f"{result_dir}/buildings_*.geojson"),
                "Street Data": glob.glob(f"{result_dir}/streets.*")
            }
            available_files[result_dir] = files
    
    # Format the output
    output = "=== AVAILABLE RESULT FILES ===\n\n"
    
    for result_dir, file_categories in available_files.items():
        output += f"📁 {result_dir.upper()}:\n"
        for category, files in file_categories.items():
            if files:
                output += f"  📂 {category}:\n"
                for file in files:
                    file_size = os.path.getsize(file) if os.path.exists(file) else 0
                    size_str = f"({file_size:,} bytes)" if file_size > 0 else "(empty)"
                    output += f"    • {os.path.basename(file)} {size_str}\n"
        output += "\n"
    
    if not any(available_files.values()):
        output += "No result files found. Run an analysis first.\n"
    
    return output

@tool
def compare_scenarios(street_name: str) -> str:
    """
    Compares both DH and HP scenarios for a given street.
    This tool runs both scenarios and provides a side-by-side comparison.
    
    Args:
        street_name: The name of the street to analyze.
        
    Returns:
        A comprehensive comparison of both scenarios.
    """
    print(f"TOOL: Comparing DH and HP scenarios for '{street_name}'...")
    
    try:
        # Get building IDs
        building_ids = get_building_ids_for_street.func(street_name)
        if not building_ids:
            return f"No buildings found for street '{street_name}'"
        
        # Run both scenarios
        dh_result = run_simulation_pipeline.func(building_ids, "DH")
        hp_result = run_simulation_pipeline.func(building_ids, "HP")
        
        # Analyze both KPI reports
        dh_kpi = "results_test/scenario_kpis.csv"
        hp_kpi = "results_test/scenario_kpis.csv"  # Same file gets overwritten
        
        if os.path.exists(dh_kpi):
            # Read the KPI data for comparison
            df = pd.read_csv(dh_kpi)
            
            comparison = f"""
=== SCENARIO COMPARISON FOR {street_name.upper()} ===
Buildings Analyzed: {len(building_ids)}

DISTRICT HEATING (DH) SCENARIO:
{dh_result}

HEAT PUMP (HP) SCENARIO:
{hp_result}

KPI COMPARISON:
{df.to_string(index=False)}

RECOMMENDATION:
"""
            
            # Add simple recommendation based on KPIs
            try:
                # Check what scenarios are available
                available_scenarios = df['scenario'].tolist()
                print(f"TOOL: Available scenarios in KPI file: {available_scenarios}")
                
                # Look for DH and HP scenarios
                dh_scenarios = [s for s in available_scenarios if 'dh' in s.lower()]
                hp_scenarios = [s for s in available_scenarios if 'hp' in s.lower()]
                
                if dh_scenarios and hp_scenarios:
                    # Get first DH and first HP scenario
                    dh_data = df[df['scenario'] == dh_scenarios[0]].iloc[0]
                    hp_data = df[df['scenario'] == hp_scenarios[0]].iloc[0]
                    
                    dh_cost = dh_data['lcoh_eur_per_mwh']
                    hp_cost = hp_data['lcoh_eur_per_mwh']
                    dh_emissions = dh_data['co2_t_per_a']
                    hp_emissions = hp_data['co2_t_per_a']
                    
                    cost_savings = ((dh_cost - hp_cost) / dh_cost) * 100
                    emission_diff = dh_emissions - hp_emissions
                    
                    comparison += f"""
• Cost: Heat Pumps are {cost_savings:.1f}% cheaper (€{hp_cost:.2f} vs €{dh_cost:.2f}/MWh)
• Emissions: District Heating produces {emission_diff:.2f} fewer tons CO₂/year
• Recommendation: {'Heat Pumps' if cost_savings > 20 else 'District Heating'} based on {'cost' if cost_savings > 20 else 'emissions'} priority
"""
                else:
                    comparison += f"""
• Available scenarios: {', '.join(available_scenarios)}
• Recommendation: Both scenarios completed successfully. Check individual results for detailed analysis.
"""
                    
            except Exception as e:
                comparison += f"""
• Error in detailed comparison: {str(e)}
• Both scenarios completed successfully. Check individual results for detailed analysis.
"""
            
            return comparison
        else:
            return f"Analysis completed but KPI comparison not available.\n\nDH Result: {dh_result}\n\nHP Result: {hp_result}"
            
    except Exception as e:
        return f"Error during scenario comparison: {str(e)}"

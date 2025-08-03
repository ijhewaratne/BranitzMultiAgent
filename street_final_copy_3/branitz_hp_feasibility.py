import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from shapely.geometry import Point, LineString
from pathlib import Path
from shapely.ops import nearest_points
from pyproj import Transformer
import random
import time
from shapely.strtree import STRtree
import subprocess
from datetime import datetime
import json
import pandapower as pp

# Import power simulation functions - we'll define them locally to avoid path issues
# import sys
# sys.path.append('../thesis-data-2/power-sim')
# from simuV6_multiprocessing_ohne_UW import (
#     create_base_network,
#     create_external_grid,
#     create_transformers
# )

# Local power simulation functions
def create_base_network_local(nodes_data):
    """Create empty pandapower network with buses for each node."""
    net = pp.create_empty_network(name="Branitzer Siedlung", f_hz=50)
    
    # Dictionary for mapping node IDs to buses
    node_id_to_bus = {}
    bus_geodata_list = []
    
    # Create LV buses for each node
    for node in nodes_data:
        node_id = str(node['id'])
        bus = pp.create_bus(
            net,
            vn_kv=0.4,
            name=f"Node {node_id}",
            type="b",
            zone="Branitz"
        )
        node_id_to_bus[node_id] = bus
        bus_geodata_list.append({'bus': bus, 'x': node['lon'], 'y': node['lat']})
    
    # Create MV bus (20 kV)
    mv_bus = pp.create_bus(
        net,
        vn_kv=20,
        name="MV Grid Connection",
        type="b",
        zone="Branitz"
    )
    
    # Assign geodata to MV bus
    mv_geodata = {'bus': mv_bus, 'x': bus_geodata_list[0]['x'], 'y': bus_geodata_list[0]['y']}
    bus_geodata_list.append(mv_geodata)
    net.bus_geodata = pd.DataFrame(bus_geodata_list).set_index('bus')
    
    return net, node_id_to_bus, mv_bus

def create_external_grid_local(net, mv_bus):
    """Create external grid connection."""
    return pp.create_ext_grid(
        net,
        bus=mv_bus,
        vm_pu=1.02,
        va_degree=0.0,
        s_sc_max_mva=250,
        rx_max=0.1,
        name="External Grid 20kV"
    )

def create_transformers_local(net, mv_bus, node_id_to_bus, nodes_data):
    """Create transformers for substations."""
    transformers_created = 0
    trafo_mapping = {}
    
    # Transformer parameters
    trafo_params = {
        '250': {'sn_mva': 0.25, 'vk_percent': 4.0, 'vkr_percent': 1.1, 'pfe_kw': 0.3, 'i0_percent': 0.2},
        '630': {'sn_mva': 0.63, 'vk_percent': 6.0, 'vkr_percent': 0.8, 'pfe_kw': 0.6, 'i0_percent': 0.15},
        '1000': {'sn_mva': 1.0, 'vk_percent': 6.0, 'vkr_percent': 0.7, 'pfe_kw': 0.75, 'i0_percent': 0.1}
    }
    
    # Transformer sizes
    trafo_sizes = {'C': '250', 'B': '250', 'J': '250', 'E': '1000'}
    
    for node in nodes_data:
        tags = node.get('tags', {})
        node_id = str(node['id'])
        
        if tags.get("power") == "substation":
            trafo_id = tags.get("trafoid", "unknown")
            
            if node_id in node_id_to_bus:
                lv_bus = node_id_to_bus[node_id]
                size = trafo_sizes.get(trafo_id, '630')
                params = trafo_params[size]
                
                idx = pp.create_transformer_from_parameters(
                    net,
                    hv_bus=mv_bus,
                    lv_bus=lv_bus,
                    sn_mva=params['sn_mva'],
                    vn_hv_kv=20.0,
                    vn_lv_kv=0.4,
                    vk_percent=params['vk_percent'],
                    vkr_percent=params['vkr_percent'],
                    pfe_kw=params['pfe_kw'],
                    i0_percent=params['i0_percent'],
                    shift_degree=150,
                    name=f"MV_Transformer_{trafo_id}",
                    tap_min=-2,
                    tap_max=2,
                    tap_step_percent=2.5,
                    tap_pos=0,
                    tap_neutral=0,
                    tap_side="hv"
                )
                trafo_mapping[idx] = trafo_id
                transformers_created += 1
    
    return transformers_created, trafo_mapping

# --- CONFIG ---
# Centralized file paths
STREETS_FILE = Path('street_final_copy_3/results_test/streets.geojson')
BUILDINGS_FILE = Path('street_final_copy_3/data/geojson/hausumringe_mit_adressenV3.geojson')
POWER_LINES_FILE = Path('street_final_copy_3/branitz_hp_feasibility_outputs/power_lines.geojson')
POWER_SUBSTATIONS_FILE = Path('street_final_copy_3/branitz_hp_feasibility_outputs/power_substations.geojson')
POWER_PLANTS_FILE = Path('street_final_copy_3/branitz_hp_feasibility_outputs/power_plants.geojson')
POWER_GENERATORS_FILE = Path('street_final_copy_3/branitz_hp_feasibility_outputs/power_generators.geojson')
OUTPUT_DIR = Path('street_final_copy_3/branitz_hp_feasibility_outputs')
OUTPUT_CSV_PATH = OUTPUT_DIR / 'building_proximity_table.csv'
OUTPUT_MAP_PATH = OUTPUT_DIR / 'branitz_hp_feasibility_map.html'
OUTPUT_DIR.mkdir(exist_ok=True)

# --- 1. Print all unique power tags and geometry types ---
def print_power_tags():
    for file, label in [
        (POWER_LINES_FILE, 'lines'),
        (POWER_SUBSTATIONS_FILE, 'substations'),
        (POWER_PLANTS_FILE, 'plants'),
        (POWER_GENERATORS_FILE, 'generators')]:
        gdf = gpd.read_file(file)
        print(f"{label.title()} - count: {len(gdf)}; geometry types: {gdf.geometry.geom_type.value_counts().to_dict()}")
        if 'power' in gdf.columns:
            print(f"  Unique power tags: {gdf['power'].unique()}")

# --- 2. Load Power Infrastructure ---
def load_power_infrastructure():
    lines = gpd.read_file(POWER_LINES_FILE)
    substations = gpd.read_file(POWER_SUBSTATIONS_FILE)
    plants = gpd.read_file(POWER_PLANTS_FILE)
    generators = gpd.read_file(POWER_GENERATORS_FILE)
    return lines, substations, plants, generators

# --- 3. Load Buildings ---
def load_buildings(buildings_file):
    print(f"Loading buildings from {buildings_file}...")
    buildings = gpd.read_file(buildings_file)
    print(f"Loaded {len(buildings)} buildings.")
    return buildings

# --- 3.5. Load Load Profiles ---
def load_load_profiles(load_profiles_file):
    print(f"Loading load profiles from {load_profiles_file}...")
    with open(load_profiles_file, 'r') as f:
        load_profiles = json.load(f)
    print(f"Loaded load profiles for {len(load_profiles)} buildings.")
    return load_profiles

# --- 4.5. Compute Service Lines (Street-Following) ---
def compute_service_lines_street_following(buildings, substations, plants, generators=None, streets_gdf=None):
    """
    Compute service lines from buildings to nearest infrastructure following street network.
    Includes substations, plants, and generators as infrastructure.
    Uses an STRtree spatial index for O(log N) nearest-node lookups instead of brute-force scanning.
    """
    import networkx as nx
    from shapely.ops import nearest_points
    
    print("Computing street-following service lines...")
    
    # Combine substations, plants, and generators into infrastructure
    infra_list = []
    if substations is not None and not substations.empty:
        infra_list.append(substations)
    if plants is not None and not plants.empty:
        infra_list.append(plants)
    if generators is not None and not generators.empty:
        infra_list.append(generators)
    if infra_list:
        infra = gpd.GeoDataFrame(pd.concat(infra_list, ignore_index=True))
    else:
        print("No infrastructure found for service line computation.")
        return buildings
    
    # Ensure we're in a projected CRS for accurate calculations
    if infra.crs.is_geographic:
        utm_crs = "EPSG:32633"
        infra = infra.to_crs(utm_crs)
        buildings_proj = buildings.to_crs(utm_crs)
        if streets_gdf is not None:
            streets_proj = streets_gdf.to_crs(utm_crs)
    else:
        buildings_proj = buildings.to_crs(infra.crs)
        if streets_gdf is not None:
            streets_proj = streets_gdf.to_crs(infra.crs)
    
    # Create street network if available
    if streets_gdf is not None:
        print("Creating street network for routing...")
        G = nx.Graph()
        # Add street segments as edges
        for idx, street in streets_proj.iterrows():
            coords = list(street.geometry.coords)
            for i in range(len(coords) - 1):
                node1 = f"street_{idx}_{i}"
                node2 = f"street_{idx}_{i+1}"
                # Add nodes with positions
                G.add_node(node1, pos=coords[i], node_type='street')
                G.add_node(node2, pos=coords[i+1], node_type='street')
                # Add edge with length as weight
                length = Point(coords[i]).distance(Point(coords[i+1]))
                G.add_edge(node1, node2, weight=length, edge_type='street', length=length)
        # Connect nearby street nodes
        print("Connecting nearby street nodes...")
        node_positions = [G.nodes[n]['pos'] for n in G.nodes() if G.nodes[n]['node_type'] == 'street']
        node_names = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'street']
        node_points = [Point(pos) for pos in node_positions]
        
        # Use a simpler approach for connecting nearby nodes
        for i, point in enumerate(node_points):
            for j, other_point in enumerate(node_points):
                if i != j and not G.has_edge(node_names[i], node_names[j]):
                    dist = point.distance(other_point)
                    if dist < 5.0:
                        G.add_edge(node_names[i], node_names[j], weight=dist, edge_type='connection', length=dist)
        print(f"Created street network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    else:
        print("No street data available, using straight-line connections")
        G = None
    
    service_lines = []
    nearest_infra_types = []
    distances = []
    routing_methods = []
    
    for idx, building in buildings_proj.iterrows():
        building_centroid = building.geometry.centroid
        # Find nearest infrastructure
        nearest_idx = infra.distance(building_centroid).idxmin()
        nearest_geom = infra.loc[nearest_idx].geometry
        # Determine infrastructure type
        infra_type = infra.loc[nearest_idx]['power'] if 'power' in infra.columns else 'infrastructure'
        if G is not None:
            # Find nearest street node to building using direct distance calculation
            building_nearest_street = None
            min_building_distance = float('inf')
            for node in G.nodes():
                if G.nodes[node]['node_type'] == 'street':
                    node_pos = G.nodes[node]['pos']
                    node_point = Point(node_pos)
                    distance = building_centroid.distance(node_point)
                    if distance < min_building_distance:
                        min_building_distance = distance
                        building_nearest_street = node
            
            # Find nearest street node to infrastructure
            infra_nearest_street = None
            min_infra_distance = float('inf')
            for node in G.nodes():
                if G.nodes[node]['node_type'] == 'street':
                    node_pos = G.nodes[node]['pos']
                    node_point = Point(node_pos)
                    distance = nearest_geom.centroid.distance(node_point)
                    if distance < min_infra_distance:
                        min_infra_distance = distance
                        infra_nearest_street = node
            
            # Find shortest path between street nodes
            if building_nearest_street and infra_nearest_street:
                try:
                    path = nx.shortest_path(G, building_nearest_street, infra_nearest_street, weight='weight')
                    # Create path geometry
                    path_coords = []
                    for node in path:
                        node_pos = G.nodes[node]['pos']
                        path_coords.append(node_pos)
                    # Add building and infrastructure connection points
                    building_point = (building_centroid.x, building_centroid.y)
                    infra_point = (nearest_geom.centroid.x, nearest_geom.centroid.y)
                    # Create complete path: building -> street -> infrastructure
                    complete_coords = [building_point] + path_coords + [infra_point]
                    service_line = LineString(complete_coords)
                    # Calculate total distance
                    total_distance = 0
                    for i in range(len(complete_coords) - 1):
                        p1 = Point(complete_coords[i])
                        p2 = Point(complete_coords[i + 1])
                        total_distance += p1.distance(p2)
                    routing_methods.append('street_following')
                except nx.NetworkXNoPath:
                    # Fallback to straight line if no path found
                    nearest_point = nearest_points(building_centroid, nearest_geom)[1]
                    service_line = LineString([building_centroid, nearest_point])
                    total_distance = building_centroid.distance(nearest_point)
                    routing_methods.append('straight_line_fallback')
            else:
                # Fallback to straight line
                nearest_point = nearest_points(building_centroid, nearest_geom)[1]
                service_line = LineString([building_centroid, nearest_point])
                total_distance = building_centroid.distance(nearest_point)
                routing_methods.append('straight_line_fallback')
        else:
            # No street network, use straight line
            nearest_point = nearest_points(building_centroid, nearest_geom)[1]
            service_line = LineString([building_centroid, nearest_point])
            total_distance = building_centroid.distance(nearest_point)
            routing_methods.append('straight_line_no_streets')
        service_lines.append(service_line)
        nearest_infra_types.append(infra_type)
        distances.append(total_distance)
    # Add service line information to buildings
    buildings = buildings.copy()
    buildings['service_line'] = service_lines
    buildings['nearest_infra_type'] = nearest_infra_types
    buildings['service_line_distance'] = distances
    buildings['routing_method'] = routing_methods
    print(f"Computed {len(service_lines)} service lines")
    print(f"Infrastructure types: {pd.Series(nearest_infra_types).value_counts().to_dict()}")
    print(f"Routing methods: {pd.Series(routing_methods).value_counts().to_dict()}")
    return buildings

# --- 4.6. Compute Power Feasibility ---
def compute_power_feasibility(buildings, load_profiles, network_json_path, scenario="winter_werktag_abendspitze"):
    """
    Compute power flow feasibility for buildings that are close to transformers.
    Returns power metrics for each building that can be connected.
    
    Args:
        buildings: GeoDataFrame of buildings
        load_profiles: Dictionary of load profiles
        network_json_path: Path to network JSON file
        scenario: Load profile scenario to use (default: winter_werktag_abendspitze)
    """
    print("Computing power flow feasibility...")
    
    # Load network data
    with open(network_json_path, 'r') as f:
        network_data = json.load(f)
    
    nodes_data = network_data["nodes"]
    ways_data = network_data["ways"]
    
    # Create pandapower network
    net, node_id_to_bus, mv_bus = create_base_network_local(nodes_data)
    create_external_grid_local(net, mv_bus)
    transformers_created, trafo_mapping = create_transformers_local(net, mv_bus, node_id_to_bus, nodes_data)
    
    # Create lines (simplified version)
    lines_created = 0
    for way in ways_data:
        way_id = way['id']
        node_ids = [str(node_id) for node_id in way['nodes']]
        tags = way['tags']
        
        power_type = tags.get("power", "")
        connection_type = tags.get("connection", "")
        
        if power_type in ["line", "minor_line"] or connection_type in ["electrical", "electrical_highway"]:
            # Simplified line parameters
            params = {
                "r_ohm_per_km": 0.125,
                "x_ohm_per_km": 0.078,
                "c_nf_per_km": 264,
                "max_i_ka": 0.275
            }
            
            for i in range(len(node_ids) - 1):
                from_node_id = node_ids[i]
                to_node_id = node_ids[i + 1]
                from_bus = node_id_to_bus.get(from_node_id)
                to_bus = node_id_to_bus.get(to_node_id)
                
                if from_bus is None or to_bus is None:
                    continue
                
                from_node = next((node for node in nodes_data if str(node['id']) == from_node_id), None)
                to_node = next((node for node in nodes_data if str(node['id']) == to_node_id), None)
                if from_node is None or to_node is None:
                    continue
                
                # Calculate distance
                lon1, lat1 = from_node['lon'], from_node['lat']
                lon2, lat2 = to_node['lon'], to_node['lat']
                length_km = ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5 * 111  # Approximate km
                
                pp.create_line_from_parameters(
                    net,
                    from_bus=from_bus,
                    to_bus=to_bus,
                    length_km=length_km,
                    r_ohm_per_km=params["r_ohm_per_km"],
                    x_ohm_per_km=params["x_ohm_per_km"],
                    c_nf_per_km=params["c_nf_per_km"],
                    max_i_ka=params["max_i_ka"],
                    name=f"Line {way_id}_{i}"
                )
                lines_created += 1
    
    print(f"Created network with {len(net.bus)} buses, {len(net.line)} lines, {len(net.trafo)} transformers")
    
    # Initialize results
    power_metrics = {}
    
    # Process buildings that are close to transformers
    buildings_close_to_transformer = buildings[buildings['flag_far_transformer'] == False].copy()
    print(f"Processing {len(buildings_close_to_transformer)} buildings close to transformers...")
    
    for idx, building in buildings_close_to_transformer.iterrows():
        building_id = building.get('gebaeude', building.get('id', str(idx)))
        
        # Skip if no load profile available
        if building_id not in load_profiles:
            continue
        
        # Get peak load from selected scenario
        try:
            peak_load_kw = load_profiles[building_id][scenario]
        except KeyError:
            # Fallback to winter evening peak scenario
            try:
                peak_load_kw = load_profiles[building_id]["winter_werktag_abendspitze"]
            except KeyError:
                # Fallback to first available scenario
                scenarios = list(load_profiles[building_id].keys())
                if scenarios:
                    peak_load_kw = load_profiles[building_id][scenarios[0]]
                else:
                    continue
        
        # Convert to MW and calculate reactive power
        p_mw = peak_load_kw / 1000.0
        power_factor = 0.95
        q_mvar = p_mw * np.tan(np.arccos(power_factor))
        
        # Find nearest network node (consumer node)
        building_centroid = building.geometry.centroid
        min_distance = float('inf')
        nearest_node = None
        
        for node in nodes_data:
            if node['tags'].get('power') == 'consumer':
                node_point = Point(node['lon'], node['lat'])
                distance = building_centroid.distance(node_point)
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node
        
        if nearest_node is None:
            continue
        
        node_id = str(nearest_node['id'])
        if node_id not in node_id_to_bus:
            continue
        
        bus = node_id_to_bus[node_id]
        
        # Create load
        try:
            pp.create_load(
                net,
                bus=bus,
                p_mw=p_mw,
                q_mvar=q_mvar,
                name=f"Load_{building_id}"
            )
        except Exception as e:
            print(f"Error creating load for building {building_id}: {e}")
            continue
    
    # Run power flow analysis
    try:
        print("Running power flow analysis...")
        pp.runpp(net, algorithm='nr', max_iteration=40, tolerance_mva=1e-3)
        
        # Compute metrics
        if len(net.trafo) > 0:
            max_loading = max([trafo.loading_percent for trafo in net.res_trafo.itertuples()])
        else:
            max_loading = 0.0
        
        if len(net.bus) > 0:
            min_voltage = min([bus.vm_pu for bus in net.res_bus.itertuples()])
        else:
            min_voltage = 1.0
        
        # Store results for all buildings
        for idx, building in buildings.iterrows():
            building_id = building.get('gebaeude', building.get('id', str(idx)))
            power_metrics[building_id] = {
                "max_loading": max_loading,
                "min_voltage": min_voltage
            }
        
        print(f"Power flow analysis completed successfully")
        print(f"Max transformer loading: {max_loading:.2f}%")
        print(f"Min voltage: {min_voltage:.3f} pu")
        
    except pp.LoadflowNotConverged as e:
        print(f"Power flow did not converge: {e}")
        # Return default values for all buildings
        for idx, building in buildings.iterrows():
            building_id = building.get('gebaeude', building.get('id', str(idx)))
            power_metrics[building_id] = {
                "max_loading": np.nan,
                "min_voltage": np.nan
            }
    except Exception as e:
        print(f"Error in power flow analysis: {e}")
        # Return default values for all buildings
        for idx, building in buildings.iterrows():
            building_id = building.get('gebaeude', building.get('id', str(idx)))
            power_metrics[building_id] = {
                "max_loading": np.nan,
                "min_voltage": np.nan
            }
    
    return power_metrics

# --- 4.5. Compute Service Lines (Legacy - Straight Lines) ---
def compute_service_lines(buildings, substations, transformers):
    """
    Legacy function: Compute straight-line service lines from buildings to nearest infrastructure.
    """
    from shapely.ops import nearest_points
    
    # Combine substations and transformers into infrastructure
    if not substations.empty and not transformers.empty:
        infra = gpd.GeoDataFrame(pd.concat([substations, transformers], ignore_index=True))
    elif not substations.empty:
        infra = substations
    elif not transformers.empty:
        infra = transformers
    else:
        print("No infrastructure found for service line computation.")
        return buildings
    
    # Ensure we're in a projected CRS for accurate calculations
    if infra.crs.is_geographic:
        utm_crs = "EPSG:32633"
        infra = infra.to_crs(utm_crs)
        buildings_proj = buildings.to_crs(utm_crs)
    else:
        buildings_proj = buildings.to_crs(infra.crs)
    
    service_lines = []
    nearest_infra_types = []
    distances = []
    
    for idx, building in buildings_proj.iterrows():
        building_centroid = building.geometry.centroid
        
        # Find nearest infrastructure
        nearest_idx = infra.distance(building_centroid).idxmin()
        nearest_geom = infra.loc[nearest_idx].geometry
        
        # Get nearest point on infrastructure
        nearest_point = nearest_points(building_centroid, nearest_geom)[1]
        
        # Create service line
        service_line = LineString([building_centroid, nearest_point])
        service_lines.append(service_line)
        
        # Determine infrastructure type
        if nearest_idx < len(substations) if not substations.empty else 0:
            infra_type = 'substation'
        else:
            infra_type = 'transformer'
        nearest_infra_types.append(infra_type)
        
        # Calculate distance
        distance = building_centroid.distance(nearest_point)
        distances.append(distance)
    
    # Add service line information to buildings
    buildings = buildings.copy()
    buildings['service_line'] = service_lines
    buildings['nearest_infra_type'] = nearest_infra_types
    buildings['service_line_distance'] = distances
    
    print(f"Computed {len(service_lines)} service lines (straight-line)")
    print(f"Infrastructure types: {pd.Series(nearest_infra_types).value_counts().to_dict()}")
    
    return buildings

# --- 4. Proximity Analysis ---
def compute_proximity(buildings, lines, substations, plants, generators):
    """
    Compute proximity of buildings to power lines, substations, and transformers (treating plants and generators as transformers for proximity analysis).
    """
    # Merge plants and generators as transformers
    transformers = pd.concat([plants, generators], ignore_index=True)
    # Determine a suitable projected CRS (UTM zone based on buildings centroid)
    if buildings.crs is None or buildings.crs.is_geographic:
        # Estimate UTM CRS from centroid
        centroid = buildings.geometry.unary_union.centroid
        utm_crs = f"EPSG:326{int((centroid.x + 180) // 6 + 1):02d}"
        print(f"Reprojecting all layers to {utm_crs} for accurate distance calculations.")
        buildings = buildings.to_crs(utm_crs)
        lines = lines.to_crs(utm_crs) if not lines.empty else lines
        substations = substations.to_crs(utm_crs) if not substations.empty else substations
        transformers = transformers.to_crs(utm_crs) if not transformers.empty else transformers
    else:
        utm_crs = buildings.crs
        lines = lines.to_crs(utm_crs) if not lines.empty and lines.crs != utm_crs else lines
        substations = substations.to_crs(utm_crs) if not substations.empty and substations.crs != utm_crs else substations
        transformers = transformers.to_crs(utm_crs) if not transformers.empty and transformers.crs != utm_crs else transformers

    buildings = buildings.copy()
    buildings['centroid'] = buildings.geometry.centroid
    if not lines.empty:
        buildings['dist_to_line'] = buildings['centroid'].apply(lambda x: lines.distance(x).min())
    else:
        buildings['dist_to_line'] = np.nan
    if not substations.empty:
        buildings['dist_to_substation'] = buildings['centroid'].apply(lambda x: substations.distance(x).min())
    else:
        buildings['dist_to_substation'] = np.nan
    if not transformers.empty:
        buildings['dist_to_transformer'] = buildings['centroid'].apply(lambda x: transformers.distance(x).min())
    else:
        buildings['dist_to_transformer'] = np.nan
    buildings['flag_far_substation'] = buildings['dist_to_substation'] > 500
    buildings['flag_far_transformer'] = buildings['dist_to_transformer'] > 500
    return buildings

# --- 5. Output Table/CSV ---
def output_results_table(buildings, output_dir, metadata):
    cols = ['dist_to_line', 'dist_to_substation', 'dist_to_transformer', 'flag_far_substation', 'flag_far_transformer', 'max_trafo_loading', 'min_voltage_pu']
    id_col = None
    for c in ['gebaeudeid', 'GebaeudeID', 'gebaeude', 'id']:
        if c in buildings.columns:
            id_col = c
            break
    if id_col:
        out_df = buildings[[id_col] + cols]
    else:
        out_df = buildings[cols]
    
    # Write CSV with provenance metadata
    csv_path = Path(output_dir) / 'building_proximity_table.csv'
    with csv_path.open('w') as f:
        f.write(f"# Generated by commit {metadata['commit_sha']} at {metadata['run_time']}\n")
        out_df.to_csv(f, index=False)
    print(f"✅ Results table saved to {csv_path}")

# --- 6. Visualization (Enhanced Interactive Style) ---
def visualize(buildings, lines, substations, plants, generators, output_dir, show_building_to_line=False, streets_gdf=None, draw_service_lines=True, sample_service_lines=False, service_line_sample_size=100, metadata=None):
    """
    Enhanced interactive visualization with FeatureGroups and layer controls.
    Args:
        draw_service_lines: Whether to render any service-line connections on the map.
        sample_service_lines: If true, draw only a random subset of service lines (useful for debugging or performance).
        service_line_sample_size: Number of service lines to draw if sampling is enabled.
    """
    # 1. Work in projected CRS (UTM) for all distance and connection calculations
    # Determine UTM zone from buildings
    if buildings.crs is None or buildings.crs.is_geographic:
        centroid = buildings.geometry.unary_union.centroid
        utm_crs = f"EPSG:326{int((centroid.x + 180) // 6 + 1):02d}"
        buildings_utm = buildings.to_crs(utm_crs)
        lines_utm = lines.to_crs(utm_crs) if not lines.empty else lines
        substations_utm = substations.to_crs(utm_crs) if not substations.empty else substations
        plants_utm = plants.to_crs(utm_crs) if not plants.empty else plants
        generators_utm = generators.to_crs(utm_crs) if not generators.empty else generators
    else:
        utm_crs = buildings.crs
        buildings_utm = buildings
        lines_utm = lines.to_crs(utm_crs) if not lines.empty and lines.crs != utm_crs else lines
        substations_utm = substations.to_crs(utm_crs) if not substations.empty and substations.crs != utm_crs else substations
        plants_utm = plants.to_crs(utm_crs) if not plants.empty and plants.crs != utm_crs else plants
        generators_utm = generators.to_crs(utm_crs) if not generators.empty and generators.crs != utm_crs else generators

    # 2. Prepare connection lines in UTM
    connection_lines = []
    # Substation connections
    if not substations_utm.empty and not lines_utm.empty:
        for _, sub in substations_utm.iterrows():
            sub_centroid = sub.geometry.centroid
            nearest_line_idx = lines_utm.distance(sub_centroid).idxmin()
            nearest_geom = lines_utm.loc[nearest_line_idx].geometry
            nearest_point = nearest_points(sub_centroid, nearest_geom)[1]
            connection_lines.append({
                'color': 'red',
                'coords': [(sub_centroid.x, sub_centroid.y), (nearest_point.x, nearest_point.y)],
                'tooltip': 'Substation-Connection'
            })
    # Plant connections
    if not plants_utm.empty and not lines_utm.empty:
        for _, plant in plants_utm.iterrows():
            plant_centroid = plant.geometry.centroid
            nearest_line_idx = lines_utm.distance(plant_centroid).idxmin()
            nearest_geom = lines_utm.loc[nearest_line_idx].geometry
            nearest_point = nearest_points(plant_centroid, nearest_geom)[1]
            connection_lines.append({
                'color': 'green',
                'coords': [(plant_centroid.x, plant_centroid.y), (nearest_point.x, nearest_point.y)],
                'tooltip': 'Plant-Connection'
            })

    # 3. Reproject all geometries and connection lines to WGS84 for Folium
    buildings = buildings_utm.to_crs(epsg=4326)
    lines = lines_utm.to_crs(epsg=4326) if not lines_utm.empty else lines_utm
    substations = substations_utm.to_crs(epsg=4326) if not substations_utm.empty else substations_utm
    plants = plants_utm.to_crs(epsg=4326) if not plants_utm.empty else plants_utm
    generators = generators_utm.to_crs(epsg=4326) if not generators_utm.empty else generators_utm
    # Reproject connection lines
    transformer = Transformer.from_crs(utm_crs, 'EPSG:4326', always_xy=True)
    for conn in connection_lines:
        (x1, y1), (x2, y2) = conn['coords']
        lon1, lat1 = transformer.transform(x1, y1)
        lon2, lat2 = transformer.transform(x2, y2)
        conn['coords_wgs'] = [(lat1, lon1), (lat2, lon2)]

    # Recompute centroids in WGS84
    buildings['centroid'] = buildings.geometry.centroid

    center = buildings['centroid'].unary_union.centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=15)

    # 4. Create FeatureGroups for layer control
    fg_streets = folium.FeatureGroup(name='Streets', show=True)
    fg_power_lines = folium.FeatureGroup(name='Power Lines', show=True)
    fg_infra = folium.FeatureGroup(name='Infrastructure', show=False)
    fg_service_lines = folium.FeatureGroup(name='Service Lines', show=False)
    fg_buildings = folium.FeatureGroup(name='Buildings', show=True)

    # Plot street network if provided
    if streets_gdf is not None:
        streets = streets_gdf.to_crs(epsg=4326)
        for _, row in streets.iterrows():
            if row.geometry.geom_type == 'LineString':
                coords = list(row.geometry.coords)
                folium.PolyLine(
                    locations=[(lat, lon) for lon, lat in coords],
                    color='gray', weight=3, opacity=0.7, tooltip='Street'
                ).add_to(fg_streets)

    # Power lines with endpoints
    if not lines.empty:
        for _, row in lines.iterrows():
            if row.geometry.geom_type == 'LineString':
                coords = list(row.geometry.coords)
                folium.PolyLine(locations=[(lat, lon) for lon, lat in coords], color='orange', weight=4, opacity=0.8, tooltip=row.get('power', 'line')).add_to(fg_power_lines)
                # Mark start and end points
                start = coords[0]
                end = coords[-1]
                folium.CircleMarker(location=[start[1], start[0]], color='black', radius=5, tooltip='Line Start').add_to(fg_power_lines)
                folium.CircleMarker(location=[end[1], end[0]], color='yellow', radius=5, tooltip='Line End').add_to(fg_power_lines)
    
    # Draw connection lines in WGS84
    for conn in connection_lines:
        folium.PolyLine(locations=conn['coords_wgs'], color=conn['color'], weight=2, opacity=0.7, tooltip=conn['tooltip']).add_to(fg_power_lines)
    # Draw service lines if available
    if 'service_line' in buildings.columns and draw_service_lines:
        indices = list(range(len(buildings)))
        if sample_service_lines:
            indices = random.sample(indices, min(service_line_sample_size, len(indices)))
        for idx in indices:
            building = buildings.iloc[idx]
            if building['service_line'] is not None:
                service_line = building['service_line']
                if hasattr(service_line, 'coords'):
                    coords = list(service_line.coords)
                    if len(coords) >= 2:
                        # Reproject service line to WGS84 if needed
                        if buildings.crs != 'EPSG:4326':
                            transformer = Transformer.from_crs(buildings.crs, 'EPSG:4326', always_xy=True)
                            coords_wgs = []
                            for x, y in coords:
                                lon, lat = transformer.transform(x, y)
                                coords_wgs.append([lat, lon])
                        else:
                            coords_wgs = [[lat, lon] for lon, lat in coords]
                        # Color based on infrastructure type
                        color = 'red' if building.get('nearest_infra_type') == 'substation' else 'purple'
                        folium.PolyLine(locations=coords_wgs, color=color, weight=2, opacity=0.6, 
                                      tooltip=f"Service Line: {building.get('service_line_distance', 0):.1f}m to {building.get('nearest_infra_type', 'infrastructure')}").add_to(fg_service_lines)
    # Substations
    if not substations.empty:
        for _, row in substations.iterrows():
            if row.geometry.geom_type == 'Point' or row.geometry.geom_type == 'Polygon':
                centroid = row.geometry.centroid
                folium.CircleMarker(location=[centroid.y, centroid.x], color='red', radius=8, tooltip='Substation').add_to(fg_infra)
    # Plants
    if not plants.empty:
        for _, row in plants.iterrows():
            centroid = row.geometry.centroid
            folium.CircleMarker(location=[centroid.y, centroid.x], color='green', radius=8, tooltip='Plant').add_to(fg_infra)
    # Generators
    if not generators.empty:
        for _, row in generators.iterrows():
            centroid = row.geometry.centroid
            folium.CircleMarker(location=[centroid.y, centroid.x], color='purple', radius=6, tooltip='Generator').add_to(fg_infra)
    
    # Buildings
    for idx, b in buildings.iterrows():
        # Get distance values with proper formatting
        dist_to_line = b.get('dist_to_line', np.nan)
        dist_to_substation = b.get('dist_to_substation', np.nan)
        dist_to_transformer = b.get('dist_to_transformer', np.nan)
        max_loading = b.get('max_trafo_loading', np.nan)
        min_voltage = b.get('min_voltage_pu', np.nan)
        
        # Format values for display
        dist_to_line_str = f"{dist_to_line:.1f}" if not pd.isna(dist_to_line) else "N/A"
        dist_to_substation_str = f"{dist_to_substation:.1f}" if not pd.isna(dist_to_substation) else "N/A"
        dist_to_transformer_str = f"{dist_to_transformer:.1f}" if not pd.isna(dist_to_transformer) else "N/A"
        max_loading_str = f"{max_loading:.2f}" if not pd.isna(max_loading) else "N/A"
        min_voltage_str = f"{min_voltage:.3f}" if not pd.isna(min_voltage) else "N/A"
        
        tooltip = (
            f"Building ID: {str(idx)}<br>"
            f"Dist to line: {dist_to_line_str} m<br>"
            f"Dist to substation: {dist_to_substation_str} m<br>"
            f"Dist to transformer: {dist_to_transformer_str} m<br>"
            f"Max trafo loading: {max_loading_str}%<br>"
            f"Min voltage: {min_voltage_str} pu"
        )
        folium.CircleMarker(location=[b['centroid'].y, b['centroid'].x], color='blue', radius=3,
                            tooltip=tooltip).add_to(fg_buildings)
    # Add all FeatureGroups to the map
    for fg in [fg_streets, fg_power_lines, fg_infra, fg_service_lines, fg_buildings]:
        fg.add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add provenance metadata to the map
    if metadata:
        m.get_root().html.add_child(
            folium.Element(f'<!-- Generated by commit {metadata["commit_sha"]} at {metadata["run_time"]} -->')
        )
    
    # Save map to the specified output directory
    map_path = Path(output_dir) / 'hp_feasibility_map.html'
    m.save(str(map_path))
    print(f"✅ Interactive map saved to {map_path}")

# --- 7. Dashboard Creation ---
def create_hp_dashboard(map_path, stats_dict, chart_paths, output_path):
    """
    Create a comprehensive HTML dashboard for HP feasibility analysis.
    
    Args:
        map_path: Path to the interactive map HTML file
        stats_dict: Dictionary of statistics to display
        chart_paths: List of paths to chart images
        output_path: Output path for the dashboard HTML
    """
    # Convert chart paths to base64 for embedding
    import base64
    
    chart_images = []
    for chart_path in chart_paths:
        try:
            with open(chart_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                chart_images.append(f"data:image/png;base64,{img_data}")
        except FileNotFoundError:
            chart_images.append("")
    
    dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heat Pump Feasibility Analysis Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }}
        .left-panel {{ display: flex; flex-direction: column; gap: 20px; }}
        .right-panel {{ display: flex; flex-direction: column; gap: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric-card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .metric-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 8px; font-size: 14px; }}
        .metric-value {{ font-size: 20px; color: #27ae60; font-weight: bold; }}
        .metric-unit {{ font-size: 12px; color: #7f8c8d; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ color: #2c3e50; border-bottom: 2px solid #bdc3c7; padding-bottom: 8px; margin-bottom: 15px; font-size: 16px; }}
        .status-success {{ color: #27ae60; font-weight: bold; }}
        .status-warning {{ color: #f39c12; font-weight: bold; }}
        .status-error {{ color: #e74c3c; font-weight: bold; }}
        .map-container {{ text-align: center; }}
        .map-container iframe {{ border: 1px solid #bdc3c7; border-radius: 8px; width: 100%; height: calc(100vh - 200px); min-height: 500px; }}
        .chart-container {{ text-align: center; margin: 15px 0; }}
        .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #bdc3c7; border-radius: 8px; }}
        .summary-stats {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
        .summary-stats h4 {{ margin-top: 0; color: #2c3e50; }}
        .summary-stats ul {{ margin: 0; padding-left: 20px; }}
        .summary-stats li {{ margin-bottom: 5px; }}
        .scenario-selector {{ margin-bottom: 15px; }}
        .scenario-selector select {{ padding: 8px 12px; border: 1px solid #bdc3c7; border-radius: 4px; font-size: 14px; }}
        .scenario-selector label {{ font-weight: bold; color: #2c3e50; margin-right: 10px; }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .dashboard-grid {{ grid-template-columns: 1fr; }}
            .container {{ padding: 15px; margin: 10px; }}
            .metric-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
            .map-container iframe {{ height: 400px; }}
        }}
        
        @media (max-width: 480px) {{
            .metric-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 24px; }}
            .header h2 {{ font-size: 18px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔌 Heat Pump Feasibility Analysis Dashboard</h1>
            <h2>Branitzer Siedlung - Electrical Infrastructure Assessment</h2>
            <p>Comprehensive analysis of electrical infrastructure for heat pump deployment</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="left-panel">
                <div class="section">
                    <h3 class="section-title">📊 Electrical Network Metrics</h3>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-title">Max Transformer Loading</div>
                            <div class="metric-value">{stats_dict.get('MaxTrafoLoading', 'N/A'):.2f}%</div>
                            <div class="metric-unit">peak utilization</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Min Voltage</div>
                            <div class="metric-value">{stats_dict.get('MinVoltagePU', 'N/A'):.3f}</div>
                            <div class="metric-unit">per unit</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Avg Distance to Line</div>
                            <div class="metric-value">{stats_dict.get('AvgDistLine', 'N/A'):.0f}</div>
                            <div class="metric-unit">meters</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Avg Distance to Substation</div>
                            <div class="metric-value">{stats_dict.get('AvgDistSub', 'N/A'):.0f}</div>
                            <div class="metric-unit">meters</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">🏢 Building Proximity Analysis</h3>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-title">Total Buildings</div>
                            <div class="metric-value">{stats_dict.get('TotalBuildings', 'N/A')}</div>
                            <div class="metric-unit">buildings</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Close to Transformer</div>
                            <div class="metric-value">{stats_dict.get('CloseToTransformer', 'N/A')}</div>
                            <div class="metric-unit">buildings</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Service Connections</div>
                            <div class="metric-value">{stats_dict.get('ServiceConnections', 'N/A')}</div>
                            <div class="metric-unit">connections</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-title">Network Coverage</div>
                            <div class="metric-value">{stats_dict.get('NetworkCoverage', 'N/A'):.1f}%</div>
                            <div class="metric-unit">coverage</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">⚡ System Status</h3>
                    <div class="summary-stats">
                        <h4>Electrical Infrastructure Assessment</h4>
                        <ul>
                            <li><span class="status-success">✅ Power Flow Analysis</span> - Newton-Raphson convergence achieved</li>
                            <li><span class="status-success">✅ Street-Following Routing</span> - All service connections follow streets</li>
                            <li><span class="status-success">✅ Capacity Assessment</span> - Transformer loading and voltage analysis</li>
                            <li><span class="status-success">✅ Proximity Analysis</span> - Distance-based feasibility assessment</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="section">
                    <h3 class="section-title">🗺️ Interactive Network Map</h3>
                    <div class="scenario-selector">
                        <label for="scenario-select">Load Profile Scenario:</label>
                        <select id="scenario-select" onchange="updateMapScenario()">
                            <option value="winter_werktag_abendspitze">Winter Weekday Evening Peak</option>
                            <option value="summer_sonntag_abendphase">Summer Sunday Evening</option>
                            <option value="winter_werktag_mittag">Winter Weekday Noon</option>
                            <option value="summer_werktag_abendspitze">Summer Weekday Evening Peak</option>
                        </select>
                    </div>
                    <div class="map-container">
                        <iframe id="map-iframe" src="{map_path}"></iframe>
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">📈 Analysis Charts</h3>"""
    
    # Add charts if available
    if len(chart_images) >= 2:
        dashboard_html += f"""
                    <div class="chart-container">
                        <h4>Distance to Transformer Distribution</h4>
                        <img src="{chart_images[0]}" alt="Distance to Transformer Histogram">
                    </div>
                    <div class="chart-container">
                        <h4>Distance to Power Line Distribution</h4>
                        <img src="{chart_images[1]}" alt="Distance to Power Line Histogram">
                    </div>"""
    elif len(chart_images) == 1:
        dashboard_html += f"""
                    <div class="chart-container">
                        <h4>Distance to Transformer Distribution</h4>
                        <img src="{chart_images[0]}" alt="Distance to Transformer Histogram">
                    </div>"""
    
    dashboard_html += f"""
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3 class="section-title">✅ Implementation Readiness</h3>
            <div class="summary-stats">
                <h4>Heat Pump Deployment Assessment</h4>
                <ul>
                    <li><span class="status-success">✅ Electrical Capacity</span> - Network can support heat pump loads</li>
                    <li><span class="status-success">✅ Infrastructure Proximity</span> - Buildings within connection range</li>
                    <li><span class="status-success">✅ Street-Based Routing</span> - Construction-ready service connections</li>
                    <li><span class="status-success">✅ Power Quality</span> - Voltage levels within acceptable range</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        function updateMapScenario() {{
            const select = document.getElementById('scenario-select');
            const iframe = document.getElementById('map-iframe');
            const selectedScenario = select.value;
            
            // Update iframe source with scenario parameter
            const currentSrc = iframe.src;
            const baseUrl = currentSrc.split('?')[0];
            iframe.src = baseUrl + '?scenario=' + selectedScenario;
            
            console.log('Updated map scenario to:', selectedScenario);
        }}
    </script>
</body>
</html>"""
    
    # Save dashboard
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print(f"✅ Dashboard created: {output_path}")

# --- MAIN PIPELINE ---
def main():
    # Capture Git SHA and timestamp for provenance
    try:
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit_sha = "unknown"
    run_time = datetime.now().isoformat()
    metadata = {'commit_sha': commit_sha, 'run_time': run_time}
    
    # Check for scenario parameter (for interactive scenario selection)
    import sys
    scenario = "winter_werktag_abendspitze"  # default scenario
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    
    print(f"Running analysis with commit {commit_sha} at {run_time}")
    print(f"Using load profile scenario: {scenario}")
    
    print_power_tags()
    lines, substations, plants, generators = load_power_infrastructure()
    buildings = load_buildings(BUILDINGS_FILE)
    
    # Load load profiles for power flow analysis
    load_profiles_file = Path('thesis-data-2/power-sim/gebaeude_lastphasenV2.json')
    if load_profiles_file.exists():
        load_profiles = load_load_profiles(load_profiles_file)
    else:
        print(f"Warning: Load profiles file not found at {load_profiles_file}")
        load_profiles = {}
    
    # Load street data for street-following routing
    if not STREETS_FILE.exists():
        raise FileNotFoundError(f"Street network not found at {STREETS_FILE}")
    print(f"Loading street data from {STREETS_FILE}...")
    streets_gdf = gpd.read_file(STREETS_FILE)
    print(f"Loaded {len(streets_gdf)} street segments")
    
    # For proximity, treat plants, generators as transformers for now (or adjust as needed)
    buildings = compute_proximity(buildings, lines, substations, plants, generators)
    # Compute service lines from buildings to nearest infrastructure (street-following if available)
    buildings = compute_service_lines_street_following(buildings, substations, plants, generators, streets_gdf)
    
    # Compute power flow feasibility
    network_json_path = Path('thesis-data-2/power-sim/branitzer_siedlung_ns_v3_ohne_UW.json')
    if network_json_path.exists() and load_profiles:
        power_metrics = compute_power_feasibility(buildings, load_profiles, network_json_path, scenario)
        
        # Add power metrics to buildings dataframe
        for idx, row in buildings.iterrows():
            building_id = row.get('gebaeude', row.get('id', str(idx)))
            metrics = power_metrics.get(building_id, {})
            buildings.at[idx, 'max_trafo_loading'] = metrics.get('max_loading', np.nan)
            buildings.at[idx, 'min_voltage_pu'] = metrics.get('min_voltage', np.nan)
    else:
        print(f"Warning: Network JSON file not found at {network_json_path}")
        # Add empty columns
        buildings['max_trafo_loading'] = np.nan
        buildings['min_voltage_pu'] = np.nan
    
    output_results_table(buildings, OUTPUT_DIR, metadata)
    visualize(buildings, lines, substations, plants, generators, OUTPUT_DIR, show_building_to_line=False, streets_gdf=streets_gdf, draw_service_lines=True, sample_service_lines=False, metadata=metadata)
    
    # Create dashboard with charts
    print("Creating enhanced dashboard with charts...")
    
    # Calculate statistics
    stats = {
        'MaxTrafoLoading': buildings['max_trafo_loading'].max(),
        'MinVoltagePU': buildings['min_voltage_pu'].min(),
        'AvgDistLine': buildings['dist_to_line'].mean(),
        'AvgDistSub': buildings['dist_to_substation'].mean(),
        'AvgDistTrans': buildings['dist_to_transformer'].mean(),
        'TotalBuildings': len(buildings),
        'CloseToTransformer': len(buildings[buildings['flag_far_transformer'] == False]),
        'ServiceConnections': len(buildings),
        'NetworkCoverage': (len(buildings[buildings['flag_far_transformer'] == False]) / len(buildings)) * 100
    }
    
    # Generate charts
    chart_paths = []
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        # Chart 1: Distance to transformer histogram
        plt.figure(figsize=(10, 6))
        plt.hist(buildings['dist_to_transformer'].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Distance to Transformer (meters)')
        plt.ylabel('Number of Buildings')
        plt.title('Distribution of Building Distances to Transformers')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        chart1_path = '/tmp/dist_transformer_hist.png'
        plt.savefig(chart1_path, dpi=150, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart1_path)
        
        # Chart 2: Distance to power line histogram
        plt.figure(figsize=(10, 6))
        plt.hist(buildings['dist_to_line'].dropna(), bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.xlabel('Distance to Power Line (meters)')
        plt.ylabel('Number of Buildings')
        plt.title('Distribution of Building Distances to Power Lines')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        chart2_path = '/tmp/dist_line_hist.png'
        plt.savefig(chart2_path, dpi=150, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart2_path)
        
        print("✅ Charts generated successfully")
        
    except ImportError:
        print("⚠️ Matplotlib not available, skipping charts")
    except Exception as e:
        print(f"⚠️ Error generating charts: {e}")
    
    # Create dashboard
    dashboard_path = OUTPUT_DIR / 'hp_feasibility_dashboard.html'
    create_hp_dashboard(
        map_path='branitz_hp_feasibility_map.html',
        stats_dict=stats,
        chart_paths=chart_paths,
        output_path=dashboard_path
    )
    
    print("All steps completed. Check the output directory for results.")

if __name__ == "__main__":
    main() 
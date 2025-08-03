import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
from shapely.geometry import LineString
import json
import networkx as nx
from scipy.spatial import distance_matrix

# --- Part 1: Load Your Data Files ---

# Load the building footprints
buildings_gdf = gpd.read_file("results_test/buildings_prepared.geojson")

# !! ACTION REQUIRED: Provide the path to your street map file !!
# This can be a GeoJSON, Shapefile, or other format GeoPandas can read.
street_filepath = "results_test/streets.geojson" 

try:
    street_gdf = gpd.read_file(street_filepath)
except Exception as e:
    print(f"Error loading street file: {e}")
    print("Please make sure the path is correct and the file exists.")
    street_gdf = None

# Proceed only if both files were loaded successfully
if not buildings_gdf.empty and street_gdf is not None:

    # --- Part 2: Prepare Data and Calculate Network ---

    # Project both layers to the same projected CRS for accuracy
    print(f"Projecting layers to a suitable local CRS...")
    utm_crs = buildings_gdf.estimate_utm_crs()
    buildings_proj = buildings_gdf.to_crs(utm_crs)
    street_proj = street_gdf.to_crs(utm_crs)
    print(f"Layers projected to: {utm_crs}")

    # Combine all street segments into one continuous line for calculations
    street_line = street_proj.geometry.unary_union
    
    # Calculate the service line connections
    connection_lines = []
    building_street_connections = []  # Store building to street connections
    
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

    # Create a new GeoDataFrame for the connection lines
    connections_gdf = gpd.GeoDataFrame(geometry=connection_lines, crs=utm_crs)
    print(f"Successfully calculated {len(connections_gdf)} service connections.")

    # --- Part 3: Create Network Graph ---
    
    # Create building-to-building network using minimum spanning tree
    building_centroids = buildings_proj.geometry.centroid
    building_ids = buildings_proj.get('GebaeudeID', buildings_proj.get('oi', [f'building_{i}' for i in range(len(buildings_proj))]))
    
    # Create position dictionary
    pos = {building_id: (centroid.x, centroid.y) for building_id, centroid in zip(building_ids, building_centroids)}
    
    # Create complete graph
    coordinates = list(pos.values())
    complete_graph = nx.Graph()
    dist_matrix = distance_matrix(coordinates, coordinates)
    
    for i in range(len(building_ids)):
        for j in range(i + 1, len(building_ids)):
            id1 = building_ids[i]
            id2 = building_ids[j]
            dist = dist_matrix[i, j]
            complete_graph.add_edge(id1, id2, weight=dist)

    # Create minimum spanning tree
    mst_graph = nx.minimum_spanning_tree(complete_graph)
    print(f"Created network graph with {mst_graph.number_of_nodes()} nodes and {mst_graph.number_of_edges()} edges.")

    # --- Part 4: Export to JSON ---
    
    # Prepare graph data for JSON export
    graph_data = {
        'metadata': {
            'total_buildings': len(buildings_proj),
            'total_connections': len(connections_gdf),
            'graph_nodes': mst_graph.number_of_nodes(),
            'graph_edges': mst_graph.number_of_edges(),
            'crs': str(utm_crs)
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
    json_output_path = "results_test/network_graph.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully exported network graph to JSON: {json_output_path}")

    # --- Part 5: Plot Everything on the Map ---

    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Plot layers from bottom to top by controlling the call order
    
    # 1. Plot the main street line (bottom layer)
    street_proj.plot(ax=ax, color="black", linewidth=3, label="Main Street")
    
    # 2. Plot buildings on top of the street
    buildings_proj.plot(ax=ax, color="lightgrey", edgecolor="black")
    
    # 3. Plot the new service connection lines on top of buildings
    connections_gdf.plot(ax=ax, color="red", linewidth=1.5, label="Service Connections")
    
    # 4. Plot the MST graph edges
    edge_artists = nx.draw_networkx_edges(
        mst_graph,
        pos,
        ax=ax,
        edge_color="#0066ff",
        width=2,
        alpha=0.7
    )
    
    # 5. Plot the MST graph nodes
    node_artists = nx.draw_networkx_nodes(
        mst_graph,
        pos,
        ax=ax,
        node_size=60,
        node_color="blue",
        edgecolors="black"
    )

    ax.set_title("Network Connections and Building Graph")
    ax.set_axis_off()
    ax.set_aspect('equal', adjustable='box') # Ensure correct aspect ratio
    plt.legend()
    plt.tight_layout()
    plt.show()


    # --- Part 6: Export the Network for JOSM (see Part 2 of explanation) ---

    # Define output file paths
    output_connections_path = "results_test/service_connections.geojson"
    output_buildings_path = "results_test/buildings_projected.geojson"
    output_street_path = "results_test/street_projected.geojson"

    # Export the calculated connection lines
    connections_gdf.to_file(output_connections_path, driver="GeoJSON")
    
    # Also export the projected buildings and street for context in JOSM
    buildings_proj.to_file(output_buildings_path, driver="GeoJSON")
    street_proj.to_file(output_street_path, driver="GeoJSON")

    print(f"\nSuccessfully exported network files for JOSM:")
    print(f"- Connections: {output_connections_path}")
    print(f"- Buildings: {output_buildings_path}")
    print(f"- Street: {output_street_path}")
    print(f"- JSON Graph: {json_output_path}")
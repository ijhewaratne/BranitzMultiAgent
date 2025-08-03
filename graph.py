import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix

# Load just the building geodata
nodes_gdf = gpd.read_file("results_test/buildings_prepared.geojson")

# Ensure the GeoDataFrame is not empty
if nodes_gdf.empty:
    print("Error: The GeoJSON file is empty or could not be read.")
else:
    # --- Part 1: Prepare Node Positions ---
    utm_crs = nodes_gdf.estimate_utm_crs()
    nodes_proj = nodes_gdf.to_crs(utm_crs)
    nodes_proj["centroid"] = nodes_proj.geometry.centroid

    # Create the position dictionary using the unique building ID
    pos = {
        row["GebaeudeID"]: (row.centroid.x, row.centroid.y)
        for _, row in nodes_proj.iterrows()
    }

    # --- Part 2: Create a New Network from the Buildings ---
    building_ids = list(pos.keys())
    coordinates = list(pos.values())
    complete_graph = nx.Graph()
    dist_matrix = distance_matrix(coordinates, coordinates)
    
    for i in range(len(building_ids)):
        for j in range(i + 1, len(building_ids)):
            id1 = building_ids[i]
            id2 = building_ids[j]
            dist = dist_matrix[i, j]
            complete_graph.add_edge(id1, id2, weight=dist)

    mst_graph = nx.minimum_spanning_tree(complete_graph)
    print(f"Successfully created a new network with {mst_graph.number_of_nodes()} nodes and {mst_graph.number_of_edges()} edges.")


    # --- Part 3: PLOTTING SECTION CORRECTED FOR YOUR ENVIRONMENT ---

    fig, ax = plt.subplots(figsize=(12, 12))

    # 1) Plot background building footprints with zorder=0
    # This part is okay because the geopandas plot function handles zorder correctly.
    nodes_proj.plot(ax=ax, color="lightgrey", edgecolor="black", alpha=0.7, zorder=0)

    # 2) Draw the edges WITHOUT the zorder keyword and capture the artists
    edge_artists = nx.draw_networkx_edges(
        mst_graph,
        pos,
        ax=ax,
        edge_color="#0066ff",
        width=1.5
    )
    # Now, manually set the zorder on the returned artists
    if isinstance(edge_artists, list):
        for artist in edge_artists:
            artist.set_zorder(1)
    else:
        edge_artists.set_zorder(1)

    # 3) Draw the nodes WITHOUT the zorder keyword and capture the artists
    node_artists = nx.draw_networkx_nodes(
        mst_graph,
        pos,
        ax=ax,
        node_size=60,
        node_color="red",
        edgecolors="black"
    )
    # Now, manually set the zorder on the returned artists
    node_artists.set_zorder(2)

    ax.set_title("Minimum Spanning Tree Network of Buildings")
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
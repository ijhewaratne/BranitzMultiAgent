# src/network_construction.py

import networkx as nx

def create_network_graph(buildings, street_edges_gdf, street_nodes_gdf, output_graphml=None):
    """
    Build the networkx graph for the street/energy system.
    - buildings: GeoDataFrame
    - street_edges_gdf: GeoDataFrame (edges)
    - street_nodes_gdf: GeoDataFrame (nodes)
    - output_graphml: filename to save the graph, or None
    Returns: networkx.Graph
    """
    G = nx.Graph()

    # Add nodes, avoid duplicate x/y keys
    for idx, row in street_nodes_gdf.iterrows():
        node_attrs = {k: v for k, v in row.items() if k != 'geometry' and k not in ['x', 'y']}
        G.add_node(
            row['osmid'] if 'osmid' in row else idx,
            x=row.geometry.x,
            y=row.geometry.y,
            **node_attrs
        )

    # Add edges between nodes (if your edges GeoDataFrame has 'from' and 'to')
    for idx, edge_row in street_edges_gdf.iterrows():
        from_node = edge_row['from'] if 'from' in edge_row else None
        to_node = edge_row['to'] if 'to' in edge_row else None
        if from_node is not None and to_node is not None:
            edge_attrs = {k: v for k, v in edge_row.items() if k != 'geometry'}
            G.add_edge(from_node, to_node, **edge_attrs)

    # Attach buildings as nodes (if required)
    # Example: for idx, bldg in buildings.iterrows():
    #     G.add_node(f"building_{idx}", x=bldg.geometry.x, y=bldg.geometry.y, type='building')

    if output_graphml:
        # Clean None values from node and edge attributes for GraphML compatibility
        for node, data in G.nodes(data=True):
            for k, v in list(data.items()):
                if v is None:
                    data[k] = ""
        for u, v, data in G.edges(data=True):
            for k, v2 in list(data.items()):
                if v2 is None:
                    data[k] = ""

        nx.write_graphml(G, output_graphml)

    return G

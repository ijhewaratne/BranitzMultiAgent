# tools/data_tools.py
"""
Data exploration and retrieval tools for the enhanced energy analysis system.
"""

import os
from .core_imports import tool, gpd, Path

@tool
def get_all_street_names() -> list[str]:
    """
    Retrieves all available street names from the building dataset.
    
    Returns:
        A list of all street names available for analysis.
    """
    print("TOOL: Getting all street names...")
    
    try:
        # Load buildings data
        buildings_file = "data/geojson/hausumringe_mit_adressenV3.geojson"
        if not os.path.exists(buildings_file):
            return ["Error: Buildings file not found"]
        
        buildings_gdf = gpd.read_file(buildings_file)
        
        # Extract unique street names
        if 'strasse' in buildings_gdf.columns:
            street_names = buildings_gdf['strasse'].dropna().unique().tolist()
        elif 'street' in buildings_gdf.columns:
            street_names = buildings_gdf['street'].dropna().unique().tolist()
        else:
            return ["Error: No street name column found in buildings data"]
        
        # Sort and return
        street_names.sort()
        return street_names[:50]  # Limit to first 50 for display
        
    except Exception as e:
        return [f"Error retrieving street names: {str(e)}"]

@tool
def get_building_ids_for_street(street_name: str) -> list[str]:
    """
    Retrieves building IDs for a specific street.
    
    Args:
        street_name: The name of the street to get building IDs for
        
    Returns:
        A list of building IDs for the specified street
    """
    print(f"TOOL: Getting building IDs for '{street_name}'...")
    
    try:
        # Load buildings data
        buildings_file = "data/geojson/hausumringe_mit_adressenV3.geojson"
        if not os.path.exists(buildings_file):
            return ["Error: Buildings file not found"]
        
        buildings_gdf = gpd.read_file(buildings_file)
        
        # Filter buildings for the specified street
        if 'strasse' in buildings_gdf.columns:
            street_buildings = buildings_gdf[buildings_gdf['strasse'] == street_name]
        elif 'street' in buildings_gdf.columns:
            street_buildings = buildings_gdf[buildings_gdf['street'] == street_name]
        else:
            return ["Error: No street name column found in buildings data"]
        
        # Extract building IDs
        if 'GebaeudeID' in street_buildings.columns:
            building_ids = street_buildings['GebaeudeID'].dropna().astype(str).tolist()
        elif 'building_id' in street_buildings.columns:
            building_ids = street_buildings['building_id'].dropna().astype(str).tolist()
        else:
            building_ids = [f"Building_{i}" for i in range(len(street_buildings))]
        
        return building_ids
        
    except Exception as e:
        return [f"Error retrieving building IDs: {str(e)}"] 
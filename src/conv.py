import geopandas as gpd
import pandas as pd
import json

# Load building geometries
buildings_gdf = gpd.read_file("data/geojson/hausumringe_mit_flurid.geojson")

# Load attributes JSON
with open("data/json/output_branitzer_siedlungV11.json", "r") as f:
    attrs_dict = json.load(f)

attrs_df = pd.DataFrame.from_dict(attrs_dict, orient="index")
attrs_df['oi'] = attrs_df.index  # <-- This is the fix!

# Ensure oi is string type
buildings_gdf['oi'] = buildings_gdf['oi'].astype(str)
attrs_df['oi'] = attrs_df['oi'].astype(str)

# Merge
merged_gdf = buildings_gdf.merge(attrs_df[['oi', 'GebaeudeID']], on='oi', how='left')

print(merged_gdf[['oi', 'GebaeudeID']].head())

merged_gdf.to_file("data/geojson/hausumringe_with_gebaeudeid.geojson", driver="GeoJSON")

#!/usr/bin/env python3
"""
Building Demand and Load Profile Analysis
Analyzes building energy demands and load profiles for the Branitz area.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import geopandas as gpd

def load_building_data():
    """Load building demand and load profile data."""
    print("📊 Loading Building Data...")
    
    # Load load profiles
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2.json', 'r') as f:
        load_profiles = json.load(f)
    
    # Load building demands
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2_verbrauch.json', 'r') as f:
        building_demands = json.load(f)
    
    # Load building geometries
    buildings_gdf = gpd.read_file('data/geojson/hausumringe_mit_adressenV3.geojson')
    
    print(f"✅ Loaded data for {len(load_profiles)} buildings")
    return load_profiles, building_demands, buildings_gdf

def analyze_building_types(building_demands):
    """Analyze building types and their characteristics."""
    print("\n🏢 Building Type Analysis:")
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame.from_dict(building_demands, orient='index')
    
    # Building type summary
    building_types = df['gebaeudefunktion'].value_counts()
    print(f"\nBuilding Types (Top 10):")
    for i, (btype, count) in enumerate(building_types.head(10).items(), 1):
        print(f"  {i:2d}. {btype}: {count} buildings")
    
    # Energy consumption by building type
    print(f"\nEnergy Consumption by Building Type:")
    energy_by_type = df.groupby('gebaeudefunktion').agg({
        'jahresverbrauch_kwh': ['mean', 'sum', 'count'],
        'nutzflaeche_m2': 'mean',
        'spezifischer_verbrauch_kwh_pro_m2': 'mean'
    }).round(2)
    
    energy_by_type.columns = ['Avg_Annual_kWh', 'Total_Annual_kWh', 'Building_Count', 'Avg_Area_m2', 'Avg_Specific_kWh_m2']
    energy_by_type = energy_by_type.sort_values('Total_Annual_kWh', ascending=False)
    
    print(energy_by_type.head(10))
    
    return df, energy_by_type

def analyze_load_profiles(load_profiles):
    """Analyze load profiles for different scenarios."""
    print("\n⚡ Load Profile Analysis:")
    
    # Get all scenario names
    sample_building = list(load_profiles.keys())[0]
    scenarios = list(load_profiles[sample_building].keys())
    
    print(f"\nAvailable Scenarios ({len(scenarios)}):")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i:2d}. {scenario}")
    
    # Analyze peak loads for different scenarios
    print(f"\nPeak Load Analysis:")
    peak_loads = {}
    for scenario in scenarios:
        loads = [load_profiles[building][scenario] for building in load_profiles.keys()]
        peak_loads[scenario] = {
            'max': max(loads),
            'min': min(loads),
            'mean': np.mean(loads),
            'median': np.median(loads)
        }
    
    peak_df = pd.DataFrame.from_dict(peak_loads, orient='index')
    print(peak_df.round(4))
    
    return scenarios, peak_loads

def analyze_street_buildings(buildings_gdf, building_demands):
    """Analyze buildings by street."""
    print("\n🏘️ Street Analysis:")
    
    # Get unique streets
    streets = []
    for idx, building in buildings_gdf.iterrows():
        try:
            adressen = json.loads(building['adressen'])
            for addr in adressen:
                if addr.get('str'):
                    streets.append(addr['str'])
        except:
            continue
    
    unique_streets = list(set(streets))
    print(f"\nFound {len(unique_streets)} unique streets")
    
    # Show top streets by building count
    street_counts = {}
    for street in unique_streets:
        count = streets.count(street)
        street_counts[street] = count
    
    street_df = pd.DataFrame(list(street_counts.items()), columns=['Street', 'Building_Count'])
    street_df = street_df.sort_values('Building_Count', ascending=False)
    
    print(f"\nTop 15 Streets by Building Count:")
    print(street_df.head(15))
    
    return street_df

def create_load_profile_visualization(load_profiles, scenarios):
    """Create load profile visualization."""
    print("\n📈 Creating Load Profile Visualization...")
    
    # Select a few representative scenarios
    key_scenarios = [
        'winter_werktag_abendspitze',
        'winter_werktag_morgenspitze', 
        'sommer_werktag_abendspitze',
        'sommer_werktag_morgenspitze'
    ]
    
    # Get sample buildings
    sample_buildings = list(load_profiles.keys())[:5]
    
    # Create plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.ravel()
    
    for i, scenario in enumerate(key_scenarios):
        loads = [load_profiles[building][scenario] for building in sample_buildings]
        
        axes[i].bar(range(len(sample_buildings)), loads)
        axes[i].set_title(f'Load Profile: {scenario}')
        axes[i].set_xlabel('Building Index')
        axes[i].set_ylabel('Load (pu)')
        axes[i].set_xticks(range(len(sample_buildings)))
        axes[i].set_xticklabels([f'B{i+1}' for i in range(len(sample_buildings))])
    
    plt.tight_layout()
    plt.savefig('building_load_profiles_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved load profile visualization to 'building_load_profiles_analysis.png'")
    
    return fig

def analyze_specific_street(street_name, buildings_gdf, building_demands, load_profiles):
    """Analyze buildings for a specific street."""
    print(f"\n🏘️ Analysis for Street: {street_name}")
    
    # Find buildings on this street
    street_buildings = []
    for idx, building in buildings_gdf.iterrows():
        try:
            adressen = json.loads(building['adressen'])
            for addr in adressen:
                if addr.get('str', '').lower() == street_name.lower():
                    building_id = building.get('gebaeude', building.get('id', str(idx)))
                    street_buildings.append({
                        'building_id': building_id,
                        'geometry': building.geometry,
                        'adressen': adressen
                    })
                    break
        except:
            continue
    
    print(f"Found {len(street_buildings)} buildings on {street_name}")
    
    if street_buildings:
        # Analyze building demands for this street
        street_demands = []
        for building in street_buildings:
            building_id = building['building_id']
            if building_id in building_demands:
                demand = building_demands[building_id].copy()
                demand['building_id'] = building_id
                street_demands.append(demand)
        
        if street_demands:
            street_df = pd.DataFrame(street_demands)
            print(f"\nBuilding Demands for {street_name}:")
            print(street_df[['gebaeudefunktion', 'nutzflaeche_m2', 'jahresverbrauch_kwh', 'spezifischer_verbrauch_kwh_pro_m2']].round(2))
            
            # Load profile analysis for this street
            print(f"\nLoad Profile Summary for {street_name}:")
            street_loads = {}
            for building in street_buildings:
                building_id = building['building_id']
                if building_id in load_profiles:
                    for scenario, load in load_profiles[building_id].items():
                        if scenario not in street_loads:
                            street_loads[scenario] = []
                        street_loads[scenario].append(load)
            
            # Calculate statistics
            for scenario, loads in street_loads.items():
                if loads:
                    print(f"  {scenario}: max={max(loads):.4f}, min={min(loads):.4f}, avg={np.mean(loads):.4f}")
    
    return street_buildings

def main():
    """Main analysis function."""
    print("🔍 Building Demand and Load Profile Analysis")
    print("=" * 60)
    
    # Load data
    load_profiles, building_demands, buildings_gdf = load_building_data()
    
    # Analyze building types
    df, energy_by_type = analyze_building_types(building_demands)
    
    # Analyze load profiles
    scenarios, peak_loads = analyze_load_profiles(load_profiles)
    
    # Analyze streets
    street_df = analyze_street_buildings(buildings_gdf, building_demands)
    
    # Create visualization
    fig = create_load_profile_visualization(load_profiles, scenarios)
    
    # Analyze specific streets
    sample_streets = ['Damaschkeallee', 'Parkstraße', 'Luciestraße']
    for street in sample_streets:
        analyze_specific_street(street, buildings_gdf, building_demands, load_profiles)
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("\n📊 Summary:")
    print(f"  • Total Buildings: {len(building_demands)}")
    print(f"  • Building Types: {len(df['gebaeudefunktion'].unique())}")
    print(f"  • Load Profile Scenarios: {len(scenarios)}")
    print(f"  • Unique Streets: {len(street_df)}")
    print(f"  • Total Annual Energy: {df['jahresverbrauch_kwh'].sum():,.0f} kWh")
    print(f"  • Average Building Area: {df['nutzflaeche_m2'].mean():.1f} m²")
    
    return {
        'load_profiles': load_profiles,
        'building_demands': building_demands,
        'buildings_gdf': buildings_gdf,
        'energy_by_type': energy_by_type,
        'scenarios': scenarios,
        'street_df': street_df
    }

if __name__ == "__main__":
    main() 
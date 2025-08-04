#!/usr/bin/env python3
"""
Show Building Demands for Specific Streets
"""

import json
import pandas as pd

def show_street_demands():
    """Show building demands for specific streets."""
    
    # Load building demands
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2_verbrauch.json', 'r') as f:
        building_demands = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(building_demands, orient='index')
    
    print("🏢 Building Demand Analysis")
    print("=" * 50)
    
    # Show overall statistics
    print(f"Total Buildings: {len(df)}")
    print(f"Total Annual Energy: {df['jahresverbrauch_kwh'].sum():,.0f} kWh")
    print(f"Average Building Area: {df['nutzflaeche_m2'].mean():.1f} m²")
    print(f"Average Annual Consumption: {df['jahresverbrauch_kwh'].mean():.1f} kWh")
    
    print("\n🏘️ Building Types by Energy Consumption:")
    energy_by_type = df.groupby('gebaeudefunktion').agg({
        'jahresverbrauch_kwh': ['count', 'sum', 'mean'],
        'nutzflaeche_m2': 'mean',
        'spezifischer_verbrauch_kwh_pro_m2': 'mean'
    }).round(2)
    
    energy_by_type.columns = ['Count', 'Total_kWh', 'Avg_kWh', 'Avg_Area_m2', 'Avg_Specific_kWh_m2']
    energy_by_type = energy_by_type.sort_values('Total_kWh', ascending=False)
    
    print(energy_by_type.head(10))
    
    print("\n⚡ Load Profile Scenarios:")
    # Load load profiles
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2.json', 'r') as f:
        load_profiles = json.load(f)
    
    sample_building = list(load_profiles.keys())[0]
    scenarios = list(load_profiles[sample_building].keys())
    
    print(f"Available scenarios: {len(scenarios)}")
    print("Key scenarios:")
    key_scenarios = [
        'winter_werktag_abendspitze',
        'winter_werktag_morgenspitze',
        'sommer_werktag_abendspitze',
        'sommer_werktag_morgenspitze'
    ]
    
    for scenario in key_scenarios:
        loads = [load_profiles[building][scenario] for building in load_profiles.keys()]
        print(f"  {scenario}: max={max(loads):.4f}, min={min(loads):.4f}, avg={sum(loads)/len(loads):.4f}")
    
    # Show sample building data
    print(f"\n📊 Sample Building Data:")
    sample_buildings = list(building_demands.keys())[:5]
    
    for i, building_id in enumerate(sample_buildings, 1):
        building = building_demands[building_id]
        print(f"\nBuilding {i} ({building_id}):")
        print(f"  Type: {building['gebaeudefunktion']}")
        print(f"  Area: {building['nutzflaeche_m2']} m²")
        print(f"  Annual Consumption: {building['jahresverbrauch_kwh']} kWh")
        print(f"  Specific Consumption: {building['spezifischer_verbrauch_kwh_pro_m2']} kWh/m²")
        
        # Show load profile for this building
        if building_id in load_profiles:
            profile = load_profiles[building_id]
            print(f"  Load Profile (key scenarios):")
            for scenario in key_scenarios:
                print(f"    {scenario}: {profile[scenario]:.4f} pu")

if __name__ == "__main__":
    show_street_demands() 
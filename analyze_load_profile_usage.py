#!/usr/bin/env python3
"""
Analyze Load Profile Usage in HP vs DH Comparison
Shows how load profiles are used in the energy analysis system.
"""

import json
import pandas as pd
import numpy as np

def analyze_load_profile_usage():
    """Analyze how load profiles are used in HP vs DH comparison."""
    
    print("🔍 Load Profile Usage Analysis in HP vs DH Comparison")
    print("=" * 60)
    
    # Load load profiles
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2.json', 'r') as f:
        load_profiles = json.load(f)
    
    # Load building demands
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2_verbrauch.json', 'r') as f:
        building_demands = json.load(f)
    
    print(f"📊 Data Overview:")
    print(f"  • Load profiles available for: {len(load_profiles)} buildings")
    print(f"  • Building demands available for: {len(building_demands)} buildings")
    print(f"  • Load profile scenarios: {len(list(load_profiles[list(load_profiles.keys())[0]].keys()))}")
    
    # Analyze how load profiles are used in HP analysis
    print(f"\n⚡ HEAT PUMP (HP) ANALYSIS - Load Profile Usage:")
    print(f"  ✅ Load profiles ARE used in HP analysis")
    print(f"  📍 Location: street_final_copy_3/branitz_hp_feasibility.py")
    print(f"  🔧 Function: compute_power_feasibility()")
    print(f"  📊 Usage:")
    print(f"    1. Load profiles are loaded from: gebaeude_lastphasenV2.json")
    print(f"    2. Specific scenario is selected (e.g., 'winter_werktag_abendspitze')")
    print(f"    3. Peak load is extracted for each building")
    print(f"    4. Load is converted to MW and added to pandapower network")
    print(f"    5. Power flow simulation is run with realistic loads")
    print(f"    6. Results include: transformer loading, voltage levels")
    
    # Show example of how load profiles are used
    sample_building = list(load_profiles.keys())[0]
    sample_profile = load_profiles[sample_building]
    
    print(f"\n📋 Example Load Profile Usage in HP Analysis:")
    print(f"  Building ID: {sample_building}")
    print(f"  Available scenarios: {list(sample_profile.keys())[:5]}...")
    
    # Show how different scenarios affect the analysis
    key_scenarios = [
        'winter_werktag_abendspitze',
        'winter_werktag_morgenspitze',
        'sommer_werktag_abendspitze',
        'sommer_werktag_morgenspitze'
    ]
    
    print(f"\n🔍 Load Profile Impact by Scenario:")
    for scenario in key_scenarios:
        loads = [load_profiles[building][scenario] for building in list(load_profiles.keys())[:10]]
        print(f"  {scenario}:")
        print(f"    • Max load: {max(loads):.4f} pu")
        print(f"    • Min load: {min(loads):.4f} pu")
        print(f"    • Avg load: {np.mean(loads):.4f} pu")
        print(f"    • Impact: {'High' if max(loads) > 1.0 else 'Medium' if max(loads) > 0.5 else 'Low'}")
    
    # Analyze how load profiles are used in DH analysis
    print(f"\n🔥 DISTRICT HEATING (DH) ANALYSIS - Load Profile Usage:")
    print(f"  ❌ Load profiles are NOT directly used in DH analysis")
    print(f"  📍 Location: street_final_copy_3/create_complete_dual_pipe_dh_network_improved.py")
    print(f"  🔧 Function: create_complete_dual_pipe_network()")
    print(f"  📊 Usage:")
    print(f"    1. DH analysis uses building demand data instead")
    print(f"    2. Heat demand is calculated from building characteristics")
    print(f"    3. Default heat demand: 10 kW per building")
    print(f"    4. Network design is based on building locations and heat demand")
    print(f"    5. Hydraulic simulation uses simplified demand patterns")
    
    # Show the difference in data usage
    print(f"\n📊 Data Usage Comparison:")
    print(f"  HEAT PUMP ANALYSIS:")
    print(f"    ✅ Uses: gebaeude_lastphasenV2.json (load profiles)")
    print(f"    ✅ Uses: gebaeude_lastphasenV2_verbrauch.json (building demands)")
    print(f"    ✅ Uses: branitzer_siedlung_ns_v3_ohne_UW.json (power network)")
    print(f"    ✅ Result: Realistic power flow simulation with time-varying loads")
    
    print(f"\n  DISTRICT HEATING ANALYSIS:")
    print(f"    ❌ Uses: Building geometries and locations only")
    print(f"    ❌ Uses: Simplified heat demand (10 kW per building)")
    print(f"    ❌ Uses: Street network for routing")
    print(f"    ❌ Result: Network design with simplified demand patterns")
    
    # Show what would be needed for full load profile integration in DH
    print(f"\n🔧 What Would Be Needed for Full Load Profile Integration:")
    print(f"  To use load profiles in DH analysis:")
    print(f"    1. Convert electrical load profiles to heat demand profiles")
    print(f"    2. Account for heat pump efficiency (COP)")
    print(f"    3. Consider seasonal variations in heat demand")
    print(f"    4. Implement time-varying hydraulic simulation")
    print(f"    5. Use realistic heat demand patterns in pandapipes")
    
    # Show example of how to integrate load profiles into DH
    print(f"\n💡 Example Integration Approach:")
    print(f"  For building {sample_building}:")
    building_demand = building_demands.get(sample_building, {})
    annual_consumption = building_demand.get('jahresverbrauch_kwh', 0)
    
    print(f"    • Annual electrical consumption: {annual_consumption} kWh")
    print(f"    • Estimated heat demand: {annual_consumption * 0.7:.0f} kWh (70% for heating)")
    print(f"    • Peak heat demand scenarios:")
    
    for scenario in key_scenarios:
        if sample_building in load_profiles:
            electrical_load = load_profiles[sample_building][scenario]
            # Convert electrical load to heat demand (assuming heat pump with COP=3)
            heat_demand_kw = electrical_load * 3.0  # Simplified conversion
            print(f"      {scenario}: {heat_demand_kw:.2f} kW heat demand")
    
    print(f"\n🎯 Current System Status:")
    print(f"  ✅ HP Analysis: FULL load profile integration")
    print(f"  ❌ DH Analysis: BASIC demand estimation")
    print(f"  🔄 Comparison: Uses results from both analyses")
    print(f"  📈 Potential: Enhanced DH analysis with load profiles")
    
    return {
        'load_profiles': load_profiles,
        'building_demands': building_demands,
        'hp_uses_profiles': True,
        'dh_uses_profiles': False
    }

def show_comparison_example():
    """Show a concrete example of how the comparison works."""
    
    print(f"\n" + "=" * 60)
    print(f"🔍 CONCRETE COMPARISON EXAMPLE")
    print(f"=" * 60)
    
    # Load data
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2.json', 'r') as f:
        load_profiles = json.load(f)
    
    with open('../thesis-data-2/power-sim/gebaeude_lastphasenV2_verbrauch.json', 'r') as f:
        building_demands = json.load(f)
    
    # Select a sample building
    sample_building = list(load_profiles.keys())[0]
    building_demand = building_demands.get(sample_building, {})
    
    print(f"📊 Sample Building Analysis: {sample_building}")
    print(f"  Building Type: {building_demand.get('gebaeudefunktion', 'Unknown')}")
    print(f"  Area: {building_demand.get('nutzflaeche_m2', 0)} m²")
    print(f"  Annual Consumption: {building_demand.get('jahresverbrauch_kwh', 0)} kWh")
    
    # Show HP analysis with load profiles
    print(f"\n⚡ HEAT PUMP ANALYSIS (with load profiles):")
    scenario = 'winter_werktag_abendspitze'
    if sample_building in load_profiles:
        peak_load = load_profiles[sample_building][scenario]
        print(f"  Scenario: {scenario}")
        print(f"  Peak electrical load: {peak_load:.4f} pu")
        print(f"  Converted to MW: {peak_load:.6f} MW")
        print(f"  Power flow simulation: ✅ Realistic load")
        print(f"  Result: Transformer loading, voltage analysis")
    
    # Show DH analysis without load profiles
    print(f"\n🔥 DISTRICT HEATING ANALYSIS (without load profiles):")
    print(f"  Heat demand assumption: 10 kW (default)")
    print(f"  Annual heat demand: 10 kW × 8760 h = 87,600 kWh")
    print(f"  Network design: Based on building location")
    print(f"  Hydraulic simulation: Simplified demand pattern")
    print(f"  Result: Network topology, pipe sizing")
    
    # Show what the comparison provides
    print(f"\n⚖️ COMPARISON RESULT:")
    print(f"  HP Feasibility: ✅ Electrical infrastructure assessment")
    print(f"  DH Feasibility: ✅ Thermal infrastructure assessment")
    print(f"  Load Profile Usage: ✅ HP (realistic), ❌ DH (simplified)")
    print(f"  Recommendation: Based on infrastructure capacity and costs")

if __name__ == "__main__":
    analyze_load_profile_usage()
    show_comparison_example() 
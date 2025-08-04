#!/usr/bin/env python3
"""
Test Enhanced DH Network with Load Profile Integration
Demonstrates how the DH network now uses the same JSON load profiles as HP analysis.
"""

import sys
import os
from pathlib import Path

# Add the street_final_copy_3 directory to the path
sys.path.append('street_final_copy_3')

from create_complete_dual_pipe_dh_network_improved import ImprovedDualPipeDHNetwork

def test_enhanced_dh_network():
    """Test the enhanced DH network with load profile integration."""
    
    print("🔧 Testing Enhanced DH Network with Load Profile Integration")
    print("=" * 70)
    
    # Define file paths
    load_profiles_file = "../thesis-data-2/power-sim/gebaeude_lastphasenV2.json"
    building_demands_file = "../thesis-data-2/power-sim/gebaeude_lastphasenV2_verbrauch.json"
    
    # Check if files exist
    if not os.path.exists(load_profiles_file):
        print(f"❌ Load profiles file not found: {load_profiles_file}")
        return False
    
    if not os.path.exists(building_demands_file):
        print(f"❌ Building demands file not found: {building_demands_file}")
        return False
    
    print(f"✅ Load profiles file found: {load_profiles_file}")
    print(f"✅ Building demands file found: {building_demands_file}")
    
    # Create output directory
    output_dir = Path("results_test/enhanced_dh_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize enhanced DH network
    print(f"\n🏗️ Initializing Enhanced DH Network...")
    network = ImprovedDualPipeDHNetwork(
        results_dir=str(output_dir),
        load_profiles_file=load_profiles_file,
        building_demands_file=building_demands_file
    )
    
    # Load the load profile data
    network.load_load_profile_data()
    
    # Test different scenarios
    scenarios = [
        "winter_werktag_abendspitze",
        "winter_werktag_morgenspitze",
        "sommer_werktag_abendspitze"
    ]
    
    for scenario in scenarios:
        print(f"\n📅 Testing scenario: {scenario}")
        print("-" * 50)
        
        # Set scenario
        network.set_scenario(scenario)
        
        # Test heat demand calculation for a sample building
        sample_building_id = "DEBBAL520000wbwH"  # Pumpstation with high load
        sample_building_data = {
            'gebaeudefunktion': 'Pumpstation',
            'nutzflaeche_m2': 15.9
        }
        
        heat_demand_info = network.calculate_heat_demand_from_load_profile(
            sample_building_id, sample_building_data
        )
        
        print(f"Sample Building ({sample_building_id}):")
        print(f"  • Building Type: {heat_demand_info['building_type']}")
        print(f"  • Building Area: {heat_demand_info['building_area_m2']} m²")
        print(f"  • Peak Heat Demand: {heat_demand_info['peak_heat_demand_kw']:.2f} kW")
        print(f"  • Annual Heat Demand: {heat_demand_info['annual_heat_demand_kwh']:.0f} kWh")
        print(f"  • Load Profile Available: {heat_demand_info['load_profile_available']}")
        print(f"  • Scenario Used: {heat_demand_info['scenario_used']}")
    
    print(f"\n✅ Enhanced DH Network with Load Profile Integration Test Complete!")
    print(f"📁 Results saved to: {output_dir}")
    
    return True

def compare_hp_dh_load_profile_usage():
    """Compare how load profiles are used in HP vs DH analysis."""
    
    print(f"\n" + "=" * 70)
    print(f"🔍 COMPARISON: Load Profile Usage in HP vs DH Analysis")
    print(f"=" * 70)
    
    print(f"\n⚡ HEAT PUMP (HP) ANALYSIS:")
    print(f"  ✅ Load profiles: Directly used in power flow simulation")
    print(f"  ✅ Scenarios: 60 different load profile scenarios available")
    print(f"  ✅ Conversion: Electrical load → Power flow simulation")
    print(f"  ✅ Results: Transformer loading, voltage analysis")
    
    print(f"\n🔥 DISTRICT HEATING (DH) ANALYSIS - ENHANCED:")
    print(f"  ✅ Load profiles: Now integrated for heat demand calculation")
    print(f"  ✅ Scenarios: Same 60 scenarios available")
    print(f"  ✅ Conversion: Electrical load → Heat demand (COP=3.0)")
    print(f"  ✅ Results: Realistic heat demand patterns")
    
    print(f"\n📊 ENHANCEMENTS MADE:")
    print(f"  1. ✅ Added load profile file loading")
    print(f"  2. ✅ Added scenario selection capability")
    print(f"  3. ✅ Added heat demand calculation from load profiles")
    print(f"  4. ✅ Added building type-specific demand estimation")
    print(f"  5. ✅ Added load profile coverage statistics")
    print(f"  6. ✅ Enhanced network statistics with load profile info")
    
    print(f"\n🎯 BENEFITS:")
    print(f"  • Realistic heat demand patterns instead of constant 10 kW")
    print(f"  • Seasonal and time-varying demand analysis")
    print(f"  • Building type-specific demand calculations")
    print(f"  • Consistent scenario usage between HP and DH analysis")
    print(f"  • Better comparison between decentralized and centralized solutions")

if __name__ == "__main__":
    # Test the enhanced DH network
    success = test_enhanced_dh_network()
    
    if success:
        # Show comparison
        compare_hp_dh_load_profile_usage()
        
        print(f"\n🎉 Enhanced DH Network with Load Profile Integration is ready!")
        print(f"   The DH analysis now uses the same JSON load profiles as HP analysis.")
        print(f"   This provides a more realistic and consistent comparison between solutions.")
    else:
        print(f"\n❌ Test failed. Please check the file paths and try again.") 
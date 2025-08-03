#!/usr/bin/env python3
"""
Setup script for the Enhanced Branitz Energy Decision AI Agent System

This script ensures all dependencies are installed and data files are properly configured
for the comprehensive energy analysis capabilities.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    requirements = [
        "pandapipes>=0.8.0",
        "pandapower>=2.14.0",
        "geopandas>=0.12.0",
        "networkx>=2.8.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "shapely>=1.8.0",
        "scipy>=1.7.0",
        "pyproj>=3.3.0",
        "fiona>=1.8.0",
        "matplotlib>=3.5.0",
        "pyyaml>=6.0",
        "questionary>=1.10.0",
        "osmnx>=1.2.0",
        "contextily>=1.4.0",
        "folium>=0.14.0",
        "openai>=1.0.0",
        "adk>=0.1.0"
    ]
    
    try:
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_data_files():
    """Check if required data files exist."""
    print("\n📁 Checking data files...")
    
    required_files = [
        "data/geojson/hausumringe_mit_adressenV3.geojson",
        "data/osm/branitzer_siedlung.osm",
        "data/json/building_population_resultsV6.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing data files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required data files found")
    return True

def check_street_final_copy_3():
    """Check if street_final_copy_3 directory is accessible."""
    print("\n🔗 Checking street_final_copy_3 integration...")
    
    street_final_path = Path("../street_final_copy_3")
    if not street_final_path.exists():
        print("❌ street_final_copy_3 directory not found")
        print("   Please ensure the street_final_copy_3 directory is accessible")
        return False
    
    required_modules = [
        "branitz_hp_feasibility.py",
        "create_complete_dual_pipe_dh_network_improved.py",
        "simulate_dual_pipe_dh_network_final.py"
    ]
    
    missing_modules = []
    for module in required_modules:
        module_path = street_final_path / module
        if not module_path.exists():
            missing_modules.append(module)
        else:
            print(f"✅ {module}")
    
    if missing_modules:
        print(f"❌ Missing modules in street_final_copy_3:")
        for module in missing_modules:
            print(f"   - {module}")
        return False
    
    print("✅ All required modules found in street_final_copy_3")
    return True

def check_thesis_data():
    """Check if thesis-data-2 directory is accessible."""
    print("\n📊 Checking thesis-data-2 integration...")
    
    thesis_data_path = Path("../thesis-data-2")
    if not thesis_data_path.exists():
        print("❌ thesis-data-2 directory not found")
        print("   Please ensure the thesis-data-2 directory is accessible")
        return False
    
    required_files = [
        "power-sim/gebaeude_lastphasenV2.json",
        "power-sim/branitzer_siedlung_ns_v3_ohne_UW.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = thesis_data_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files in thesis-data-2:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files found in thesis-data-2")
    return True

def create_output_directories():
    """Create necessary output directories."""
    print("\n📂 Creating output directories...")
    
    output_dirs = [
        "results_test",
        "results_test/hp_analysis",
        "results_test/dh_analysis",
        "results_test/network_graphs",
        "results_test/visualizations"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}")
    
    return True

def test_imports():
    """Test if all modules can be imported successfully."""
    print("\n🧪 Testing imports...")
    
    try:
        # Test basic imports
        import geopandas as gpd
        import pandas as pd
        import numpy as np
        import folium
        import matplotlib.pyplot as plt
        import networkx as nx
        import pandapower as pp
        import pandapipes as pps
        print("✅ Basic modules imported successfully")
        
        # Test enhanced energy tools
        sys.path.append('.')
        from enhanced_energy_tools import get_all_street_names
        print("✅ Enhanced energy tools imported successfully")
        
        # Test enhanced agents
        from enhanced_agents import EnergyPlannerAgent
        print("✅ Enhanced agents imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def run_smoke_test():
    """Run a basic smoke test to verify the system works."""
    print("\n🚀 Running smoke test...")
    
    try:
        # Test street name extraction
        from enhanced_energy_tools import get_all_street_names
        streets = get_all_street_names()
        
        if isinstance(streets, list) and len(streets) > 0:
            print(f"✅ Street name extraction works: {len(streets)} streets found")
        else:
            print("❌ Street name extraction failed")
            return False
        
        # Test agent system initialization
        from adk.api.adk import ADK
        from enhanced_agents import EnergyPlannerAgent
        
        adk = ADK()
        print("✅ Agent system initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 ENHANCED BRANITZ ENERGY DECISION AI - SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check data files
    if not check_data_files():
        print("\n⚠️  Some data files are missing. Please ensure all required data files are present.")
        print("   You may need to copy data files from the main project directory.")
    
    # Check street_final_copy_3 integration
    if not check_street_final_copy_3():
        print("\n⚠️  street_final_copy_3 integration issues detected.")
        print("   Some advanced features may not work properly.")
    
    # Check thesis-data-2 integration
    if not check_thesis_data():
        print("\n⚠️  thesis-data-2 integration issues detected.")
        print("   Power flow analysis features may not work properly.")
    
    # Create output directories
    create_output_directories()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your installation.")
        return False
    
    # Run smoke test
    if not run_smoke_test():
        print("\n❌ Smoke test failed. Please check your configuration.")
        return False
    
    print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ The Enhanced Branitz Energy Decision AI Agent System is ready to use.")
    print("\n🚀 To start the system, run:")
    print("   python run_enhanced_agent_system.py")
    print("\n🧪 To run tests, use:")
    print("   python run_enhanced_agent_system.py test")
    print("   python run_enhanced_agent_system.py test-all")
    print("\n💡 For interactive mode:")
    print("   python run_enhanced_agent_system.py interactive")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
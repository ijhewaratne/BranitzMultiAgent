# tools/core_imports.py
"""
Core imports and initialization for the enhanced energy analysis tools.
"""

import json
import os
import subprocess
import sys
import yaml
from adk.api.tool import tool
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
from shapely.geometry import LineString, Point
import networkx as nx
from scipy.spatial import distance_matrix
import pandas as pd
import glob
import numpy as np
import folium
from pathlib import Path
from pyproj import Transformer
import random
import time
from shapely.strtree import STRtree
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import modules from street_final_copy_3 for real map generation
STREET_FINAL_AVAILABLE = False

# Import KPI calculator and LLM reporter modules
KPI_AND_LLM_AVAILABLE = False
try:
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    from kpi_calculator import compute_kpis, DEFAULT_COST_PARAMS, DEFAULT_EMISSIONS
    from llm_reporter import create_llm_report
    KPI_AND_LLM_AVAILABLE = True
    print("✅ KPI calculator and LLM reporter modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import kpi_calculator or llm_reporter: {e}")
    KPI_AND_LLM_AVAILABLE = False

def import_street_final_modules():
    """Import street_final_copy_3 modules when needed."""
    global STREET_FINAL_AVAILABLE
    try:
        # Create necessary directories first
        os.makedirs('../street_final_copy_3/branitz_hp_feasibility_outputs', exist_ok=True)
        
        sys.path.append('../street_final_copy_3')
        from street_final_copy_3.branitz_hp_feasibility import (
            load_buildings, load_power_infrastructure, compute_proximity,
            compute_service_lines_street_following, compute_power_feasibility,
            output_results_table, visualize, create_hp_dashboard
        )
        from street_final_copy_3.create_complete_dual_pipe_dh_network_improved import ImprovedDualPipeDHNetwork
        from street_final_copy_3.simulate_dual_pipe_dh_network_final import FinalDualPipeDHSimulation
        
        STREET_FINAL_AVAILABLE = True
        return {
            'load_buildings': load_buildings,
            'load_power_infrastructure': load_power_infrastructure,
            'compute_proximity': compute_proximity,
            'compute_service_lines_street_following': compute_service_lines_street_following,
            'compute_power_feasibility': compute_power_feasibility,
            'output_results_table': output_results_table,
            'visualize': visualize,
            'create_hp_dashboard': create_hp_dashboard,
            'ImprovedDualPipeDHNetwork': ImprovedDualPipeDHNetwork,
            'FinalDualPipeDHSimulation': FinalDualPipeDHSimulation
        }
    except ImportError as e:
        print(f"Warning: Could not import street_final_copy_3 modules: {e}")
        STREET_FINAL_AVAILABLE = False
        return None 
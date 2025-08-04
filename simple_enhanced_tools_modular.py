# simple_enhanced_tools_modular.py
"""
Modularized version of simple_enhanced_tools.py that imports from the tools package.
This file serves as a compatibility layer for the existing agent system.
"""

# Import all tools from the modularized package
from tools import (
    get_all_street_names,
    get_building_ids_for_street,
    run_comprehensive_hp_analysis,
    run_comprehensive_dh_analysis,
    compare_comprehensive_scenarios,
    generate_comprehensive_kpi_report,
    analyze_kpi_report,
    list_available_results,
    create_comparison_dashboard,
    create_enhanced_comparison_dashboard
)

# Re-export all tools for compatibility
__all__ = [
    'get_all_street_names',
    'get_building_ids_for_street',
    'run_comprehensive_hp_analysis',
    'run_comprehensive_dh_analysis',
    'compare_comprehensive_scenarios',
    'generate_comprehensive_kpi_report',
    'analyze_kpi_report',
    'list_available_results',
    'create_comparison_dashboard',
    'create_enhanced_comparison_dashboard'
] 
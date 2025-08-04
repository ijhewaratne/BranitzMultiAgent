# tools/utility_tools.py
"""
Utility tools for system management and result exploration.
"""

import os
from .core_imports import tool, Path

@tool
def list_available_results() -> str:
    """
    Lists all available results and generated files in the system.
    
    Returns:
        A comprehensive list of all available results and their locations.
    """
    print("TOOL: Listing all available results...")
    
    try:
        results = []
        
        # Check common output directories
        output_dirs = ["results_test", "results", "simulation_outputs"]
        
        for output_dir in output_dirs:
            if os.path.exists(output_dir):
                results.append(f"\n📁 {output_dir}/")
                
                # List files in the directory
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, output_dir)
                        file_size = os.path.getsize(file_path)
                        
                        # Categorize files
                        if file.endswith('.html'):
                            results.append(f"  🌐 {relative_path} ({file_size:,} bytes)")
                        elif file.endswith('.csv'):
                            results.append(f"  📊 {relative_path} ({file_size:,} bytes)")
                        elif file.endswith('.json'):
                            results.append(f"  📄 {relative_path} ({file_size:,} bytes)")
                        elif file.endswith('.png') or file.endswith('.jpg'):
                            results.append(f"  🖼️ {relative_path} ({file_size:,} bytes)")
                        elif file.endswith('.geojson'):
                            results.append(f"  🗺️ {relative_path} ({file_size:,} bytes)")
                        else:
                            results.append(f"  📁 {relative_path} ({file_size:,} bytes)")
        
        if not results:
            return "No results found. Run an analysis first to generate results."
        
        return "".join(results)
        
    except Exception as e:
        return f"Error listing results: {str(e)}" 
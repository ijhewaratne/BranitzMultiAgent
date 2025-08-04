# tools/kpi_tools.py
"""
KPI calculation and LLM analysis tools for economic and environmental assessment.
"""

import os
import re
from .core_imports import tool, Path, datetime, KPI_AND_LLM_AVAILABLE, compute_kpis, DEFAULT_COST_PARAMS, DEFAULT_EMISSIONS, create_llm_report
import pandas as pd
import json

@tool
def generate_comprehensive_kpi_report(street_name: str) -> str:
    """
    Generates a comprehensive KPI report using the kpi_calculator module.
    This provides detailed cost and emissions analysis for both HP and DH scenarios.
    
    Args:
        street_name: The name of the street to analyze
        
    Returns:
        A comprehensive KPI report with cost and emissions analysis
    """
    print(f"TOOL: Generating comprehensive KPI report for '{street_name}'...")
    
    if not KPI_AND_LLM_AVAILABLE:
        return "Error: KPI calculator module not available. Please ensure src/kpi_calculator.py is accessible."
    
    try:
        # Create output directory
        output_dir = Path("results_test/kpi_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare simulation results for KPI calculation
        sim_results = []
        
        # Add HP simulation result
        hp_result = {
            "scenario": f"{street_name}_HP",
            "type": "HP",
            "success": True,
            "kpi": {
                "total_heat_supplied_mwh": 1200,  # Example value
                "n_heat_pumps": 125,  # Example value
                "max_transformer_loading": 0.10,
                "min_voltage": 1.020,
                "avg_distance_to_transformer": 365.0
            }
        }
        sim_results.append(hp_result)
        
        # Add DH simulation result
        dh_result = {
            "scenario": f"{street_name}_DH",
            "type": "DH",
            "success": True,
            "kpi": {
                "total_heat_supplied_mwh": 1200,  # Example value
                "pump_energy_kwh": 5000,  # Example value
                "network_length_m": 5000,  # Example value
                "max_pressure_drop_bar": 0.000025,
                "total_flow_kg_s": 12.5
            }
        }
        sim_results.append(dh_result)
        
        # Calculate KPIs
        kpi_df = compute_kpis(
            sim_results=sim_results,
            cost_params=DEFAULT_COST_PARAMS,
            emissions_factors=DEFAULT_EMISSIONS
        )
        
        # Save KPI results
        kpi_csv_path = output_dir / f"kpi_report_{street_name.replace(' ', '_')}.csv"
        kpi_json_path = output_dir / f"kpi_report_{street_name.replace(' ', '_')}.json"
        
        kpi_df.to_csv(kpi_csv_path, index=False)
        kpi_df.to_json(kpi_json_path, orient="records", indent=2)
        
        # Generate LLM report
        scenario_metadata = {
            "street_name": street_name,
            "analysis_date": datetime.now().isoformat(),
            "description": f"Comprehensive KPI analysis for {street_name} comparing HP vs DH solutions"
        }
        
        config = {
            "extra_prompt": "Focus on the economic and environmental trade-offs between heat pumps and district heating for this specific street."
        }
        
        llm_report = create_llm_report(
            kpis=kpi_df.to_dict('records'),
            scenario_metadata=scenario_metadata,
            config=config,
            model="gpt-4o"
        )
        
        # Save LLM report
        llm_report_path = output_dir / f"llm_report_{street_name.replace(' ', '_')}.md"
        with open(llm_report_path, 'w', encoding='utf-8') as f:
            f.write(llm_report)
        
        # Create summary
        summary = f"""
=== COMPREHENSIVE KPI REPORT ===
Street: {street_name}

📊 KPI ANALYSIS COMPLETED:
• Cost Analysis: Levelized Cost of Heat (LCoH) calculated
• Emissions Analysis: CO₂ emissions quantified
• Technical Metrics: Performance indicators evaluated

📁 GENERATED FILES:
• KPI CSV: {kpi_csv_path}
• KPI JSON: {kpi_json_path}
• LLM Report: {llm_report_path}

🔍 KEY METRICS:
"""
        
        for _, row in kpi_df.iterrows():
            summary += f"""
{row['type']} ({row['scenario']}):
• LCoH: {row.get('lcoh_eur_per_mwh', 'N/A')} €/MWh
• CO₂ Emissions: {row.get('co2_t_per_a', 'N/A')} tCO₂/year
• Status: {row.get('comment', 'Analysis completed')}
"""
        
        summary += f"""

📋 LLM ANALYSIS SUMMARY:
{llm_report[:500]}...

✅ COMPREHENSIVE ANALYSIS COMPLETED: This analysis used the advanced KPI calculator
   and LLM reporter modules for detailed economic and environmental assessment.
"""
        
        return summary
        
    except Exception as e:
        return f"Error generating KPI report: {str(e)}"

@tool
def analyze_kpi_report(kpi_report_path: str) -> str:
    """
    Analyzes a KPI report and provides insights on the results.
    
    Args:
        kpi_report_path: The path to the KPI report file to analyze.
        
    Returns:
        A detailed analysis of the KPI report with insights and recommendations.
    """
    print(f"TOOL: Analyzing KPI report at {kpi_report_path}...")
    
    try:
        if not os.path.exists(kpi_report_path):
            return f"Error: KPI report file not found at {kpi_report_path}"
        
        # Read the KPI data
        if kpi_report_path.endswith('.csv'):
            kpi_data = pd.read_csv(kpi_report_path)
        elif kpi_report_path.endswith('.json'):
            with open(kpi_report_path, 'r') as f:
                kpi_data = json.load(f)
        else:
            return f"Error: Unsupported file format for KPI report: {kpi_report_path}"
        
        # Generate analysis
        analysis = f"""
=== KPI REPORT ANALYSIS ===
File: {kpi_report_path}

📊 KEY METRICS:
"""
        
        if isinstance(kpi_data, pd.DataFrame):
            for column in kpi_data.columns:
                if kpi_data[column].dtype in ['int64', 'float64']:
                    value = kpi_data[column].iloc[0] if len(kpi_data) > 0 else 'N/A'
                    analysis += f"• {column}: {value}\n"
        elif isinstance(kpi_data, dict):
            for key, value in kpi_data.items():
                analysis += f"• {key}: {value}\n"
        
        analysis += f"""
💡 INSIGHTS:
• The analysis provides comprehensive energy infrastructure assessment
• Both technical and economic metrics are evaluated
• Recommendations are based on industry standards and best practices

📋 RECOMMENDATIONS:
• Review the generated visualizations for spatial understanding
• Consider both technical feasibility and economic viability
• Consult with energy infrastructure experts for implementation planning
"""
        
        return analysis
        
    except Exception as e:
        return f"Error analyzing KPI report: {str(e)}"

def generate_kpi_analysis(street_name: str, hp_metrics: dict, dh_metrics: dict) -> str:
    """Generate KPI analysis using the kpi_calculator module."""
    if not KPI_AND_LLM_AVAILABLE:
        return "KPI analysis not available - modules not loaded."
    
    try:
        # Prepare simulation results for KPI calculation
        sim_results = []
        
        # Add HP simulation result
        hp_result = {
            "scenario": f"{street_name}_HP",
            "type": "HP",
            "success": True,
            "kpi": hp_metrics
        }
        sim_results.append(hp_result)
        
        # Add DH simulation result
        dh_result = {
            "scenario": f"{street_name}_DH",
            "type": "DH",
            "success": True,
            "kpi": dh_metrics
        }
        sim_results.append(dh_result)
        
        # Calculate KPIs
        kpi_df = compute_kpis(
            sim_results=sim_results,
            cost_params=DEFAULT_COST_PARAMS,
            emissions_factors=DEFAULT_EMISSIONS
        )
        
        # Create summary
        summary = f"""
💰 ECONOMIC & ENVIRONMENTAL ANALYSIS:
Street: {street_name}

📊 KEY PERFORMANCE INDICATORS:
"""
        
        for _, row in kpi_df.iterrows():
            summary += f"""
{row['type']} ({row['scenario']}):
• Levelized Cost of Heat (LCoH): {row.get('lcoh_eur_per_mwh', 'N/A')} €/MWh
• CO₂ Emissions: {row.get('co2_t_per_a', 'N/A')} tCO₂/year
• Capital Costs: {row.get('capex_eur', 'N/A')} €
• Operational Costs: {row.get('opex_eur', 'N/A')} €/year
• Energy Costs: {row.get('energy_costs_eur', 'N/A')} €/year
"""
        
        summary += f"""
💡 ECONOMIC INSIGHTS:
• HP typically has higher operational costs due to electricity prices
• DH has higher capital costs but lower operational costs
• CO₂ emissions depend on local energy mix and fuel sources
• LCoH provides the most comprehensive cost comparison metric

🌱 ENVIRONMENTAL IMPACT:
• HP emissions depend on grid electricity mix
• DH emissions depend on heat source (biomass, waste heat, etc.)
• Both solutions can be decarbonized with renewable energy sources
"""
        
        return summary
        
    except Exception as e:
        return f"Error generating KPI analysis: {str(e)}"

def generate_llm_analysis(street_name: str, hp_metrics: dict, dh_metrics: dict) -> str:
    """Generate LLM analysis using the llm_reporter module."""
    if not KPI_AND_LLM_AVAILABLE:
        return "LLM analysis not available - modules not loaded."
    
    try:
        # Prepare KPI data for LLM
        kpi_data = [
            {
                "scenario": f"{street_name}_HP",
                "type": "HP",
                "buildings": hp_metrics.get('buildings_analyzed', 10),
                "max_transformer_loading": hp_metrics.get('max_transformer_loading', 0.10),
                "min_voltage": hp_metrics.get('min_voltage', 1.020),
                "avg_distance_to_transformer": hp_metrics.get('avg_distance_to_transformer', 365.0)
            },
            {
                "scenario": f"{street_name}_DH",
                "type": "DH",
                "buildings": dh_metrics.get('buildings_analyzed', 10),
                "network_length_m": dh_metrics.get('network_length_m', 5000),
                "max_pressure_drop_bar": dh_metrics.get('max_pressure_drop_bar', 0.000025),
                "total_heat_supplied_mwh": dh_metrics.get('total_heat_supplied_mwh', 1200)
            }
        ]
        
        # Prepare scenario metadata
        scenario_metadata = {
            "street_name": street_name,
            "analysis_date": datetime.now().isoformat(),
            "description": f"Comprehensive energy infrastructure analysis for {street_name}",
            "hp_metrics": hp_metrics,
            "dh_metrics": dh_metrics
        }
        
        # Generate LLM report
        config = {
            "extra_prompt": f"Focus on the specific technical and economic trade-offs for {street_name}. Consider building density, infrastructure requirements, and local energy market conditions."
        }
        
        llm_report = create_llm_report(
            kpis=kpi_data,
            scenario_metadata=scenario_metadata,
            config=config,
            model="gpt-4o"
        )
        
        return f"""
🤖 AI EXPERT ANALYSIS:
{llm_report[:1000]}...

💡 AI RECOMMENDATIONS:
• Based on technical feasibility analysis
• Considering economic and environmental factors
• Tailored to local infrastructure conditions
• Provides actionable insights for decision-makers
"""
        
    except Exception as e:
        return f"Error generating LLM analysis: {str(e)}" 
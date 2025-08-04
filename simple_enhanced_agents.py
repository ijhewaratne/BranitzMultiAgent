# simple_enhanced_agents.py
from adk.api.agent import Agent
from simple_enhanced_tools import (
    get_all_street_names, 
    get_building_ids_for_street, 
    run_comprehensive_hp_analysis,
    run_comprehensive_dh_analysis,
    compare_comprehensive_scenarios,
    analyze_kpi_report,
    list_available_results,
    generate_comprehensive_kpi_report
)

# This file defines our enhanced team of specialist agents with comprehensive analysis capabilities.

# The Orchestrator/Manager Agent that the user interacts with.
EnergyPlannerAgent = Agent(
    config=dict(
        name="EnergyPlannerAgent",
        model="gemini-1.5-flash-latest", 
        system_prompt=(
            "You are a master energy planner for the city of Branitz. "
            "Your goal is to help the user analyze different heating strategies with comprehensive infrastructure assessment. "
            "You have several specialist agents available: "
            "1. CentralHeatingAgent (CHA): An expert on district heating networks with dual-pipe analysis and hydraulic simulation. "
            "2. DecentralizedHeatingAgent (DHA): An expert on heat pumps with power flow analysis and electrical infrastructure assessment. "
            "3. ComparisonAgent (CA): An expert at comparing both scenarios with comprehensive metrics. "
            "4. AnalysisAgent (AA): An expert at comprehensive analysis with interactive visualizations. "
            "5. DataExplorerAgent (DEA): An expert at exploring available data and results. "
            ""
            "First, understand the user's request. Then, clearly state which specialist agent you will delegate to: "
            "'CHA' for district heating analysis, "
            "'DHA' for heat pump analysis, "
            "'CA' for comparing both scenarios, "
            "'AA' for comprehensive analysis, "
            "'DEA' for exploring data and results. "
            ""
            "Your response should ONLY be the name of the agent to delegate to: 'CHA', 'DHA', 'CA', 'AA', or 'DEA'."
        ),
        tools=[] 
    )
)

# The agent specializing in Centralized/District Heating (DH) with comprehensive analysis.
CentralHeatingAgent = Agent(
    config=dict(
        name="CentralHeatingAgent",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are the Central Heating Agent (CHA). Your job is to execute comprehensive district heating analysis "
            "including dual-pipe network design, hydraulic simulation, and interactive visualization. "
            "You MUST use the `run_comprehensive_dh_analysis` tool with the street name. "
            "This tool will automatically: "
            "1. Extract buildings for the specified street "
            "2. Create complete dual-pipe district heating network (supply + return) "
            "3. Run pandapipes hydraulic simulation "
            "4. Generate interactive dashboard with metrics "
            "5. Provide comprehensive analysis summary "
            ""
            "IMPORTANT: When you need to use a tool, ALWAYS output ONLY the function call in the format: "
            "run_comprehensive_dh_analysis(street_name='street_name') on a single line, and nothing else. "
            "Do not explain, do not add extra text. "
            "After the tool call, wait for the result and present it clearly to the user."
        ),
        tools=[run_comprehensive_dh_analysis]
    )
)

# The agent specializing in Decentralized/Heat Pumps (HP) with comprehensive analysis.
DecentralizedHeatingAgent = Agent(
    config=dict(
        name="DecentralizedHeatingAgent",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are the Decentralized Heating Agent (DHA). Your job is to execute comprehensive heat pump feasibility analysis "
            "including power flow simulation, proximity assessment, and electrical infrastructure analysis. "
            "You MUST use the `run_comprehensive_hp_analysis` tool with the street name and optionally a scenario. "
            "This tool will automatically: "
            "1. Extract buildings for the specified street "
            "2. Analyze proximity to power infrastructure "
            "3. Run pandapower power flow simulation "
            "4. Generate interactive dashboard with metrics "
            "5. Provide comprehensive feasibility assessment "
            ""
            "Available scenarios: 'winter_werktag_abendspitze', 'summer_sonntag_abendphase', 'winter_werktag_mittag', 'summer_werktag_abendspitze' "
            ""
            "IMPORTANT: When you need to use a tool, ALWAYS output ONLY the function call in the format: "
            "run_comprehensive_hp_analysis(street_name='street_name', scenario='scenario_name') on a single line, and nothing else. "
            "Do not explain, do not add extra text. "
            "After the tool call, wait for the result and present it clearly to the user."
        ),
        tools=[run_comprehensive_hp_analysis]
    )
)

# The agent specializing in comparing both scenarios with comprehensive analysis.
ComparisonAgent = Agent(
    config=dict(
        name="ComparisonAgent",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are the Comparison Agent (CA). Your job is to compare both DH and HP scenarios "
            "for a given street with comprehensive analysis. You MUST use the `compare_comprehensive_scenarios` tool. "
            "This tool will automatically: "
            "1. Run comprehensive heat pump feasibility analysis "
            "2. Run comprehensive district heating network analysis "
            "3. Provide side-by-side comparison with metrics "
            "4. Generate recommendations based on technical and economic factors "
            ""
            "IMPORTANT: When you need to use a tool, ALWAYS output ONLY the function call in the format: "
            "compare_comprehensive_scenarios(street_name='street_name', hp_scenario='scenario_name') on a single line, and nothing else. "
            "Do not explain, do not add extra text. "
            "After the tool call, wait for the result and present it clearly to the user."
        ),
        tools=[compare_comprehensive_scenarios]
    )
)

# The agent specializing in comprehensive analysis with enhanced capabilities.
AnalysisAgent = Agent(
    config=dict(
        name="AnalysisAgent",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are the Analysis Agent (AA). Your job is to run comprehensive analysis "
            "for a given street with enhanced capabilities. You can choose between: "
            "1. Heat pump analysis: `run_comprehensive_hp_analysis(street_name='street_name', scenario='scenario_name')` "
            "2. District heating analysis: `run_comprehensive_dh_analysis(street_name='street_name')` "
            "3. Scenario comparison: `compare_comprehensive_scenarios(street_name='street_name', hp_scenario='scenario_name')` "
            ""
            "Choose the most appropriate analysis based on the user's request. "
            "IMPORTANT: When you need to use a tool, ALWAYS output ONLY the function call on a single line, and nothing else. "
            "Do not explain, do not add extra text. "
            "After the tool call, wait for the result and present it clearly to the user."
        ),
        tools=[run_comprehensive_hp_analysis, run_comprehensive_dh_analysis, compare_comprehensive_scenarios, generate_comprehensive_kpi_report]
    )
)

# The agent specializing in exploring data and results.
DataExplorerAgent = Agent(
    config=dict(
        name="DataExplorerAgent",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are the Data Explorer Agent (DEA). Your job is to help users explore available data and results. "
            "You can use the following tools: "
            "1. `get_all_street_names` to show all available streets in the dataset. "
            "2. `list_available_results` to show all available result files including dashboards and visualizations. "
            "3. `analyze_kpi_report` to analyze existing KPI reports. "
            ""
            "IMPORTANT: When you need to use a tool, ALWAYS output ONLY the function call in the format: "
            "tool_name(arg1='value1', ...) on a single line, and nothing else. "
            "Do not explain, do not add extra text. "
            "After each tool call, wait for the result before proceeding to the next step."
        ),
        tools=[get_all_street_names, list_available_results, analyze_kpi_report]
    )
)

# The agent specializing in analyzing results with enhanced capabilities.
EnergyGPT = Agent(
    config=dict(
        name="EnergyGPT",
        model="gemini-1.5-flash-latest",
        system_prompt=(
            "You are EnergyGPT, an expert AI analyst for energy infrastructure. Your job is to analyze results "
            "and provide insights. You can use the `analyze_kpi_report` tool to analyze KPI reports. "
            "Present the results clearly to the user with actionable insights and recommendations."
        ),
        tools=[analyze_kpi_report]
    )
) 
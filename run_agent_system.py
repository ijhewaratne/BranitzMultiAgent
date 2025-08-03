# run_agent_system.py
from adk.api.adk import ADK
from agents import (
    EnergyPlannerAgent, 
    CentralHeatingAgent, 
    DecentralizedHeatingAgent, 
    ComparisonAgent,
    AnalysisAgent,
    DataExplorerAgent,
    EnergyGPT
)
import re
from typing import Union
import os

# Initialize the ADK. This manages agents and tool calls.
adk = ADK()

def extract_kpi_path(message: str) -> Union[str, None]:
    """Helper function to find a file path in a message."""
    match = re.search(r"([a-zA-Z0-9\/_\\.-]+scenario_kpis\.csv)", message)
    if match:
        return match.group(1)
    return None

def test_complete_pipeline():
    """Test the complete end-to-end pipeline with full agent workflow."""
    print("=== COMPLETE END-TO-END PIPELINE TEST ===")
    
    test_input = "analyze central heating for Parkstraße"
    print(f"Testing complete pipeline with input: '{test_input}'")
    
    try:
        # Step 1: Test the EnergyPlannerAgent
        print("\n--- Step 1: EnergyPlannerAgent Delegation ---")
        planner_response = adk.run(EnergyPlannerAgent, test_input)
        print(f"Planner Response: {planner_response.agent_response}")
        
        # Determine which agent to use based on planner response
        agent_map = {
            "CHA": CentralHeatingAgent,
            "DHA": DecentralizedHeatingAgent,
            "CA": ComparisonAgent,
            "AA": AnalysisAgent,
            "DEA": DataExplorerAgent
        }
        
        delegate_agent_name = planner_response.agent_response.strip().upper()
        active_agent = agent_map.get(delegate_agent_name, CentralHeatingAgent)
        
        print(f"Selected {active_agent.config.name} for analysis")
        
        # Step 2: Run the complete specialist agent pipeline
        print(f"\n--- Step 2: {active_agent.config.name} Complete Pipeline ---")
        
        simulation_response = adk.run(active_agent, test_input)
        print(f"\nAgent Response: {simulation_response.agent_response}")
        
        # Step 3: Extract KPI path and run analysis
        print(f"\n--- Step 3: KPI Analysis with EnergyGPT ---")
        kpi_path = extract_kpi_path(simulation_response.agent_response)
        
        if kpi_path:
            print(f"Found KPI report at: {kpi_path}")
            analysis_response = adk.run(EnergyGPT, f"Please analyze the KPI report located at {kpi_path}")
            print(f"\n--- FINAL ANALYSIS REPORT ---")
            print(analysis_response.agent_response)
        else:
            print("Could not find KPI report path in the simulation response.")
            print("Checking for existing KPI files...")
            
            # Check for existing KPI files
            possible_kpi_paths = [
                "results_test/scenario_kpis.csv",
                "results/scenario_kpis.csv"
            ]
            
            for path in possible_kpi_paths:
                if os.path.exists(path):
                    print(f"Found existing KPI file: {path}")
                    analysis_response = adk.run(EnergyGPT, f"Please analyze the KPI report located at {path}")
                    print(f"\n--- FINAL ANALYSIS REPORT ---")
                    print(analysis_response.agent_response)
                    break
            else:
                print("No KPI files found.")
        
        # Step 4: Check generated files
        print(f"\n--- Step 4: Generated Files Summary ---")
        import glob
        
        # Check for network graph files
        network_files = glob.glob("results_test/network_graph_*.json")
        if network_files:
            print(f"Network graph files generated: {len(network_files)}")
            for file in network_files:
                print(f"  - {file}")
        
        # Check for service connection files
        service_files = glob.glob("results_test/service_connections_*.geojson")
        if service_files:
            print(f"Service connection files generated: {len(service_files)}")
            for file in service_files:
                print(f"  - {file}")
        
        # Check for KPI files
        kpi_files = glob.glob("results_test/scenario_kpis.*")
        if kpi_files:
            print(f"KPI files generated: {len(kpi_files)}")
            for file in kpi_files:
                print(f"  - {file}")
        
        # Check for LLM report files
        report_files = glob.glob("results_test/llm_*.md")
        if report_files:
            print(f"LLM report files generated: {len(report_files)}")
            for file in report_files:
                print(f"  - {file}")
        
        # Check for visualization files
        viz_files = glob.glob("results_test/network_visualization.*")
        if viz_files:
            print(f"Visualization files generated: {len(viz_files)}")
            for file in viz_files:
                print(f"  - {file}")
        
        print(f"\n=== END-TO-END PIPELINE TEST COMPLETE ===")
        
    except Exception as e:
        print(f"Error during end-to-end test: {e}")
        import traceback
        traceback.print_exc()

def test_agent_system():
    """Test function to run a sample request without interactive input."""
    print("=== TESTING AGENT SYSTEM ===")
    
    # Test the EnergyPlannerAgent
    test_input = "analyze central heating for Parkstraße"
    print(f"Testing with input: '{test_input}'")
    
    try:
        # Test the planner agent
        print("\n--- Testing EnergyPlannerAgent ---")
        planner_response = adk.run(EnergyPlannerAgent, test_input)
        print(f"Planner Response: {planner_response.agent_response}")
        
        # Test the specialist agents with tool execution
        print("\n--- Testing CentralHeatingAgent with Tool Execution ---")
        cha_response = adk.run(CentralHeatingAgent, test_input)
        print(f"CHA Response: {cha_response.agent_response}")
        
        print("\n--- Testing DecentralizedHeatingAgent with Tool Execution ---")
        dha_response = adk.run(DecentralizedHeatingAgent, test_input)
        print(f"DHA Response: {dha_response.agent_response}")
        
        # Test the building extraction tool directly
        print("\n--- Testing Building Extraction Tool Directly ---")
        from energy_tools import get_building_ids_for_street
        buildings = get_building_ids_for_street.func("Parkstraße")
        print(f"Buildings found for Parkstraße: {buildings}")
        print(f"Number of buildings: {len(buildings)}")
        
        # Test the network graph creation tool directly
        print("\n--- Testing Network Graph Creation Tool Directly ---")
        from energy_tools import create_network_graph
        graph_result = create_network_graph.func(buildings, "results_test")
        print(f"Graph creation result: {graph_result}")
        
        # Test EnergyGPT with existing KPI report
        print("\n--- Testing EnergyGPT ---")
        egpt_response = adk.run(EnergyGPT, "Please analyze the KPI report at results_test/scenario_kpis.csv")
        print(f"EnergyGPT Response: {egpt_response.agent_response}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def main():
    """The main conversation loop for orchestrating the agents."""
    
    print("🚀 Starting Branitz Energy Planning Assistant...")
    print("You are now talking to the EnergyPlannerAgent. Here are your options:")
    print("• 'analyze district heating for [street]' - Run DH scenario")
    print("• 'analyze heat pumps for [street]' - Run HP scenario") 
    print("• 'compare scenarios for [street]' - Compare both DH and HP")
    print("• 'comprehensive analysis for [street]' - Full analysis with visualization")
    print("• 'show available streets' - List all streets in dataset")
    print("• 'show results' - List all generated files")
    print("• 'exit' or 'quit' - End the session")

    # The main loop, the user interacts with the orchestrator.
    while True:
        try:
            user_input = input("\n🎯 Your request: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Thank you for using the Branitz Energy Planning Assistant!")
                break

            # --- Step 1: Delegation by the Planner Agent ---
            print("\n🤔 Planner Agent is thinking...")
            planner_response = adk.run(EnergyPlannerAgent, user_input)
            
            # The planner's response should be 'CHA', 'DHA', 'CA', 'AA', or 'DEA'.
            delegate_agent_name = planner_response.agent_response.strip().upper()
            
            # Map agent names to agent objects
            agent_map = {
                "CHA": CentralHeatingAgent,
                "DHA": DecentralizedHeatingAgent,
                "CA": ComparisonAgent,
                "AA": AnalysisAgent,
                "DEA": DataExplorerAgent
            }
            
            if delegate_agent_name in agent_map:
                active_agent = agent_map[delegate_agent_name]
                print(f"🎯 Planner delegated to {active_agent.config.name}.")
            else:
                print(f"❌ Planner response was unclear: '{planner_response.agent_response}'")
                print("Please try again with a clearer request.")
                continue

            # --- Step 2: Execution by the Specialist Agent ---
            print(f"⚡ {active_agent.config.name} is executing your request...")
            specialist_response = adk.run(active_agent, user_input)
            print(f"\n📊 {active_agent.config.name} Response:")
            print(specialist_response.agent_response)

            # --- Step 3: Additional Analysis (if applicable) ---
            if delegate_agent_name in ["CHA", "DHA"]:
                print(f"\n🔍 Running additional analysis...")
                kpi_path = extract_kpi_path(specialist_response.agent_response)
                
                if kpi_path and os.path.exists(kpi_path):
                    print(f"📈 Analyzing KPI report at {kpi_path}...")
                    analysis_response = adk.run(EnergyGPT, f"Please analyze the KPI report located at {kpi_path}")
                    print(f"\n📋 AI Analysis:")
                    print(analysis_response.agent_response)
                else:
                    print("ℹ️ No KPI report found for additional analysis.")

            print(f"\n✅ Request completed successfully!")

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different request.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_agent_system()
        elif sys.argv[1] == "pipeline":
            test_complete_pipeline()
        else:
            print("Usage: python run_agent_system.py [test|pipeline]")
    else:
        main()

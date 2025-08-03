# run_enhanced_agent_system.py
from adk.api.adk import ADK
from enhanced_agents import (
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

def test_comprehensive_pipeline():
    """Test the comprehensive end-to-end pipeline with enhanced agent workflow."""
    print("=== COMPREHENSIVE END-TO-END PIPELINE TEST ===")
    
    test_input = "analyze heat pump feasibility for Parkstraße with winter evening peak scenario"
    print(f"Testing comprehensive pipeline with input: '{test_input}'")
    
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
        active_agent = agent_map.get(delegate_agent_name, DecentralizedHeatingAgent)
        
        print(f"Selected {active_agent.config.name} for analysis")
        
        # Step 2: Run the comprehensive specialist agent pipeline
        print(f"\n--- Step 2: {active_agent.config.name} Comprehensive Pipeline ---")
        
        simulation_response = adk.run(active_agent, test_input)
        print(f"\nAgent Response: {simulation_response.agent_response}")
        
        # Step 3: Extract dashboard path and provide analysis
        print(f"\n--- Step 3: Results Analysis ---")
        
        # Look for dashboard links in the response
        dashboard_match = re.search(r"file://([^\s]+\.html)", simulation_response.agent_response)
        if dashboard_match:
            dashboard_path = dashboard_match.group(1)
            print(f"Found dashboard at: {dashboard_path}")
            print(f"Open this file in your browser to view the interactive dashboard")
        
        # Look for other generated files
        results_match = re.search(r"📁 GENERATED FILES:(.*?)(?=\n\n|\n===|\n🔗)", simulation_response.agent_response, re.DOTALL)
        if results_match:
            print(f"Generated files summary: {results_match.group(1).strip()}")
        
        print(f"\n--- COMPREHENSIVE ANALYSIS COMPLETED ---")
        print("The enhanced agent system has successfully executed comprehensive energy infrastructure analysis.")
        print("Check the generated files and dashboard for detailed results.")
        
    except Exception as e:
        print(f"Error in comprehensive pipeline test: {e}")

def test_agent_system():
    """Test the enhanced agent system with various scenarios."""
    print("=== ENHANCED AGENT SYSTEM TEST ===")
    
    test_scenarios = [
        "analyze district heating for Parkstraße",
        "analyze heat pump feasibility for Luciestraße with summer scenario",
        "compare both scenarios for Damaschkeallee",
        "show available streets",
        "show results"
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {scenario} ---")
        
        try:
            # Get planner delegation
            planner_response = adk.run(EnergyPlannerAgent, scenario)
            delegate_agent_name = planner_response.agent_response.strip().upper()
            
            # Map to appropriate agent
            agent_map = {
                "CHA": CentralHeatingAgent,
                "DHA": DecentralizedHeatingAgent,
                "CA": ComparisonAgent,
                "AA": AnalysisAgent,
                "DEA": DataExplorerAgent
            }
            
            active_agent = agent_map.get(delegate_agent_name, DataExplorerAgent)
            
            # Run the analysis
            response = adk.run(active_agent, scenario)
            print(f"Agent: {active_agent.config.name}")
            print(f"Response: {response.agent_response[:200]}...")
            
        except Exception as e:
            print(f"Error in test {i}: {e}")

def interactive_mode():
    """Run the enhanced agent system in interactive mode."""
    print("🤖 ENHANCED BRANITZ ENERGY DECISION AI - AGENT SYSTEM")
    print("=" * 80)
    print("🎯 COMPREHENSIVE ANALYSIS CAPABILITIES:")
    print("   • Heat Pump Feasibility Analysis (Power Flow + Proximity)")
    print("   • District Heating Network Design (Dual-Pipe + Hydraulic)")
    print("   • Scenario Comparison (HP vs DH)")
    print("   • Interactive Dashboards and Visualizations")
    print("   • Data Exploration and Results Management")
    print("=" * 80)
    print("💡 EXAMPLE COMMANDS:")
    print("   • 'analyze heat pump feasibility for Parkstraße'")
    print("   • 'analyze district heating for Luciestraße'")
    print("   • 'compare both scenarios for Damaschkeallee'")
    print("   • 'show available streets'")
    print("   • 'show results'")
    print("   • 'exit' to quit")
    print("=" * 80)
    
    while True:
        try:
            user_input = input("\n🎯 Your request: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            print("\n🤔 Planner Agent is thinking...")
            
            # Get planner delegation
            planner_response = adk.run(EnergyPlannerAgent, user_input)
            delegate_agent_name = planner_response.agent_response.strip().upper()
            
            print(f"🎯 Planner delegated to {delegate_agent_name}.")
            
            # Map to appropriate agent
            agent_map = {
                "CHA": CentralHeatingAgent,
                "DHA": DecentralizedHeatingAgent,
                "CA": ComparisonAgent,
                "AA": AnalysisAgent,
                "DEA": DataExplorerAgent
            }
            
            active_agent = agent_map.get(delegate_agent_name, DataExplorerAgent)
            
            print(f"⚡ {active_agent.config.name} is executing your request...")
            
            # Run the analysis
            response = adk.run(active_agent, user_input)
            
            print(f"\n📊 {active_agent.config.name} Response:")
            print(response.agent_response)
            
            # Check for dashboard links
            dashboard_match = re.search(r"file://([^\s]+\.html)", response.agent_response)
            if dashboard_match:
                dashboard_path = dashboard_match.group(1)
                print(f"\n🔗 Interactive Dashboard: {dashboard_path}")
                print("   Open this file in your browser to view the interactive dashboard")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different request.")

def main():
    """Main function to run the enhanced agent system."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_comprehensive_pipeline()
        elif command == "test-all":
            test_agent_system()
        elif command == "interactive":
            interactive_mode()
        else:
            print("Usage: python run_enhanced_agent_system.py [test|test-all|interactive]")
            print("  test: Run comprehensive pipeline test")
            print("  test-all: Run all test scenarios")
            print("  interactive: Run in interactive mode")
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 
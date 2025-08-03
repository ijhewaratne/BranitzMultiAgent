# Enhanced Branitz Energy Decision AI - Agent System

A sophisticated multi-agent system for urban energy planning with **comprehensive infrastructure analysis capabilities**, providing production-grade energy simulation and interactive visualization through intelligent agent delegation.

## 🚀 **NEW: Comprehensive Analysis Integration**

This enhanced system now incorporates the full simulation and analysis stack from `street_final_copy_3`, providing:

- **🔌 Heat Pump Feasibility Analysis**: Power flow simulation, proximity assessment, electrical infrastructure analysis
- **🔥 District Heating Network Design**: Dual-pipe networks, hydraulic simulation, thermal infrastructure analysis  
- **📊 Interactive Dashboards**: Responsive HTML dashboards with charts and metrics
- **🗺️ Interactive Maps**: Folium-based maps with layer controls and street-following routing
- **⚡ Real-time Analysis**: Pandapower and pandapipes integration for accurate simulations

## 🤖 **Enhanced Agent Architecture**

The system consists of **7 specialized agents** with comprehensive analysis capabilities:

### **1. EnergyPlannerAgent** 🎯
- **Role**: Master orchestrator and delegation manager
- **Function**: Analyzes user requests and delegates to appropriate specialist agents
- **Tools**: None (delegation only)

### **2. CentralHeatingAgent (CHA)** 🔥
- **Role**: District Heating specialist with comprehensive analysis
- **Function**: Executes complete DH scenario analysis including:
  - Dual-pipe network design (supply + return)
  - Pandapipes hydraulic simulation
  - Interactive dashboard generation
  - Comprehensive metrics and reporting
- **Tools**: `run_comprehensive_dh_analysis`

### **3. DecentralizedHeatingAgent (DHA)** ❄️
- **Role**: Heat Pump specialist with comprehensive analysis
- **Function**: Executes complete HP scenario analysis including:
  - Power flow simulation with pandapower
  - Proximity analysis to electrical infrastructure
  - Interactive dashboard with charts
  - Comprehensive feasibility assessment
- **Tools**: `run_comprehensive_hp_analysis`

### **4. ComparisonAgent (CA)** ⚖️
- **Role**: Scenario comparison expert
- **Function**: Runs both DH and HP scenarios and provides side-by-side comparison
- **Tools**: `compare_comprehensive_scenarios`

### **5. AnalysisAgent (AA)** 📊
- **Role**: Comprehensive analysis specialist
- **Function**: Runs complete end-to-end analysis with enhanced capabilities
- **Tools**: Multiple analysis options (HP, DH, comparison)

### **6. DataExplorerAgent (DEA)** 🔍
- **Role**: Data exploration and results management
- **Function**: Helps users explore available data and results
- **Tools**: Street listing, results listing, KPI analysis

### **7. EnergyGPT** 🧠
- **Role**: AI-powered analysis and reporting
- **Function**: Generates natural language insights from KPI data
- **Tools**: KPI analysis

## 🛠️ **Enhanced Tools & Capabilities**

### **Comprehensive Analysis Tools**
- `run_comprehensive_hp_analysis(street_name, scenario)` - Complete HP feasibility analysis
- `run_comprehensive_dh_analysis(street_name)` - Complete DH network analysis
- `compare_comprehensive_scenarios(street_name, hp_scenario)` - Side-by-side comparison

### **Data Exploration Tools**
- `get_all_street_names()` - Lists all available streets
- `get_building_ids_for_street(street_name)` - Extracts building IDs for a street
- `list_available_results()` - Shows all generated files including dashboards

### **Legacy Tools (Backward Compatibility)**
- `create_network_graph(building_ids, output_dir)` - Creates building network
- `run_simulation_pipeline(building_ids, scenario_type)` - Legacy simulation pipeline
- `analyze_kpi_report(kpi_path)` - AI-powered KPI analysis

## 🚀 **Quick Start**

### 1. **Setup & Installation**
```bash
# Navigate to the agents copy directory
cd "agents copy"

# Run the setup script
python setup_enhanced_system.py

# Activate your conda environment (if using)
conda activate branitz_env
```

### 2. **Start the Enhanced System**
```bash
# Interactive mode (recommended)
python run_enhanced_agent_system.py

# Or run tests
python run_enhanced_agent_system.py test
python run_enhanced_agent_system.py test-all
```

### 3. **Interactive Usage**
The system will present you with options:
- `analyze heat pump feasibility for Parkstraße` - Run comprehensive HP analysis
- `analyze district heating for Luciestraße` - Run comprehensive DH analysis
- `compare both scenarios for Damaschkeallee` - Compare HP vs DH
- `show available streets` - List all streets in dataset
- `show results` - List all generated files

## 📊 **Example Outputs**

### **Heat Pump Feasibility Analysis**
```
=== COMPREHENSIVE HEAT PUMP FEASIBILITY ANALYSIS ===
Street: Parkstraße
Scenario: winter_werktag_abendspitze
Buildings Analyzed: 15

📊 ELECTRICAL INFRASTRUCTURE METRICS:
• Max Transformer Loading: 0.10%
• Min Voltage: 1.020 pu
• Network Coverage: 100.0% of buildings close to transformers

🏢 PROXIMITY ANALYSIS:
• Avg Distance to Power Line: 45 m
• Avg Distance to Substation: 120 m
• Avg Distance to Transformer: 85 m
• Buildings Close to Transformer: 15/15

✅ IMPLEMENTATION READINESS:
• Electrical Capacity: ✅ Network can support heat pump loads
• Infrastructure Proximity: ✅ Buildings within connection range
• Street-Based Routing: ✅ Construction-ready service connections
• Power Quality: ✅ Voltage levels within acceptable range

🔗 DASHBOARD LINK: file:///path/to/hp_feasibility_dashboard.html
```

### **District Heating Network Analysis**
```
=== COMPREHENSIVE DISTRICT HEATING NETWORK ANALYSIS ===
Street: Luciestraße
Buildings Analyzed: 23

📊 NETWORK INFRASTRUCTURE:
• Supply Pipes: 0.85 km
• Return Pipes: 0.85 km
• Total Main Pipes: 1.70 km
• Service Pipes: 1150.5 m

🏢 BUILDING CONNECTIONS:
• Total Buildings: 23
• Service Connections: 46 (supply + return)
• Total Heat Demand: 230.0 MWh/year
• Network Density: 0.074 km per building

⚡ HYDRAULIC SIMULATION:
• Pressure Drop: 0.000018 bar
• Total Flow: 2.1 kg/s
• Temperature Drop: 30.0 °C
• Hydraulic Success: ✅ Yes

🔗 DASHBOARD LINK: file:///path/to/dh_dashboard.html
```

## 📁 **Generated Files**

### **Heat Pump Analysis Outputs**
```
results_test/hp_analysis/
├── hp_feasibility_dashboard.html     # Interactive dashboard
├── hp_feasibility_map.html          # Interactive map
├── building_proximity_table.csv     # Proximity analysis
├── dist_transformer_hist.png        # Distance distribution chart
├── dist_line_hist.png              # Power line distance chart
└── power_*.geojson                 # Power infrastructure data
```

### **District Heating Analysis Outputs**
```
results_test/dh_analysis/
├── dh_dashboard_*.html              # Interactive dashboard
├── dual_supply_pipes_*.csv         # Supply network data
├── dual_return_pipes_*.csv         # Return network data
├── dual_service_connections_*.csv  # Service connections
├── pandapipes_simulation_*.json    # Hydraulic simulation results
└── pandapipes_network_*.json       # Network topology
```

## 🔧 **Technical Requirements**

### **Dependencies**
- Python 3.8+
- pandapipes >= 0.8.0
- pandapower >= 2.14.0
- geopandas >= 0.12.0
- folium >= 0.14.0
- matplotlib >= 3.5.0
- networkx >= 2.8.0
- And more (see requirements.txt)

### **Data Requirements**
- Building footprints (GeoJSON)
- Street network (OSM)
- Power infrastructure data
- Load profiles (JSON)
- Network topology (JSON)

### **Integration Requirements**
- `street_final_copy_3/` directory accessible
- `thesis-data-2/` directory accessible
- Proper file paths configured

## 🎯 **Advanced Features**

### **Interactive Dashboards**
- **Responsive Design**: Adapts to different screen sizes
- **Real-time Metrics**: Live calculation of key performance indicators
- **Interactive Maps**: Folium-based maps with layer controls
- **Chart Integration**: Matplotlib-generated charts embedded in HTML

### **Comprehensive Analysis**
- **Power Flow Simulation**: Pandapower integration for electrical analysis
- **Hydraulic Simulation**: Pandapipes integration for thermal analysis
- **Street-Following Routing**: All connections follow existing street network
- **Proximity Analysis**: Distance-based feasibility assessment

### **Scenario Management**
- **Multiple Load Profiles**: Winter/summer, weekday/weekend scenarios
- **Flexible Parameters**: Customizable network and simulation parameters
- **Comparative Analysis**: Side-by-side HP vs DH comparison

## 🚀 **Usage Examples**

### **Heat Pump Analysis**
```
🎯 Your request: analyze heat pump feasibility for Parkstraße with winter evening peak scenario

🤔 Planner Agent is thinking...
🎯 Planner delegated to DHA.

⚡ DecentralizedHeatingAgent is executing your request...
TOOL: Running comprehensive HP analysis for 'Parkstraße' with scenario 'winter_werktag_abendspitze'...
TOOL: Found 15 buildings for analysis
TOOL: Power flow simulation completed successfully
TOOL: Interactive dashboard generated

📊 DecentralizedHeatingAgent Response:
=== COMPREHENSIVE HEAT PUMP FEASIBILITY ANALYSIS ===
[Detailed analysis results with metrics and dashboard link]
```

### **District Heating Analysis**
```
🎯 Your request: analyze district heating for Luciestraße

🤔 Planner Agent is thinking...
🎯 Planner delegated to CHA.

⚡ CentralHeatingAgent is executing your request...
TOOL: Running comprehensive DH analysis for 'Luciestraße'...
TOOL: Dual-pipe network created successfully
TOOL: Hydraulic simulation completed
TOOL: Interactive dashboard generated

📊 CentralHeatingAgent Response:
=== COMPREHENSIVE DISTRICT HEATING NETWORK ANALYSIS ===
[Detailed analysis results with metrics and dashboard link]
```

### **Scenario Comparison**
```
🎯 Your request: compare both scenarios for Damaschkeallee

🤔 Planner Agent is thinking...
🎯 Planner delegated to CA.

⚡ ComparisonAgent is executing your request...
TOOL: Running comprehensive scenario comparison for 'Damaschkeallee'...
TOOL: HP analysis completed
TOOL: DH analysis completed
TOOL: Comparison report generated

📊 ComparisonAgent Response:
=== COMPREHENSIVE SCENARIO COMPARISON ===
[Side-by-side comparison with recommendations]
```

## 🔗 **Integration with Existing Systems**

### **Backward Compatibility**
- Legacy tools and agents still available
- Existing workflows continue to work
- Gradual migration path to enhanced capabilities

### **Modular Design**
- Enhanced tools can be used independently
- Legacy and enhanced systems can coexist
- Easy to extend with additional capabilities

## 📈 **Performance & Scalability**

### **Optimizations**
- Efficient data loading and processing
- Parallel computation where possible
- Caching of intermediate results
- Memory-efficient large dataset handling

### **Scalability**
- Handles large building datasets
- Efficient network analysis algorithms
- Optimized visualization generation
- Modular architecture for easy extension

## 🎉 **Conclusion**

The Enhanced Branitz Energy Decision AI Agent System represents a **significant advancement** in urban energy infrastructure analysis:

- **🤖 AI-Driven**: Natural language interface with intelligent agent delegation
- **🔌 Comprehensive**: Full power flow and hydraulic simulation capabilities
- **📊 Interactive**: Rich visualizations and dashboards
- **🏗️ Production-Ready**: Industry-standard simulation tools
- **🔗 Integrated**: Seamless integration of multiple analysis approaches

This system provides **decision-makers** with the tools they need to make informed choices about urban energy infrastructure, combining the power of AI with the precision of engineering simulation tools.

---

**Ready to transform urban energy planning? Start with the Enhanced Branitz Energy Decision AI Agent System!** 🚀 
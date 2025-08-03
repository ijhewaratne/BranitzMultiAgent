# Branitz Energy Decision AI - Agent System

A comprehensive multi-agent system for energy infrastructure analysis and decision-making in the Branitz area, focusing on heat pump feasibility and district heating network optimization.

## 🏗️ Project Overview

This system integrates advanced geospatial analysis, power flow simulation, and hydraulic modeling to provide comprehensive energy infrastructure assessments. It uses a multi-agent architecture to handle different types of energy analysis tasks.

## 🚀 Features

### Core Capabilities
- **Heat Pump Feasibility Analysis**: Electrical infrastructure assessment for heat pump deployment
- **District Heating Network Analysis**: Dual-pipe network design and hydraulic simulation
- **Multi-Agent System**: Intelligent task delegation and analysis coordination
- **Interactive Visualizations**: Professional dashboards with interactive maps
- **Street-Based Routing**: Realistic service connection planning
- **Power Flow Simulation**: Pandapower-based electrical network analysis

### Technical Features
- **Geospatial Analysis**: Advanced spatial proximity and routing algorithms
- **Real-time Simulation**: Power flow and hydraulic network modeling
- **Interactive Maps**: Folium-based interactive visualizations
- **Comprehensive Reporting**: Detailed analysis reports and KPI dashboards
- **Modular Architecture**: Extensible agent-based system design

## 📁 Project Structure

```
agents copy/
├── adk/                          # ADK framework for multi-agent system
├── data/                         # Geospatial data files
│   └── geojson/                  # Building and street data
├── results_test/                 # Analysis outputs and dashboards
│   ├── hp_analysis/             # Heat pump feasibility results
│   └── dh_analysis/             # District heating analysis results
├── street_final_copy_3/          # Core analysis modules
│   ├── branitz_hp_feasibility.py
│   ├── create_complete_dual_pipe_dh_network_improved.py
│   ├── simulate_dual_pipe_dh_network_final.py
│   └── 08_interactive_dual_pipe_runner_enhanced.py
├── simple_enhanced_agents.py     # Agent definitions
├── simple_enhanced_tools.py      # Analysis tools and functions
├── run_simple_enhanced_system.py # Main execution script
└── requirements.txt              # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Conda (recommended for environment management)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agents-copy
   ```

2. **Create and activate conda environment**
   ```bash
   conda create -n branitz_env python=3.10
   conda activate branitz_env
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install additional packages**
   ```bash
   conda install -c conda-forge geopandas folium networkx scipy pandas numpy matplotlib
   pip install pandapower pandapipes adk
   ```

## 🚀 Usage

### Quick Start

1. **Activate the environment**
   ```bash
   conda activate branitz_env
   ```

2. **Run the system**
   ```bash
   python run_simple_enhanced_system.py
   ```

3. **Interactive Mode**
   ```bash
   python run_simple_enhanced_system.py interactive
   ```

### Example Commands

#### Heat Pump Feasibility Analysis
```python
# Analyze heat pump feasibility for a specific street
"analyze heat pump feasibility for Damaschkeallee"

# Analyze with specific scenario
"analyze heat pump feasibility for Parkstraße with winter evening peak scenario"
```

#### District Heating Analysis
```python
# Analyze district heating network
"analyze district heating feasibility for Luciestraße"

# Compare scenarios
"compare heat pump vs district heating for Damaschkeallee"
```

#### Data Exploration
```python
# Explore available data
"show available streets"
"get building information for Damaschkeallee"
```

## 🤖 Agent System

### Available Agents

1. **EnergyPlannerAgent**: Main coordinator for energy analysis tasks
2. **DecentralizedHeatingAgent**: Handles heat pump feasibility analysis
3. **CentralHeatingAgent**: Manages district heating network analysis
4. **ComparisonAgent**: Compares different energy scenarios
5. **AnalysisAgent**: Provides detailed analysis reports
6. **DataExplorerAgent**: Explores and queries available data

### Agent Capabilities

Each agent has specialized tools for:
- **Geospatial Analysis**: Building filtering, proximity calculations
- **Network Simulation**: Power flow and hydraulic modeling
- **Visualization**: Interactive maps and dashboards
- **Reporting**: Comprehensive analysis reports

## 📊 Output Files

### Generated Files
- **Interactive Maps**: HTML files with Folium-based visualizations
- **Dashboards**: Comprehensive HTML dashboards with metrics and charts
- **Data Tables**: CSV files with detailed analysis results
- **Charts**: PNG files with statistical visualizations

### File Locations
- `results_test/hp_analysis/`: Heat pump feasibility results
- `results_test/dh_analysis/`: District heating analysis results
- `street_final_copy_3/branitz_hp_feasibility_outputs/`: Core analysis outputs

## 🔧 Configuration

### Environment Variables
- Set up your conda environment: `branitz_env`
- Ensure all required packages are installed

### Data Files
- Building data: `data/geojson/hausumringe_mit_adressenV3.geojson`
- Street data: `data/geojson/strassen_mit_adressenV3.geojson`
- Power infrastructure: Available in `street_final_copy_3/`

## 📈 Analysis Capabilities

### Heat Pump Feasibility
- **Electrical Infrastructure Assessment**: Transformer loading, voltage analysis
- **Proximity Analysis**: Distance to power lines, substations, transformers
- **Service Connection Planning**: Street-following routing algorithms
- **Load Profile Integration**: Time-series energy demand analysis

### District Heating Analysis
- **Network Design**: Dual-pipe supply and return systems
- **Hydraulic Simulation**: Pressure and temperature drop calculations
- **Service Connections**: Building-to-network connections
- **Optimization**: Network efficiency and cost analysis

### Comparative Analysis
- **Scenario Comparison**: Heat pump vs district heating
- **Cost-Benefit Analysis**: Implementation costs and benefits
- **Technical Feasibility**: Infrastructure requirements assessment
- **Environmental Impact**: Energy efficiency and emissions analysis

## 🧪 Testing

### Run Tests
```bash
python run_simple_enhanced_system.py test
```

### Test Coverage
- End-to-end pipeline testing
- Agent functionality verification
- Analysis accuracy validation
- Output file generation testing

## 📝 Documentation

### Code Documentation
- Inline code comments
- Function docstrings
- Module-level documentation

### User Guides
- Installation instructions
- Usage examples
- Configuration guides

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ADK Framework**: Multi-agent system architecture
- **Pandapower**: Electrical network simulation
- **Pandapipes**: Hydraulic network simulation
- **Folium**: Interactive map visualization
- **GeoPandas**: Geospatial data processing

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0**: Initial release with basic agent system
- **v1.1.0**: Added comprehensive analysis capabilities
- **v1.2.0**: Enhanced visualization and reporting
- **v1.3.0**: Integrated street-based routing and advanced simulations

---

**Note**: This system is designed for research and analysis purposes. Always verify results and consult with energy professionals for real-world implementation decisions.

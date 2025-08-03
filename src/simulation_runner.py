# src/simulation_runner.py

import argparse
import json
from pathlib import Path
import multiprocessing
import traceback

RESULTS_DIR = Path("simulation_outputs")
RESULTS_DIR.mkdir(exist_ok=True)

def run_pandapipes_simulation(scenario):
    """
    Placeholder: Run a single pandapipes simulation for DH scenario.
    Returns dict of results/KPIs for this scenario.
    """
    # Example: load network, buildings, run your simulation function
    try:
        print(f"Running DH simulation for scenario: {scenario['name']}")
        # Load buildings and network as needed (expand as required)
        #  import  actual simulation logic here
        # from dh_simulation import run_dh
        # results = run_dh(...)
        # Here, just return dummy output
        results = {
            "scenario": scenario["name"],
            "type": "DH",
            "success": True,
            "kpi": {"total_heat_supplied_mwh": 1234, "pump_energy_kwh": 3000, "max_pressure_drop_bar": 0.7}
        }
        return results
    except Exception as e:
        traceback.print_exc()
        return {"scenario": scenario.get("name", ""), "type": "DH", "success": False, "error": str(e)}

def run_pandapower_simulation(scenario):
    """
    Placeholder: Run a single pandapower simulation for HP scenario.
    Returns dict of results/KPIs for this scenario.
    """
    try:
        print(f"Running HP simulation for scenario: {scenario['name']}")
        # Load buildings and network as needed
        # from hp_simulation import run_hp
        # results = run_hp(...)
        results = {
            "scenario": scenario["name"],
            "type": "HP",
            "success": True,
            "kpi": {"max_feeder_load_percent": 82, "transformer_overloads": 1}
        }
        return results
    except Exception as e:
        traceback.print_exc()
        return {"scenario": scenario.get("name", ""), "type": "HP", "success": False, "error": str(e)}

def run_scenario(scenario_file):
    """
    Load scenario JSON, call the correct simulation function, and save results.
    """
    try:
        with open(scenario_file, "r", encoding="utf-8") as f:
            scenario = json.load(f)
        if scenario.get("type", "DH").upper() == "DH":
            results = run_pandapipes_simulation(scenario)
        elif scenario.get("type", "DH").upper() == "HP":
            results = run_pandapower_simulation(scenario)
        else:
            raise ValueError(f"Unknown scenario type: {scenario.get('type')}")
        # Save results to output file
        out_file = RESULTS_DIR / f"{scenario['name']}_results.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved: {out_file}")
        return results
    except Exception as e:
        traceback.print_exc()
        return {"scenario_file": scenario_file, "success": False, "error": str(e)}

def run_simulation_scenarios(scenario_files, parallel=True):
    """
    Batch run all scenario files. Can use multiprocessing.
    """
    print(f"Running simulations for {len(scenario_files)} scenarios...")
    if parallel and len(scenario_files) > 1:
        with multiprocessing.Pool(processes=min(4, len(scenario_files))) as pool:
            results = pool.map(run_scenario, scenario_files)
    else:
        results = [run_scenario(sf) for sf in scenario_files]
    print("\nAll simulations complete.")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch energy network simulations for scenario files.")
    parser.add_argument("--scenarios", nargs='+', required=True,
                        help="List of scenario JSON files to run")
    parser.add_argument("--no_parallel", action="store_true", help="Disable multiprocessing")
    args = parser.parse_args()

    scenario_files = args.scenarios
    run_simulation_scenarios(scenario_files, parallel=not args.no_parallel)

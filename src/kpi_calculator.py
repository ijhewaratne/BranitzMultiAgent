# src/kpi_calculator.py

import argparse
import json
from pathlib import Path
import pandas as pd

DEFAULT_COST_PARAMS = {
    "heat_pump_cop": 3.5,
    "elec_price_eur_per_kwh": 0.35,
    "biomass_price_eur_per_kwh": 0.07,
    "capex_hp_eur": 14000,
    "capex_dh_eur_per_meter": 800,
    "opex_factor": 0.01,  # O&M as percent of capex per year
    "discount_rate": 0.04,
    "project_lifetime": 20,
}

DEFAULT_EMISSIONS = {
    "grid_electricity_gco2_per_kwh": 290,
    "biomass_gco2_per_kwh": 70,
}

def compute_lcoh(total_costs_eur, total_heat_supplied_mwh, discount_rate, lifetime):
    """
    Simple NPV-based Levelized Cost of Heat (LCoH, €/MWh).
    """
    if total_heat_supplied_mwh == 0:
        return float("inf")
    # Annuitization factor (fixed capital recovery)
    q = 1 + discount_rate
    ann_factor = (q ** lifetime * discount_rate) / (q ** lifetime - 1)
    annualized_costs = total_costs_eur * ann_factor
    lcoh = annualized_costs / total_heat_supplied_mwh
    return lcoh

def compute_co2_emissions(energy_kwh, fuel_type, emissions_factors):
    """
    Returns emissions in tCO2 (tonnes).
    """
    if fuel_type == "electricity":
        gco2_per_kwh = emissions_factors.get("grid_electricity_gco2_per_kwh", 290)
    elif fuel_type == "biomass":
        gco2_per_kwh = emissions_factors.get("biomass_gco2_per_kwh", 70)
    else:
        gco2_per_kwh = 400  # fallback for fossil
    return (energy_kwh * gco2_per_kwh) / 1e6  # [tCO2]

def compute_kpis(sim_results, cost_params=None, emissions_factors=None):
    """
    Aggregate KPIs for all simulation results.
    Returns a DataFrame of scenario KPIs.
    """
    cost_params = cost_params or DEFAULT_COST_PARAMS
    emissions_factors = emissions_factors or DEFAULT_EMISSIONS
    kpi_records = []

    for res in sim_results:
        if not res.get("success", False):
            kpi_records.append({
                "scenario": res.get("scenario", ""),
                "type": res.get("type", ""),
                "lcoh_eur_per_mwh": None,
                "co2_t_per_a": None,
                "comment": res.get("error", "simulation failed"),
            })
            continue

        if res.get("type") == "DH":
            # District Heating (pandapipes)
            heat_supplied_mwh = res['kpi'].get("total_heat_supplied_mwh", 0)
            pump_energy_kwh = res['kpi'].get("pump_energy_kwh", 0)
            length_network_m = res['kpi'].get("network_length_m", 3000)
            capex = length_network_m * cost_params["capex_dh_eur_per_meter"]
            opex = capex * cost_params["opex_factor"] * cost_params["project_lifetime"]
            energy_costs = heat_supplied_mwh * 1000 * cost_params["biomass_price_eur_per_kwh"]
            total_costs = capex + opex + energy_costs
            lcoh = compute_lcoh(total_costs, heat_supplied_mwh, cost_params["discount_rate"], cost_params["project_lifetime"])
            co2 = compute_co2_emissions(heat_supplied_mwh * 1000, "biomass", emissions_factors) \
                  + compute_co2_emissions(pump_energy_kwh, "electricity", emissions_factors)
            kpi_records.append({
                "scenario": res.get("scenario", ""),
                "type": "DH",
                "lcoh_eur_per_mwh": round(lcoh, 2),
                "co2_t_per_a": round(co2, 2),
                "max_pressure_drop_bar": res['kpi'].get("max_pressure_drop_bar", None),
                "pump_energy_kwh": pump_energy_kwh,
                "comment": "",
            })
        elif res.get("type") == "HP":
            # Heat Pump (pandapower)
            hp_energy_mwh = res['kpi'].get("total_heat_supplied_mwh", 1200)
            hp_elec_kwh = hp_energy_mwh * 1000 / cost_params["heat_pump_cop"]
            capex = cost_params["capex_hp_eur"] * res['kpi'].get("n_heat_pumps", 100)
            opex = capex * cost_params["opex_factor"] * cost_params["project_lifetime"]
            energy_costs = hp_elec_kwh * cost_params["elec_price_eur_per_kwh"]
            total_costs = capex + opex + energy_costs
            lcoh = compute_lcoh(total_costs, hp_energy_mwh, cost_params["discount_rate"], cost_params["project_lifetime"])
            co2 = compute_co2_emissions(hp_elec_kwh, "electricity", emissions_factors)
            kpi_records.append({
                "scenario": res.get("scenario", ""),
                "type": "HP",
                "lcoh_eur_per_mwh": round(lcoh, 2),
                "co2_t_per_a": round(co2, 2),
                "max_feeder_load_percent": res['kpi'].get("max_feeder_load_percent", None),
                "transformer_overloads": res['kpi'].get("transformer_overloads", None),
                "comment": "",
            })
        else:
            kpi_records.append({
                "scenario": res.get("scenario", ""),
                "type": res.get("type", ""),
                "lcoh_eur_per_mwh": None,
                "co2_t_per_a": None,
                "comment": "Unknown scenario type"
            })

    return pd.DataFrame(kpi_records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate and compute KPIs from simulation results.")
    parser.add_argument("--results", nargs='+', required=True,
                        help="List of simulation results JSON files")
    parser.add_argument("--cost_params", default=None, help="Cost params JSON (optional)")
    parser.add_argument("--emissions_factors", default=None, help="Emissions factors JSON (optional)")
    parser.add_argument("--output_csv", default="results/scenario_kpis.csv", help="Summary output CSV")
    parser.add_argument("--output_json", default="results/scenario_kpis.json", help="Summary output JSON")
    args = parser.parse_args()

    # Load simulation results
    sim_results = []
    for rf in args.results:
        with open(rf, "r", encoding="utf-8") as f:
            sim_results.append(json.load(f))

    # Load params if provided
    cost_params = DEFAULT_COST_PARAMS
    emissions_factors = DEFAULT_EMISSIONS
    if args.cost_params:
        with open(args.cost_params, "r", encoding="utf-8") as f:
            cost_params = json.load(f)
    if args.emissions_factors:
        with open(args.emissions_factors, "r", encoding="utf-8") as f:
            emissions_factors = json.load(f)

    # Compute KPIs and save
    kpi_df = compute_kpis(sim_results, cost_params, emissions_factors)
    Path("results").mkdir(exist_ok=True)
    kpi_df.to_csv(args.output_csv, index=False)
    kpi_df.to_json(args.output_json, orient="records", indent=2)
    print(f"KPI table written to {args.output_csv} and {args.output_json}")

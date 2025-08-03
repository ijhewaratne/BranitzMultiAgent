# src/llm_reporter.py

import argparse
import json
import pandas as pd
from pathlib import Path

# ---- You can swap OpenAI for Gemini or another API here ----
try:
    import openai
except ImportError:
    openai = None

#client = openai.OpenAI(api_key=openai_api_key)
SYSTEM_PROMPT = (
    "You are EnergyGPT, an expert AI for municipal energy decision-making. "
    "Your job is to summarize and explain, in clear language for planners and stakeholders, "
    "the key trade-offs and results from heating scenario evaluations in Branitz. "
    "Give evidence-based, unbiased, and actionable advice based on the supplied KPI table and scenario information."
)

def create_llm_report(kpis, scenario_metadata, config, model="gpt-4o", openai_api_key=None):
    """
    Generates an executive summary report via LLM (OpenAI API by default).
    kpis: DataFrame or list of dicts with KPIs per scenario
    scenario_metadata: dict/list with context about scenarios
    config: dict of extra context, user prompt, etc.
    Returns report string.
    """
    
    import openai
    if openai is None:
        raise ImportError("openai Python module not found. Install with `pip install openai`.")

    # --- Call the LLM API ---
    if not openai_api_key:
        import os
        openai_api_key = os.environ.get("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=openai_api_key)
    # Assemble the prompt for the LLM
    table_md = pd.DataFrame(kpis).to_markdown(index=False)
    prompt = (
        f"You are an expert energy transition assistant helping a city planner make decisions between district heating (DH) and decentralized heat pumps (HP) for urban decarbonization.\n"
        f"Below is a summary table of key performance indicators (KPIs) from simulation results for several scenarios. "
        f"Compare and explain which scenario is most attractive, and why. Reference costs (LCoH), CO₂ emissions, technical constraints, and any other important factors. "
        f"Make the language clear for both technical and non-technical readers. Close with a concise recommendation.\n\n"
        f"SCENARIO METADATA:\n{json.dumps(scenario_metadata, indent=2)}\n\n"
        f"KPI SUMMARY TABLE:\n{table_md}\n"
    )
    if config and "extra_prompt" in config:
        prompt += "\n" + config["extra_prompt"]

    # --- Call the LLM API ---
    if openai is None:
        raise ImportError("openai Python module not found. Install with `pip install openai`.")

    if openai_api_key:
        openai.api_key = openai_api_key

    print("Sending prompt to LLM...")
    response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content
    return reply


def main(args_list=None):
    """
    Main entry for pipeline or CLI. Accepts sys.argv[1:] as list, or None (uses sys.argv).
    """
    import sys
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Generate a natural-language executive report using an LLM.")
    parser.add_argument("--kpis", required=True, help="KPI summary file (CSV or JSON)")
    parser.add_argument("--scenarios", required=True, help="Scenario metadata file (YAML or JSON)")
    parser.add_argument("--config", default=None, help="Config file (optional, JSON/YAML)")
    parser.add_argument("--output", default="reports/llm_report.md", help="Output Markdown file")
    parser.add_argument("--model", default="gpt-4o", help="LLM model name (default: gpt-4o)")
    parser.add_argument("--api_key", default=None, help="OpenAI API key (or set OPENAI_API_KEY env var)")
    if args_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args_list)

    Path("reports").mkdir(exist_ok=True)

    # Load KPIs
    if args.kpis.endswith(".csv"):
        kpis = pd.read_csv(args.kpis)
    else:
        with open(args.kpis, "r", encoding="utf-8") as f:
            kpis = pd.DataFrame(json.load(f))

    # Load scenario metadata
    if args.scenarios.endswith(".json"):
        with open(args.scenarios, "r", encoding="utf-8") as f:
            scenario_metadata = json.load(f)
    else:
        # Try YAML
        try:
            import yaml
            with open(args.scenarios, "r", encoding="utf-8") as f:
                scenario_metadata = yaml.safe_load(f)
        except Exception:
            scenario_metadata = {}

    # Load config
    config = {}
    if args.config:
        if args.config.endswith(".json"):
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            try:
                import yaml
                with open(args.config, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            except Exception:
                pass

    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")

    # Generate LLM report
    report_md = create_llm_report(
        kpis=kpis,
        scenario_metadata=scenario_metadata,
        config=config,
        model=args.model,
        openai_api_key=api_key,
    )

    # Save output as markdown
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"LLM report written to {args.output}")

    # Also save as HTML and TXT for convenience
    try:
        import markdown
        html = markdown.markdown(report_md)
        with open(args.output.replace('.md', '.html'), "w", encoding="utf-8") as f:
            f.write(html)
        with open(args.output.replace('.md', '.txt'), "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"Report also saved as HTML and TXT.")
    except ImportError:
        pass

if __name__ == "__main__":
    main()

import argparse
import csv
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables. `python-dotenv` will search up the directory tree for .env
load_dotenv(".env.local")


def get_langsmith_client():
    """Initializes and returns the Langsmith client."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        logging.error("LANGSMITH_API_KEY environment variable not set.")
        raise ValueError("API key not found.")
    return Client(api_key=api_key)


def fetch_root_runs(client, project_name, date_filter):
    """Fetches root runs from Langsmith."""
    logging.info(f"Fetching root runs for project '{project_name}'...")
    try:
        root_runs_iterator = client.list_runs(
            project_name=project_name,
            is_root=True,
            filter=date_filter,
        )
        all_root_runs = [run.model_dump() for run in root_runs_iterator]
        logging.info(f"Total root runs found: {len(all_root_runs)}")
        return all_root_runs
    except Exception as e:
        logging.error(f"Failed to fetch root runs: {e}")
        return []


def fetch_retriever_runs(client, project_name, date_filter):
    """Fetches retriever runs and indexes them by trace ID."""
    logging.info("Fetching retriever runs...")
    try:
        retriever_runs_iterator = client.list_runs(
            project_name=project_name,
            run_type="retriever",
            filter=date_filter,
        )

        retriever_by_trace = {}
        for run in retriever_runs_iterator:
            run_data = run.model_dump()
            trace_id = str(run_data.get("trace_id") or run_data.get("parent_run_id", ""))
            if trace_id not in retriever_by_trace:
                retriever_by_trace[trace_id] = []

            output = run_data.get("outputs", {})
            docs = output.get("documents", output.get("output", []))
            retriever_by_trace[trace_id].append(docs)

        logging.info(f"Found retriever contexts for {len(retriever_by_trace)} traces.")
        return retriever_by_trace
    except Exception as e:
        logging.error(f"Failed to fetch retriever runs: {e}")
        return {}


def combine_runs_with_context(root_runs, retriever_by_trace):
    """Merges root runs with their corresponding retrieval context."""
    logging.info("Combining root runs with retrieval context...")
    flat_runs = []
    for run_data in root_runs:
        run_id = str(run_data.get("id", ""))
        retrieval_context = retriever_by_trace.get(run_id)

        flat_run = {
            "id": run_id,
            "start_time": run_data.get("start_time", ""),
            "end_time": run_data.get("end_time", ""),
            "status": run_data.get("status", ""),
            "error": run_data.get("error", ""),
            "inputs": json.dumps(run_data.get("inputs", {}), ensure_ascii=False),
            "outputs": json.dumps(run_data.get("outputs", {}), ensure_ascii=False),
            "metadata": json.dumps(
                run_data.get("extra", {}).get("metadata", {}), ensure_ascii=False
            ),
            "retrieval_context": json.dumps(retrieval_context, ensure_ascii=False, default=str)
            if retrieval_context
            else "",
            "has_retrieval_context": bool(retrieval_context),
        }
        flat_runs.append(flat_run)
    return flat_runs


def export_data(flat_runs, output_dir, start_date, end_date):
    """Exports the combined data to JSON and CSV files."""
    if not flat_runs:
        logging.warning("No data to export.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # Format dates for the filename, using only the date part
    start_date_str = start_date.split("T")[0]
    end_date_str = end_date.split("T")[0]

    file_basename = f"runs_export_{start_date_str}_to_{end_date_str}"
    json_path = output_dir / f"{file_basename}.json"
    csv_path = output_dir / f"{file_basename}.csv"

    logging.info(f"Exporting data to {json_path} and {csv_path}...")

    # Export to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(flat_runs, f, default=str, ensure_ascii=False, indent=2)

    # Export to CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat_runs[0].keys())
        writer.writeheader()
        writer.writerows(flat_runs)

    logging.info("Export completed successfully.")


def run_diagnostic(flat_runs):
    """Prints a quick diagnostic of the exported data."""
    if not flat_runs:
        return

    with_context = sum(1 for r in flat_runs if r["has_retrieval_context"])
    without_context = len(flat_runs) - with_context

    logging.info("--- Diagnostic ---")
    logging.info(f"   Runs WITH context: {with_context}")
    logging.info(f"   Runs WITHOUT context: {without_context}")
    logging.info("--------------------")


def main():
    """Main function to orchestrate the script."""
    parser = argparse.ArgumentParser(
        description="Export Langsmith runs with found documents context."
    )
    parser.add_argument(
        "--project-name", default="testing-dev-martin", help="Langsmith project name"
    )
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output-dir", default="traces_exported")

    args = parser.parse_args()

    date_filter = f'and(gt(start_time, "{args.start_date}"), lt(start_time, "{args.end_date}"))'

    try:
        client = get_langsmith_client()

        root_runs = fetch_root_runs(client, args.project_name, date_filter)
        if not root_runs:
            logging.warning("No root runs found. Exiting.")
            return

        retriever_by_trace = fetch_retriever_runs(client, args.project_name, date_filter)

        flat_runs = combine_runs_with_context(root_runs, retriever_by_trace)

        export_data(flat_runs, Path(args.output_dir), args.start_date, args.end_date)

        run_diagnostic(flat_runs)

    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

# run_evaluation_simulation.py
"""
Script to run evaluation simulations for the LLM Policy Analysis Framework.

This script orchestrates:
1. Loading/Generating simulation data (predictions and ground truths).
2. Running selected evaluation metrics.
3. Generating reports and checking for alerts based on results.
"""

import logging
import sys
import os
from typing import List, Any, Dict

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import necessary modules from the project
try:
    from utils.logging_config import setup_logging
    # Evaluation Metrics
    from evaluation.metrics.accuracy_metrics import (
        calculate_accuracy, calculate_precision, calculate_recall, calculate_f1_score,
        plot_confusion_matrix # Added import
    )
    # Placeholder imports for other metrics (uncomment as needed)
    # from evaluation.metrics.relevance_metrics import calculate_rouge_scores # etc.
    # from evaluation.metrics.bias_metrics import calculate_demographic_parity_difference # etc.
    # from evaluation.metrics.insight_metrics import calculate_novelty_score # etc.

    # Evaluation Reporting
    from evaluation.reporting.report_generator import ReportGenerator
    from evaluation.reporting.alerting_system import AlertingSystem
    # from evaluation.reporting.dashboard_connector import PlaceholderDashboardConnector # etc.

except ImportError as e:
    print(f"Error importing project modules: {e}")
    print(f"Please ensure the script is run from the project root directory '{project_root}'")
    print(f"and the 'src' directory '{src_path}' exists and is accessible.")
    sys.exit(1)

# Configure logging
# Consider moving logging setup to a central place or using config file if complex
setup_logging() # Removed level=logging.INFO argument
logger = logging.getLogger(__name__)

# --- Simulation Configuration ---
SIMULATION_CONFIG = {
    "run_name": "basic_accuracy_test_run",
    "data_source": "synthetic", # Could be 'file', 'database', etc. later
    "metrics_to_run": ["accuracy", "precision", "recall", "f1_score"],
    "reporting_formats": ["markdown", "json", "html"], # Added 'html'
    "alert_rules": [
        {"metric_path": "accuracy", "condition": "<", "threshold": 0.7},
        {"metric_path": "precision", "condition": "<=", "threshold": 0.6},
    ]
}

# --- Data Generation ---
def generate_synthetic_data(num_samples: int = 20) -> Dict[str, List[Any]]:
    """ Generates simple synthetic prediction and ground truth data. """
    logger.info(f"Generating {num_samples} synthetic data samples...")
    # Example: Simple binary classification data
    # More sophisticated generation can be added later (e.g., controlled bias)
    import random
    predictions = [random.choice([0, 1]) for _ in range(num_samples)]
    ground_truths = [random.choice([0, 1]) for _ in range(num_samples)]

    # Example with potential imbalance
    # predictions = random.choices([0, 1], weights=[0.7, 0.3], k=num_samples)
    # ground_truths = [1 if random.random() < 0.4 else 0 for _ in range(num_samples)] # 40% positive class

    logger.debug(f"Generated Predictions: {predictions}")
    logger.debug(f"Generated Ground Truths: {ground_truths}")
    return {"predictions": predictions, "ground_truths": ground_truths}

# --- Evaluation Execution ---
def run_evaluation(data: Dict[str, List[Any]], config: Dict) -> Dict[str, Any]:
    """ Runs the configured evaluation metrics on the provided data. """
    logger.info("Starting evaluation...")
    results = {}
    predictions = data.get("predictions")
    ground_truths = data.get("ground_truths")

    if not predictions or not ground_truths:
        logger.error("Missing 'predictions' or 'ground_truths' in data.")
        return results # Return empty results

    y_true = ground_truths
    y_pred = predictions

    # --- Run Selected Metrics ---
    # Basic Accuracy Metrics
    if "accuracy" in config.get("metrics_to_run", []):
        results["accuracy"] = calculate_accuracy(y_true, y_pred)
    if "precision" in config.get("metrics_to_run", []):
        results["precision"] = calculate_precision(y_true, y_pred)
    if "recall" in config.get("metrics_to_run", []):
        results["recall"] = calculate_recall(y_true, y_pred)
    if "f1_score" in config.get("metrics_to_run", []):
        results["f1_score"] = calculate_f1_score(y_true, y_pred)

    # --- Generate Visualizations ---
    # Confusion Matrix Plot
    cm_filename = f"{config.get('run_name', 'evaluation')}_confusion_matrix.png"
    plot_file_path = plot_confusion_matrix(
        y_true, 
        y_pred, 
        labels=[0, 1], # Assuming binary classification 0/1
        filename=cm_filename,
        title=f"Confusion Matrix - {config.get('run_name', '')}"
    )
    if plot_file_path:
        # Store plot filename for reporting
        results["visualizations"] = {"confusion_matrix_plot": plot_file_path}
    else:
        results["visualizations"] = {}

    # --- Placeholder for Other Metrics (Bias, Relevance, etc.) ---
    # if "demographic_parity" in config.get("metrics_to_run", []):
    #     results["demographic_parity"] = calculate_demographic_parity_difference(...) # Needs sensitive attributes

    logger.info(f"Evaluation completed. Results: {results}")
    return results

# --- Reporting ---
def generate_reports_and_alerts(results: Dict[str, Any], config: Dict[str, Any]):
    """Generates reports and checks alerts based on results and config."""
    logger.info("Generating reports and checking alerts...")

    # Report Generation
    reporting_formats = config.get("reporting_formats", ["markdown"])
    run_context = {"simulation_config": config}
    results_with_context = {**results, "run_context": run_context} # Add context to results

    for format in reporting_formats:
        try:
            report_generator = ReportGenerator(report_format=format)
            logger.info(f"Generating report in '{format}' format...")
            # Call generate_report with only the results (which now include context)
            report_content = report_generator.generate_report(results_with_context)

            if report_content:
                # Adjust extension for different formats
                ext = format
                if format == 'markdown': ext = 'md'
                if format == 'html': ext = 'html'
                report_filename = f"{config.get('run_name', 'evaluation_report')}.{ext}"
                with open(report_filename, "w", encoding="utf-8") as f:
                    f.write(report_content)
                logger.info(f"Generated report: {report_filename}")
        except ValueError as e:
            logger.error(f"Failed to generate report in format '{format}': {e}")
        except Exception as e:
             logger.exception(f"An unexpected error occurred generating report format '{format}': {e}")

    # Check alerts
    alert_rules = config.get("alert_rules", [])
    if alert_rules:
        # Use the correct keyword argument 'alert_rules'
        alerting_system = AlertingSystem(alert_rules=alert_rules)
        logger.info("Checking alerts...")
        # Pass the original results, not the one with context, unless alerts need context
        alerts_triggered = alerting_system.check_and_trigger_alerts(results)

        if alerts_triggered:
            logger.warning(f"Alerts triggered: {len(alerts_triggered)} rules met conditions.")
            # AlertingSystem logs details internally, no need for explicit logging here
        else:
            logger.info("No alert conditions met.")
    else:
        logger.info("No alert rules configured.")

    # Dashboard Connection (Placeholder)
    # dashboard_conn = PlaceholderDashboardConnector()
    # dashboard_conn.configure(target="simulation_dashboard")
    # dashboard_conn.send_data(results, context=run_context)
    # dashboard_conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    logger.info("=================================================")
    logger.info(f"Starting Evaluation Simulation: {SIMULATION_CONFIG.get('run_name')}")
    logger.info("=================================================")

    # 1. Generate Data
    simulation_data = generate_synthetic_data(num_samples=50) # Use more samples

    if not simulation_data.get("predictions") or not simulation_data.get("ground_truths"):
         logger.error("Data generation failed. Exiting.")
         sys.exit(1)

    # 2. Run Evaluation
    evaluation_results = run_evaluation(simulation_data, SIMULATION_CONFIG)

    if not evaluation_results:
         logger.error("Evaluation run failed or produced no results. Exiting.")
         sys.exit(1)

    # 3. Generate Reports and Alerts
    generate_reports_and_alerts(evaluation_results, SIMULATION_CONFIG)

    logger.info("=================================================")
    logger.info("Evaluation Simulation Finished.")
    logger.info("=================================================")

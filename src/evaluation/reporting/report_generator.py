"""
Generates structured reports from evaluation results.

This module provides classes and functions to take various evaluation
metrics and findings (e.g., accuracy, bias scores, relevance metrics,
explainability outputs) and compile them into comprehensive reports
in different formats (e.g., Markdown, JSON, potentially HTML).
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
import datetime
import os

# Potentially needed if generating complex formats like PDF:
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Compiles evaluation results into a structured report.
    """

    def __init__(
        self,
        report_format: str = 'markdown', # Supported formats: 'markdown', 'json', 'text', 'html'
        report_title: str = "Evaluation Report",
        **kwargs
    ):
        """
        Initializes the ReportGenerator.

        Args:
            report_format (str): The desired output format ('markdown', 'json', 'text', 'html').
            report_title (str): The main title for the report.
            **kwargs: Additional configuration options for specific formats.
        """
        self.report_format = report_format.lower()
        self.report_title = report_title
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.kwargs = kwargs
        logger.info(f"ReportGenerator initialized for format: {self.report_format}")

    def _format_markdown(self, evaluation_results: Dict[str, Any]) -> str:
        """Formats the report as Markdown."""
        lines = []
        lines.append(f"# {self.report_title}")
        lines.append(f"*Generated on: {self.timestamp}*")
        lines.append("\n---\n")

        for section, data in evaluation_results.items():
            lines.append(f"## {section.replace('_', ' ').title()}")
            if isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"- **{key.replace('_', ' ').title()}**: `{value}`")
            elif isinstance(data, list):
                 for item in data:
                     lines.append(f"- {item}") # Assumes list items are simple strings for now
            else:
                lines.append(str(data))
            lines.append("") # Add spacing

        return "\n".join(lines)

    def _format_json(self, evaluation_results: Dict[str, Any]) -> str:
        """Formats the report as JSON."""
        report_data = {
            "report_metadata": {
                "title": self.report_title,
                "generation_timestamp": self.timestamp,
                "format": self.report_format
            },
            "evaluation_results": evaluation_results
        }
        try:
            return json.dumps(report_data, indent=4, default=str) # Use default=str for non-serializable types
        except TypeError as e:
            logger.error(f"Error serializing report to JSON: {e}")
            return json.dumps({"error": "Failed to serialize report data."}, indent=4)

    def _format_text(self, evaluation_results: Dict[str, Any]) -> str:
        """Formats the report as plain text."""
        lines = []
        lines.append(f"{self.report_title}")
        lines.append(f"Generated on: {self.timestamp}")
        lines.append("=" * (len(self.report_title)))
        lines.append("")

        for section, data in evaluation_results.items():
            lines.append(f"--- {section.replace('_', ' ').upper()} ---")
            if isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            elif isinstance(data, list):
                 for item in data:
                     lines.append(f"  - {item}")
            else:
                lines.append(str(data))
            lines.append("") # Add spacing

        return "\n".join(lines)

    def _format_html(self, evaluation_results: Dict[str, Any]) -> str:
        """Formats the evaluation results into an HTML string."""
        # Basic HTML structure
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<title>Evaluation Report</title>",
            "<style>",
            "body { font-family: sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 60%; margin-bottom: 20px; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "h1, h2 { color: #333; }",
            "img { max-width: 100%; height: auto; border: 1px solid #ddd; margin-top: 10px; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Evaluation Report</h1>",
        ]

        # Add Run Context if available
        run_context = evaluation_results.get("run_context", {})
        if run_context:
            html_parts.append("<h2>Run Context</h2>")
            config = run_context.get("simulation_config", {})
            html_parts.append("<table>")
            html_parts.append(f"<tr><th>Run Name</th><td>{config.get('run_name', 'N/A')}</td></tr>")
            html_parts.append(f"<tr><th>Data Source</th><td>{config.get('data_source', 'N/A')}</td></tr>")
            # Add more context details if needed
            html_parts.append("</table>")

        # Add Metrics Sections (e.g., accuracy, bias - adapt as needed)
        metric_categories = ["accuracy_metrics", "bias_metrics", "relevance_metrics"]
        for category in metric_categories:
            if category in evaluation_results:
                html_parts.append(f"<h2>{category.replace('_', ' ').title()}</h2>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Metric</th><th>Value</th></tr>")
                metrics = evaluation_results[category]
                for metric_name, value in metrics.items():
                    formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                    html_parts.append(f"<tr><td>{metric_name.replace('_', ' ').title()}</td><td>{formatted_value}</td></tr>")
                html_parts.append("</table>")

        # Add Visualizations (e.g., Confusion Matrix)
        visualizations = evaluation_results.get("visualizations", {})
        cm_plot_file = visualizations.get("confusion_matrix_plot")
        if cm_plot_file:
             # Check if file exists before adding img tag
            if os.path.exists(cm_plot_file):
                html_parts.append("<h2>Confusion Matrix</h2>")
                # Use relative path if HTML and image are in the same dir, or absolute if needed
                # For simplicity, assume relative path works for now.
                html_parts.append(f'<img src="{os.path.basename(cm_plot_file)}" alt="Confusion Matrix">')
            else:
                logger.warning(f"Confusion matrix image file not found: {cm_plot_file}. Skipping embedding.")
                html_parts.append("<p><i>Confusion matrix plot image not found.</i></p>")

        # Closing tags
        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)


    def generate_report(
        self,
        evaluation_results: Dict[str, Any],
        # Example structure for evaluation_results:
        # {
        #     "accuracy_metrics": {"precision": 0.8, "recall": 0.7, ...},
        #     "bias_metrics": {"demographic_parity": 0.1, ...},
        #     "relevance_metrics": {"rougeL": 0.45, ...},
        #     "explainability_summary": ["Feature X is most important.", ...],
        #     "benchmarking_comparison": {"vs_baseline": "Improved", ...}
        # }
    ) -> Optional[str]:
        """
        Generates the evaluation report in the specified format.

        Args:
            evaluation_results (Dict[str, Any]): A dictionary containing the
                results from various evaluation components, organized by category.

        Returns:
            Optional[str]: The formatted report string, or None if generation fails.
        """
        logger.info(f"Generating report in {self.report_format} format...")
        if not evaluation_results:
            logger.warning("Cannot generate report: evaluation_results dictionary is empty.")
            return None

        try:
            if self.report_format == 'markdown':
                report_content = self._format_markdown(evaluation_results)
            elif self.report_format == 'json':
                report_content = self._format_json(evaluation_results)
            elif self.report_format == 'text':
                report_content = self._format_text(evaluation_results)
            elif self.report_format == 'html': # Add HTML format
                report_content = self._format_html(evaluation_results)
            # Add elif for other formats like PDF etc.
            # elif self.report_format == 'pdf':
            #    report_content = self._format_pdf(evaluation_results) # Placeholder
            #    logger.warning("PDF report generation is not fully implemented.")
            else:
                logger.error(f"Unsupported report format: {self.report_format}")
                return None

            logger.info("Report generation successful.")
            return report_content

        except Exception as e:
            logger.exception(f"An error occurred during report generation: {e}")
            return None

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(level=logging.DEBUG)
# 
#     # Placeholder results from different evaluation steps
#     mock_results = {
#         "accuracy_metrics": {"precision": 0.85, "recall": 0.82, "f1_score": 0.835, "accuracy": 0.90},
#         "bias_metrics": {"demographic_parity_difference": 0.08, "equal_opportunity_difference": 0.05},
#         "insight_metrics": {"novelty_score": 0.7, "actionability_score": 0.6},
#         "relevance_metrics": {"rougeL": 0.48, "bleu": 35.2},
#         "explainability_summary": [
#             "Feature 'prior_policy_outcome' has highest importance.",
#             "Counterfactual: Changing 'region' to 'West' increases predicted cost."
#         ],
#         "benchmarking": {"vs_baseline_accuracy": "+15%", "vs_expert_agreement": "Moderate"}
#     }
# 
#     print("\n--- Report Generation Examples ---")
# 
#     # Markdown Report
#     md_reporter = ReportGenerator(report_format='markdown', report_title="Policy Analysis Model Evaluation")
#     md_report = md_reporter.generate_report(mock_results)
#     if md_report:
#         print("\n--- MARKDOWN REPORT ---")
#         print(md_report)
#         # You could save this to a file: with open("report.md", "w") as f: f.write(md_report)
# 
#     # JSON Report
#     json_reporter = ReportGenerator(report_format='json')
#     json_report = json_reporter.generate_report(mock_results)
#     if json_report:
#         print("\n--- JSON REPORT ---")
#         print(json_report)
#         # Save to file: with open("report.json", "w") as f: f.write(json_report)
# 
#     # Text Report
#     text_reporter = ReportGenerator(report_format='text', report_title="Simple Text Evaluation Summary")
#     text_report = text_reporter.generate_report(mock_results)
#     if text_report:
#         print("\n--- TEXT REPORT ---")
#         print(text_report)
#         # Save to file: with open("report.txt", "w") as f: f.write(text_report)

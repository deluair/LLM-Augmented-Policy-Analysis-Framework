"""
Handles alerting based on evaluation results.

This module defines components to monitor evaluation metrics and trigger
alerts (e.g., email, Slack notifications, logging warnings) when certain
conditions or thresholds are met. Examples include performance degradation,
high bias detection, or significant drift from benchmarks.
"""

import logging
from typing import Dict, Any, List, Optional, Callable

# Placeholder for potential notification library integration
# import smtplib
# from slack_sdk import WebClient

logger = logging.getLogger(__name__)

class AlertingSystem:
    """
    Monitors evaluation results and triggers alerts based on predefined rules.
    """

    def __init__(
        self,
        alert_rules: List[Dict[str, Any]],
        notification_channels: Optional[List[str]] = None, # e.g., ['email', 'slack', 'log']
        **kwargs
    ):
        """
        Initializes the AlertingSystem.

        Args:
            alert_rules (List[Dict[str, Any]]): A list of rules defining alert conditions.
                Each rule could be a dictionary specifying the metric, threshold,
                comparison operator (e.g., '<', '>', '=='), severity, etc.
                Example rule:
                {
                    "metric_path": "accuracy_metrics.f1_score",
                    "condition": "<",
                    "threshold": 0.7,
                    "severity": "critical",
                    "message": "F1 Score dropped below threshold!"
                }
            notification_channels (Optional[List[str]]): List of channels to send alerts to.
                                                         Defaults to ['log'].
            **kwargs: Additional configuration for notification channels (e.g., email server, Slack token).
        """
        self.alert_rules = alert_rules
        self.notification_channels = notification_channels if notification_channels else ['log']
        self.kwargs = kwargs # Store API keys, endpoints etc.
        logger.info(f"AlertingSystem initialized with {len(alert_rules)} rules. Channels: {self.notification_channels}")

        # Placeholder for initializing notification clients (e.g., Slack)
        # if 'slack' in self.notification_channels:
        #     slack_token = kwargs.get('slack_token')
        #     if slack_token:
        #         self.slack_client = WebClient(token=slack_token)
        #     else:
        #         logger.warning("Slack channel specified but no token provided.")
        #         self.slack_client = None


    def _get_metric_value(self, results: Dict[str, Any], metric_path: str) -> Optional[Any]:
        """ Safely retrieves a nested metric value using dot notation. """
        keys = metric_path.split('.')
        value = results
        try:
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else: # Handle cases where path tries to access non-dict
                     return None
                if value is None: # Path doesn't exist fully
                    return None
            return value
        except Exception as e:
            logger.error(f"Error retrieving metric '{metric_path}': {e}")
            return None


    def _check_condition(self, value: Any, condition: str, threshold: Any) -> bool:
        """ Checks if a value meets a condition relative to a threshold. """
        try:
            # Basic comparison operators
            if condition == '<': return value < threshold
            if condition == '<=': return value <= threshold
            if condition == '>': return value > threshold
            if condition == '>=': return value >= threshold
            if condition == '==': return value == threshold
            if condition == '!=': return value != threshold
            # Add more complex conditions if needed (e.g., 'in', 'not in', 'abs_diff >')
            logger.warning(f"Unsupported condition operator: {condition}")
            return False
        except TypeError:
            logger.warning(f"Cannot compare value '{value}' ({type(value)}) with threshold '{threshold}' ({type(threshold)}) using condition '{condition}'.")
            return False
        except Exception as e:
            logger.error(f"Error checking condition '{condition}': {e}")
            return False


    def _send_alert(self, rule: Dict[str, Any], metric_value: Any):
        """ Sends alert notifications through configured channels. """
        message = rule.get('message', f"Alert triggered for rule on '{rule.get('metric_path')}'")
        severity = rule.get('severity', 'info').upper()
        alert_details = (
            f"[{severity}] {message} "
            f"(Metric: {rule.get('metric_path')}, "
            f"Value: {metric_value}, "
            f"Condition: {rule.get('condition')} {rule.get('threshold')})"
        )

        logger.info(f"Triggering alert: {alert_details}")

        if 'log' in self.notification_channels:
             log_level = getattr(logging, severity, logging.WARNING) # Map severity to logging level
             logger.log(log_level, f"ALERT: {alert_details}")

        if 'email' in self.notification_channels:
            logger.warning("Email notification channel selected but not implemented.")
            # Placeholder: Add email sending logic using smtplib or another library
            # print(f"SIMULATING EMAIL ALERT: {alert_details}")
            # raise NotImplementedError("Email notification not implemented.")

        if 'slack' in self.notification_channels:
            logger.warning("Slack notification channel selected but not implemented.")
            # Placeholder: Add Slack messaging logic using slack_sdk
            # if self.slack_client:
            #    try:
            #        channel = self.kwargs.get('slack_channel', '#alerts')
            #        self.slack_client.chat_postMessage(channel=channel, text=alert_details)
            #        logger.info(f"Alert sent to Slack channel {channel}.")
            #    except Exception as e:
            #        logger.error(f"Failed to send Slack alert: {e}")
            # else:
            #    logger.error("Cannot send Slack alert: client not initialized (missing token?).")
            # print(f"SIMULATING SLACK ALERT: {alert_details}")
            # raise NotImplementedError("Slack notification not implemented.")

        # Add other channels as needed


    def check_and_trigger_alerts(self, evaluation_results: Dict[str, Any]):
        """
        Checks evaluation results against all alert rules and triggers alerts if conditions are met.

        Args:
            evaluation_results (Dict[str, Any]): The dictionary containing evaluation results,
                                                  structured similarly to input for ReportGenerator.
        """
        logger.debug("Checking evaluation results against alert rules...")
        alerts_triggered = 0
        for rule in self.alert_rules:
            metric_path = rule.get('metric_path')
            condition = rule.get('condition')
            threshold = rule.get('threshold')

            if not all([metric_path, condition, threshold is not None]):
                logger.warning(f"Skipping invalid alert rule: {rule}. Missing required fields.")
                continue

            metric_value = self._get_metric_value(evaluation_results, metric_path)

            if metric_value is None:
                logger.debug(f"Metric '{metric_path}' not found in results for rule: {rule}")
                continue # Metric not present, cannot evaluate rule

            if self._check_condition(metric_value, condition, threshold):
                self._send_alert(rule, metric_value)
                alerts_triggered += 1

        logger.info(f"Alert check completed. {alerts_triggered} alerts triggered.")


# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(level=logging.DEBUG)
# 
#     # Define alert rules
#     rules = [
#         {
#             "metric_path": "accuracy_metrics.accuracy",
#             "condition": "<",
#             "threshold": 0.85,
#             "severity": "warning",
#             "message": "Model accuracy has fallen below acceptable threshold."
#         },
#         {
#             "metric_path": "bias_metrics.demographic_parity_difference",
#             "condition": ">",
#             "threshold": 0.15,
#             "severity": "critical",
#             "message": "High demographic parity difference detected, indicating potential bias."
#         },
#         {
#             "metric_path": "relevance_metrics.bleu", # Example: metric not present in results
#             "condition": "<",
#             "threshold": 30.0,
#             "severity": "info",
#             "message": "BLEU score is lower than expected."
#         },
#         {
#             "metric_path": "operational.latency_ms", # Example: metric needs adding to results
#             "condition": ">",
#             "threshold": 500,
#             "severity": "warning",
#         }
#     ]
# 
#     # Mock evaluation results
#     results_good = {
#         "accuracy_metrics": {"accuracy": 0.90, "f1_score": 0.88},
#         "bias_metrics": {"demographic_parity_difference": 0.05},
#         "operational": {"latency_ms": 350}
#     }
#     results_bad = {
#         "accuracy_metrics": {"accuracy": 0.82, "f1_score": 0.75},
#         "bias_metrics": {"demographic_parity_difference": 0.18},
#          "operational": {"latency_ms": 600}
#     }
# 
#     # Initialize alerting system (using only log channel for example)
#     # To use Slack, add 'slack' to channels and provide 'slack_token' and optionally 'slack_channel' in kwargs
#     alerter = AlertingSystem(alert_rules=rules, notification_channels=['log'])#, slack_token='xoxb-your-token', slack_channel='#policy-alerts')
# 
#     print("\n--- Checking Good Results (Expect No Alerts) ---")
#     alerter.check_and_trigger_alerts(results_good)
# 
#     print("\n--- Checking Bad Results (Expect Alerts) ---")
#     alerter.check_and_trigger_alerts(results_bad)
# 
#     print("\n--- Checking Results with Missing Metrics ---")
#     alerter.check_and_trigger_alerts({"accuracy_metrics": {"accuracy": 0.95}}) # bias metric missing

"""
Functions for calculating accuracy-related metrics.

These metrics typically compare system outputs against a ground truth or reference set.
Examples include precision, recall, F1-score, accuracy, etc., potentially adapted
for specific policy analysis tasks (e.g., entity extraction accuracy, claim verification).
"""

import logging
from typing import List, Any, Tuple, Dict, Optional

# Add imports for plotting and confusion matrix calculation
import numpy as np
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import confusion_matrix as sk_confusion_matrix
    _PLOT_LIBS_AVAILABLE = True
except ImportError:
    _PLOT_LIBS_AVAILABLE = False
    # Optional: Log a warning if libraries are missing
    # logging.warning("Plotting libraries (matplotlib, seaborn, scikit-learn) not found. Confusion matrix plot will not be generated.")

logger = logging.getLogger(__name__)

def _calculate_confusion_matrix_counts(
    predictions: List[Any],
    ground_truths: List[Any],
    positive_label: Any = 1,
    negative_label: Any = 0
) -> Tuple[int, int, int, int]:
    """
    Calculates counts for True Positives (TP), False Positives (FP),
    True Negatives (TN), and False Negatives (FN).

    Assumes binary classification context by default (1=positive, 0=negative).

    Args:
        predictions (List[Any]): The list of predicted labels.
        ground_truths (List[Any]): The list of actual true labels.
        positive_label (Any): The label considered as 'positive'. Defaults to 1.
        negative_label (Any): The label considered as 'negative'. Defaults to 0.

    Returns:
        Tuple[int, int, int, int]: Counts for (TP, FP, TN, FN).
    """
    if len(predictions) != len(ground_truths):
        logger.error("Length mismatch between predictions and ground truths.")
        raise ValueError("Predictions and ground truths must have the same length.")

    tp = fp = tn = fn = 0
    for pred, true in zip(predictions, ground_truths):
        if pred == positive_label and true == positive_label:
            tp += 1
        elif pred == positive_label and true == negative_label:
            fp += 1
        elif pred == negative_label and true == negative_label:
            tn += 1
        elif pred == negative_label and true == positive_label:
            fn += 1
        # Can add handling for labels other than positive/negative if needed
        # else:
        #     logger.warning(f"Unexpected label pair found: pred={pred}, true={true}")

    logger.debug(f"Confusion Matrix Counts: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    return tp, fp, tn, fn


def calculate_precision(
    predictions: List[Any],
    ground_truths: List[Any],
    positive_label: Any = 1,
    zero_division: float = 0.0
) -> Optional[float]:
    """
    Calculates the precision score.

    Precision = TP / (TP + FP)
    Measures the proportion of positively predicted instances that were actually positive.
    High precision means fewer false positives.

    Args:
        predictions (List[Any]): The list of predicted labels.
        ground_truths (List[Any]): The list of actual true labels.
        positive_label (Any): The label considered as 'positive'. Defaults to 1.
        zero_division (float): Value to return if the denominator (TP + FP) is zero. Defaults to 0.0.

    Returns:
        Optional[float]: The precision score, or None if calculation fails.
    """
    try:
        tp, fp, _, _ = _calculate_confusion_matrix_counts(predictions, ground_truths, positive_label)
        denominator = tp + fp
        if denominator == 0:
            logger.warning(f"Precision calculation resulted in zero division (TP={tp}, FP={fp}). Returning {zero_division}.")
            return zero_division
        precision = tp / denominator
        logger.info(f"Calculated Precision: {precision:.4f}")
        return precision
    except ValueError as e:
        logger.error(f"Precision calculation failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during precision calculation: {e}")
        return None


def calculate_recall(
    predictions: List[Any],
    ground_truths: List[Any],
    positive_label: Any = 1,
    zero_division: float = 0.0
) -> Optional[float]:
    """
    Calculates the recall score (Sensitivity or True Positive Rate).

    Recall = TP / (TP + FN)
    Measures the proportion of actual positive instances that were correctly predicted.
    High recall means fewer false negatives.

    Args:
        predictions (List[Any]): The list of predicted labels.
        ground_truths (List[Any]): The list of actual true labels.
        positive_label (Any): The label considered as 'positive'. Defaults to 1.
        zero_division (float): Value to return if the denominator (TP + FN) is zero. Defaults to 0.0.

    Returns:
        Optional[float]: The recall score, or None if calculation fails.
    """
    try:
        tp, _, _, fn = _calculate_confusion_matrix_counts(predictions, ground_truths, positive_label)
        denominator = tp + fn
        if denominator == 0:
            logger.warning(f"Recall calculation resulted in zero division (TP={tp}, FN={fn}). Returning {zero_division}.")
            return zero_division
        recall = tp / denominator
        logger.info(f"Calculated Recall: {recall:.4f}")
        return recall
    except ValueError as e:
        logger.error(f"Recall calculation failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during recall calculation: {e}")
        return None


def calculate_f1_score(
    predictions: List[Any],
    ground_truths: List[Any],
    positive_label: Any = 1,
    zero_division: float = 0.0
) -> Optional[float]:
    """
    Calculates the F1 score.

    F1 = 2 * (Precision * Recall) / (Precision + Recall)
    The harmonic mean of precision and recall. Provides a balance between the two.

    Args:
        predictions (List[Any]): The list of predicted labels.
        ground_truths (List[Any]): The list of actual true labels.
        positive_label (Any): The label considered as 'positive'. Defaults to 1.
        zero_division (float): Value to return if precision + recall is zero. Defaults to 0.0.

    Returns:
        Optional[float]: The F1 score, or None if calculation fails.
    """
    try:
        precision = calculate_precision(predictions, ground_truths, positive_label, zero_division)
        recall = calculate_recall(predictions, ground_truths, positive_label, zero_division)

        if precision is None or recall is None:
            logger.error("F1 score calculation failed because precision or recall calculation failed.")
            return None

        denominator = precision + recall
        if denominator == 0:
            logger.warning(f"F1 score calculation resulted in zero division (Precision={precision}, Recall={recall}). Returning {zero_division}.")
            return zero_division

        f1 = 2 * (precision * recall) / denominator
        logger.info(f"Calculated F1 Score: {f1:.4f}")
        return f1
    except ValueError as e: # Already handled by precision/recall, but for safety
         logger.error(f"F1 score calculation failed: {e}")
         return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during F1 score calculation: {e}")
        return None


def calculate_accuracy(
    predictions: List[Any],
    ground_truths: List[Any]
) -> Optional[float]:
    """
    Calculates the accuracy score.

    Accuracy = (TP + TN) / (TP + FP + TN + FN)
    Measures the proportion of all instances that were correctly predicted.

    Args:
        predictions (List[Any]): The list of predicted labels.
        ground_truths (List[Any]): The list of actual true labels.

    Returns:
        Optional[float]: The accuracy score, or None if calculation fails.
    """
    try:
        tp, fp, tn, fn = _calculate_confusion_matrix_counts(predictions, ground_truths) # Use default labels
        total = tp + fp + tn + fn
        if total == 0:
            logger.warning("Accuracy calculation: No instances found. Returning 0.0.")
            return 0.0 # Or perhaps None or 1.0 depending on desired behavior for empty input
        accuracy = (tp + tn) / total
        logger.info(f"Calculated Accuracy: {accuracy:.4f}")
        return accuracy
    except ValueError as e:
        logger.error(f"Accuracy calculation failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during accuracy calculation: {e}")
        return None


def plot_confusion_matrix(
    y_true: List[Any],
    y_pred: List[Any],
    labels: Optional[List[str]] = None,
    filename: str = "confusion_matrix.png",
    title: str = "Confusion Matrix",
) -> Optional[str]:
    """
    Generates and saves a confusion matrix plot using seaborn and matplotlib.

    Requires matplotlib, seaborn, and scikit-learn to be installed.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        labels: Optional list of class labels for the axes.
                If None, uses unique values from y_true and y_pred.
        filename: Path to save the plot image.
        title: Title for the plot.

    Returns:
        Optional[str]: The filename where the plot was saved, or None if 
                       plotting libraries are unavailable or an error occurred.
    """
    if not _PLOT_LIBS_AVAILABLE:
        logger.warning(
            "Plotting libraries not available. Skipping confusion matrix generation."
        )
        return None

    try:
        cm = sk_confusion_matrix(y_true, y_pred)
        if labels is None:
            labels = np.unique(np.concatenate((y_true, y_pred))).astype(str)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            cbar=False,
        )
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(title)
        plt.tight_layout() # Adjust layout to prevent labels overlapping
        plt.savefig(filename)
        plt.close() # Close the figure to free memory
        logger.info(f"Confusion matrix plot saved to {filename}")
        return filename
    except Exception as e:
        logger.exception(f"Failed to generate confusion matrix plot: {e}")
        return None

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(level=logging.DEBUG)
#
#     preds = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
#     truths = [1, 1, 1, 0, 0, 1, 0, 1, 0, 1]
#     # TP = 4 (1->1)
#     # FP = 2 (1->0)
#     # TN = 2 (0->0)
#     # FN = 2 (0->1)
#     # Total = 10
#
#     print("\n--- Accuracy Metrics Calculation Examples ---")
#     precision = calculate_precision(preds, truths) # Expected: 4 / (4 + 2) = 0.666...
#     recall = calculate_recall(preds, truths)       # Expected: 4 / (4 + 2) = 0.666...
#     f1 = calculate_f1_score(preds, truths)         # Expected: 2 * (0.666 * 0.666) / (0.666 + 0.666) = 0.666...
#     accuracy = calculate_accuracy(preds, truths)   # Expected: (4 + 2) / 10 = 0.6
#
#     print(f"Precision: {precision}")
#     print(f"Recall: {recall}")
#     print(f"F1 Score: {f1}")
#     print(f"Accuracy: {accuracy}")
#
#     print("\n--- Zero Division Examples ---")
#     preds_zero_pos = [0, 0]
#     truths_zero_pos = [0, 0]
#     # TP=0, FP=0, TN=2, FN=0
#     print(f"Precision (Zero Denom): {calculate_precision(preds_zero_pos, truths_zero_pos)}") # TP+FP = 0
#     print(f"Recall (Zero Denom): {calculate_recall(preds_zero_pos, truths_zero_pos)}")     # TP+FN = 0
#     print(f"F1 (Zero Precision/Recall): {calculate_f1_score(preds_zero_pos, truths_zero_pos)}")
#     print(f"Accuracy: {calculate_accuracy(preds_zero_pos, truths_zero_pos)}") # (0+2)/2 = 1.0
#
#     print("\n--- Different Labels Example ---")
#     preds_str = ['yes', 'no', 'yes', 'no']
#     truths_str = ['yes', 'yes', 'no', 'no']
#     # TP=1 ('yes'->'yes'), FP=1 ('yes'->'no'), TN=1 ('no'->'no'), FN=1 ('no'->'yes')
#     precision_str = calculate_precision(preds_str, truths_str, positive_label='yes', zero_division=0.0) # 1 / (1+1) = 0.5
#     print(f"Precision ('yes' as positive): {precision_str}")
#     recall_str = calculate_recall(preds_str, truths_str, positive_label='yes', zero_division=0.0) # 1 / (1+1) = 0.5
#     print(f"Recall ('yes' as positive): {recall_str}")
#     accuracy_str = calculate_accuracy(preds_str, truths_str) # Needs _calculate_confusion_matrix adjusted or a different approach
#     # Note: calculate_accuracy uses default 0/1. For generic labels, might need direct comparison:
#     # accuracy_direct = sum(p == t for p, t in zip(preds_str, truths_str)) / len(preds_str) # (1+1)/4 = 0.5
#     # print(f"Accuracy (Direct Comparison): {accuracy_direct}")
#     # Or adjust _calculate_confusion_matrix to handle arbitrary pairs if needed for accuracy logic.
#     # Current accuracy function expects 0/1 or compatible.

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, f1_score,
    matthews_corrcoef, precision_score, recall_score, roc_auc_score, roc_curve,
)


def threshold_at_target_fpr(y_true, y_probability, target_fpr: float) -> float:
    if not 0 < target_fpr < 1:
        raise ValueError("target_fpr must be between 0 and 1")
    y_true = np.asarray(y_true)
    y_probability = np.asarray(y_probability)
    if len(set(y_true)) < 2:
        raise ValueError("Threshold validation requires both classes")
    false_positive_rates, true_positive_rates, thresholds = roc_curve(
        y_true, y_probability
    )
    eligible = np.flatnonzero(false_positive_rates <= target_fpr)
    best = eligible[np.argmax(true_positive_rates[eligible])]
    return float(thresholds[best])


def classification_metrics(y_true, y_pred, y_probability) -> dict[str, float | None]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_probability = np.asarray(y_probability)
    negatives = y_true == 0
    false_positive_rate = float(np.mean(y_pred[negatives] == 1)) if negatives.any() else None
    roc_auc = float(roc_auc_score(y_true, y_probability)) if len(set(y_true)) == 2 else None
    pr_auc = (
        float(average_precision_score(y_true, y_probability))
        if len(set(y_true)) == 2
        else None
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "false_positive_rate": false_positive_rate,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier_score": float(brier_score_loss(y_true, y_probability)),
    }

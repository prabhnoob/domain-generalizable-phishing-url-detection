"""Security-relevant evaluation metrics."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, brier_score_loss, f1_score, matthews_corrcoef,
    precision_score, recall_score, roc_auc_score,
)


def classification_metrics(y_true, y_pred, y_probability) -> dict[str, float | None]:
    """Return the metrics promised in the proposal."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_probability = np.asarray(y_probability)
    negatives = y_true == 0
    false_positive_rate = float(np.mean(y_pred[negatives] == 1)) if negatives.any() else None
    roc_auc = float(roc_auc_score(y_true, y_probability)) if len(set(y_true)) == 2 else None
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "false_positive_rate": false_positive_rate,
        "roc_auc": roc_auc,
        "brier_score": float(brier_score_loss(y_true, y_probability)),
    }

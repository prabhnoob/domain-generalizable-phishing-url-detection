import pytest

from phishing_url_detection.metrics import classification_metrics, threshold_at_target_fpr


def test_threshold_is_selected_from_requested_validation_fpr():
    labels = [0, 0, 0, 0, 1, 1]
    probabilities = [0.1, 0.2, 0.3, 0.4, 0.35, 0.9]
    threshold = threshold_at_target_fpr(labels, probabilities, target_fpr=0.01)
    assert threshold == pytest.approx(0.9)


def test_metrics_include_pr_auc():
    metrics = classification_metrics([0, 0, 1, 1], [0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    assert metrics["pr_auc"] == pytest.approx(1.0)

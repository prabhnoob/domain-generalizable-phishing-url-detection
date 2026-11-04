"""Training, evaluation, and artifact writing."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .metrics import classification_metrics, threshold_at_target_fpr
from .models import build_model
from .reproducibility import set_global_seed
from .splits import DatasetSplit, make_split, with_groups
from .domains import canonicalize_url


def run_experiment(
    frame: pd.DataFrame, *, model_name: str, split_method: str,
    output_dir: str | Path, test_size: float = 0.2, seed: int = 474,
    external_test: pd.DataFrame | None = None, canonicalize: bool = False,
    feature_view: str = "full", target_fpr: float = 0.01,
) -> dict:
    """Train one baseline and save reproducible results."""
    set_global_seed(seed)
    frame = frame.copy()
    if canonicalize:
        frame["url"] = frame["url"].map(canonicalize_url)
    if external_test is not None:
        external_test = external_test.copy()
        if canonicalize:
            external_test["url"] = external_test["url"].map(canonicalize_url)
    external_rows_before_filter = None
    external_invalid_rows_removed = None
    external_overlap_rows_removed = None
    if external_test is None:
        split = make_split(frame, split_method, test_size=test_size, seed=seed)
    else:
        grouped_train = with_groups(frame).reset_index(drop=True)
        external_rows_before_filter = len(external_test)
        grouped_test = with_groups(external_test, drop_invalid=True).reset_index(drop=True)
        external_invalid_rows_removed = external_rows_before_filter - len(grouped_test)
        external_valid_rows = len(grouped_test)
        train_domains = set(grouped_train["registrable_domain"])
        grouped_test = grouped_test[
            ~grouped_test["registrable_domain"].isin(train_domains)
        ].reset_index(drop=True)
        external_overlap_rows_removed = external_valid_rows - len(grouped_test)
        if grouped_test.empty:
            raise ValueError("No external rows remain after domain-overlap removal")
        split = DatasetSplit(
            train=grouped_train, test=grouped_test,
            method="cross_source",
        )

    validation_method = split_method if external_test is None else "domain"
    validation = make_split(
        split.train, validation_method, test_size=0.2, seed=seed
    )
    threshold_model = build_model(model_name, seed=seed, feature_view=feature_view)
    threshold_model.fit(validation.train["url"], validation.train["label"])
    validation_probabilities = threshold_model.predict_proba(validation.test["url"])[:, 1]
    decision_threshold = threshold_at_target_fpr(
        validation.test["label"], validation_probabilities, target_fpr
    )

    model = build_model(model_name, seed=seed, feature_view=feature_view)
    model.fit(split.train["url"], split.train["label"])
    probabilities = model.predict_proba(split.test["url"])[:, 1]
    predictions = (probabilities >= decision_threshold).astype(int)
    metrics = classification_metrics(split.test["label"], predictions, probabilities)
    result = {
        "model": model_name, "split": split.method, "seed": seed,
        "canonicalize": canonicalize, "feature_view": feature_view,
        "target_fpr": target_fpr,
        "decision_threshold": decision_threshold,
        "threshold_validation_method": validation_method,
        "threshold_validation_rows": len(validation.test),
        "train_rows": len(split.train), "test_rows": len(split.test),
        "metrics": metrics,
    }
    if external_test is not None:
        result["external_rows_before_domain_filter"] = external_rows_before_filter
        result["external_invalid_rows_removed"] = external_invalid_rows_removed
        result["external_overlap_rows_removed"] = external_overlap_rows_removed

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "metrics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    prediction_frame = split.test[["url", "label"]].copy()
    prediction_frame["prediction"] = predictions
    prediction_frame["phishing_probability"] = probabilities
    prediction_frame.to_csv(destination / "predictions.csv", index=False)
    joblib.dump(model, destination / "model.joblib")
    return result

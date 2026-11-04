"""Training, evaluation, and artifact writing."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .metrics import classification_metrics
from .models import build_model
from .splits import DatasetSplit, make_split


def run_experiment(
    frame: pd.DataFrame, *, model_name: str, split_method: str,
    output_dir: str | Path, test_size: float = 0.2, seed: int = 474,
    external_test: pd.DataFrame | None = None,
) -> dict:
    """Train one baseline and save reproducible results."""
    if external_test is None:
        split = make_split(frame, split_method, test_size=test_size, seed=seed)
    else:
        split = DatasetSplit(
            train=frame.reset_index(drop=True), test=external_test.reset_index(drop=True),
            method="cross_source",
        )

    model = build_model(model_name, seed=seed)
    model.fit(split.train["url"], split.train["label"])
    predictions = model.predict(split.test["url"])
    probabilities = model.predict_proba(split.test["url"])[:, 1]
    metrics = classification_metrics(split.test["label"], predictions, probabilities)
    result = {
        "model": model_name, "split": split.method, "seed": seed,
        "train_rows": len(split.train), "test_rows": len(split.test),
        "metrics": metrics,
    }

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

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .domains import canonicalize_url, registrable_domain
from .metrics import classification_metrics, threshold_at_target_fpr
from .models import build_model
from .reproducibility import set_global_seed
from .splits import DatasetSplit, make_split, with_groups


def cross_source_split(train: pd.DataFrame, external: pd.DataFrame):
    train = with_groups(train)
    test = with_groups(external, drop_invalid=True)
    invalid_removed = len(external) - len(test)

    seen_sites = set(train["registrable_domain"])
    unseen = ~test["registrable_domain"].isin(seen_sites)
    overlap_removed = len(test) - int(unseen.sum())
    test = test[unseen].reset_index(drop=True)
    if test.empty:
        raise ValueError("No external rows remain after domain-overlap removal")

    report = {
        "external_rows_before_domain_filter": len(external),
        "external_invalid_rows_removed": invalid_removed,
        "external_overlap_rows_removed": overlap_removed,
    }
    return DatasetSplit(train=train, test=test, method="cross_source"), report


def choose_threshold(train: pd.DataFrame, method: str, model_name: str,
                     seed: int, feature_view: str, target_fpr: float):
    inner = make_split(train, method, test_size=0.2, seed=seed)
    model = build_model(model_name, seed=seed, feature_view=feature_view)
    model.fit(inner.train["url"], inner.train["label"])
    scores = model.predict_proba(inner.test["url"])[:, 1]
    threshold = threshold_at_target_fpr(inner.test["label"], scores, target_fpr)
    return threshold, len(inner.test)


def save_outputs(folder: str | Path, result: dict, test: pd.DataFrame,
                 predictions, probabilities, model) -> None:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    (folder / "metrics.json").write_text(text, encoding="utf-8")

    rows = test[["url", "label"]].copy()
    rows["prediction"] = predictions
    rows["phishing_probability"] = probabilities
    rows.to_csv(folder / "predictions.csv", index=False)
    joblib.dump(model, folder / "model.joblib")


def run_experiment(
    frame: pd.DataFrame, *, model_name: str, split_method: str,
    output_dir: str | Path, test_size: float = 0.2, seed: int = 474,
    external_test: pd.DataFrame | None = None, canonicalize: bool = False,
    feature_view: str = "full", target_fpr: float = 0.01,
) -> dict:
    set_global_seed(seed)

    frame = frame.copy()
    if canonicalize:
        frame["url"] = frame["url"].map(canonicalize_url)
    if external_test is not None:
        external_test = external_test.copy()
        if canonicalize:
            external_test["url"] = external_test["url"].map(canonicalize_url)

    report = {}
    if external_test is None:
        split = make_split(frame, split_method, test_size=test_size, seed=seed)
        threshold_method = split_method
    else:
        split, report = cross_source_split(frame, external_test)
        threshold_method = "domain"

    threshold, validation_rows = choose_threshold(
        split.train, threshold_method, model_name, seed, feature_view, target_fpr
    )

    model = build_model(model_name, seed=seed, feature_view=feature_view)
    model.fit(split.train["url"], split.train["label"])
    probabilities = model.predict_proba(split.test["url"])[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    result = {
        "model": model_name, "split": split.method, "seed": seed,
        "canonicalize": canonicalize, "feature_view": feature_view,
        "target_fpr": target_fpr, "decision_threshold": threshold,
        "threshold_validation_method": threshold_method,
        "threshold_validation_rows": validation_rows,
        "train_rows": len(split.train), "test_rows": len(split.test),
        "metrics": classification_metrics(split.test["label"], predictions, probabilities),
        **report,
    }
    save_outputs(output_dir, result, split.test, predictions, probabilities, model)
    return result


def predict_urls(model_dir: str | Path, urls: list[str]) -> list[dict]:
    folder = Path(model_dir)
    model = joblib.load(folder / "model.joblib")
    run = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
    threshold = float(run["decision_threshold"])

    inputs = [canonicalize_url(u) if run.get("canonicalize") else u for u in urls]
    probabilities = model.predict_proba(inputs)[:, 1]

    rows = []
    for url, p in zip(urls, probabilities):
        rows.append({
            "url": url,
            "registrable_domain": registrable_domain(url),
            "phishing_probability": float(p),
            "decision_threshold": threshold,
            "prediction": int(p >= threshold),
        })
    return rows

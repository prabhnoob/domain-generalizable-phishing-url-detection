from pathlib import Path

import pandas as pd

from phishing_url_detection.experiment import run_experiment


def _dataset() -> pd.DataFrame:
    rows = []
    for index in range(30):
        rows.append({"url": f"https://safe{index}.com/articles/{index}", "label": 0})
        rows.append({
            "url": f"http://verify-account-{index}.example/login?id={index}",
            "label": 1,
        })
    return pd.DataFrame(rows)


def test_experiment_writes_reproducible_artifacts(tmp_path: Path):
    result = run_experiment(
        _dataset(), model_name="lexical", split_method="domain",
        output_dir=tmp_path, test_size=0.25, seed=474,
    )
    assert result["split"] == "domain"
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "predictions.csv").exists()
    assert (tmp_path / "model.joblib").exists()


def test_cross_source_removes_training_domain_overlap(tmp_path: Path):
    training = _dataset()
    external = pd.DataFrame([
        {"url": "https://safe0.com/new", "label": 0},
        {"url": "https://unseen-safe.net/home", "label": 0},
        {"url": "https://unseen-phish.net/verify-account", "label": 1},
        {"url": "http://[broken-ipv6/login", "label": 1},
    ])
    result = run_experiment(
        training, model_name="lexical", split_method="domain",
        output_dir=tmp_path, seed=474, external_test=external,
    )
    assert result["split"] == "cross_source"
    assert result["external_rows_before_domain_filter"] == 4
    assert result["external_invalid_rows_removed"] == 1
    assert result["external_overlap_rows_removed"] == 1
    assert result["test_rows"] == 2

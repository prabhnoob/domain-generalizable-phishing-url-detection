from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .domains import canonicalize_url
from .experiment import cross_source_split
from .features import LexicalURLFeatures
from .metrics import classification_metrics, threshold_at_target_fpr
from .splits import make_split


GRIDS = {
    "knn": ("k", [1, 3, 5, 11, 21]),
    "random_forest": ("max_depth", [5, 10, 20, None]),
    "lexical_lr": ("C", [0.01, 0.1, 1, 10, 100]),
    "char_lr": ("C", [0.1, 1, 10]),
}

GROUP_COLUMN = {
    "random": None,
    "host": "host",
    "domain": "registrable_domain",
    "cross_source": "registrable_domain",
}


def new_model(name: str, value, seed: int):
    if name == "knn":
        return make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=value))
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=100, max_depth=value, random_state=seed, n_jobs=-1
        )
    model = LogisticRegression(
        C=value, class_weight="balanced", max_iter=1000,
        random_state=seed, solver="liblinear",
    )
    if name == "lexical_lr":
        return make_pipeline(StandardScaler(), model)
    return model


def char_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char", lowercase=True, ngram_range=(3, 5), min_df=1,
        max_features=50_000, sublinear_tf=True,
    )


def make_folds(dev: pd.DataFrame, setup: str, seed: int, n_folds: int = 5) -> list:
    group_column = GROUP_COLUMN[setup]
    labels = dev["label"].to_numpy()
    if group_column is None:
        folds = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
        return list(folds.split(dev, labels))
    folds = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return list(folds.split(dev, labels, groups=dev[group_column]))


def feature_sets(urls, lexical, train_idx, test_idx) -> dict:
    vectorizer = char_vectorizer()
    char_train = vectorizer.fit_transform(urls[train_idx])
    char_test = vectorizer.transform(urls[test_idx])
    return {
        "lexical": (lexical[train_idx], lexical[test_idx]),
        "char": (char_train, char_test),
    }


def score_fold(y_true, scores) -> dict[str, float]:
    predictions = (scores >= 0.5).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, scores),
        "pr_auc": average_precision_score(y_true, scores),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0),
    }


def cross_validate(dev: pd.DataFrame, setup: str, seed: int):
    urls = dev["url"].to_numpy()
    labels = dev["label"].to_numpy()
    lexical = LexicalURLFeatures().transform(urls)
    out_of_fold = {}
    fold_rows = []

    for fold, (train_idx, test_idx) in enumerate(make_folds(dev, setup, seed), start=1):
        features = feature_sets(urls, lexical, train_idx, test_idx)
        for name, (parameter, values) in GRIDS.items():
            x_train, x_test = features["char" if name == "char_lr" else "lexical"]
            for value in values:
                model = new_model(name, value, seed)
                model.fit(x_train, labels[train_idx])
                scores = model.predict_proba(x_test)[:, 1]
                key = (name, str(value))
                out_of_fold.setdefault(key, np.zeros(len(dev)))[test_idx] = scores
                row = {"setup": setup, "model": name, "parameter": parameter,
                       "value": str(value), "fold": fold}
                row.update(score_fold(labels[test_idx], scores))
                fold_rows.append(row)
        print(f"{setup}: fold {fold} done", flush=True)

    return pd.DataFrame(fold_rows), out_of_fold


def summarize_folds(fold_table: pd.DataFrame) -> pd.DataFrame:
    columns = ["roc_auc", "pr_auc", "f1", "precision", "recall"]
    keys = ["setup", "model", "parameter", "value"]
    summary = fold_table.groupby(keys, sort=False)[columns].agg(["mean", "std"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    return summary.reset_index()


def best_values(summary: pd.DataFrame) -> dict[str, str]:
    best = {}
    for name in GRIDS:
        rows = summary[summary["model"] == name]
        best[name] = rows.loc[rows["roc_auc_mean"].idxmax(), "value"]
    return best


def parse_value(name: str, text: str):
    for value in GRIDS[name][1]:
        if str(value) == text:
            return value
    raise ValueError(f"Unknown value {text} for {name}")


def final_test(dev: pd.DataFrame, test: pd.DataFrame, best: dict, out_of_fold: dict,
               seed: int, target_fpr: float) -> list[dict]:
    dev_urls = dev["url"].to_numpy()
    test_urls = test["url"].to_numpy()
    dev_labels = dev["label"].to_numpy()
    test_labels = test["label"].to_numpy()

    lexical = LexicalURLFeatures()
    vectorizer = char_vectorizer()
    features = {
        "lexical": (lexical.transform(dev_urls), lexical.transform(test_urls)),
        "char": (vectorizer.fit_transform(dev_urls), vectorizer.transform(test_urls)),
    }

    results = []
    for name, text in best.items():
        threshold = threshold_at_target_fpr(
            dev_labels, out_of_fold[(name, text)], target_fpr
        )
        x_train, x_test = features["char" if name == "char_lr" else "lexical"]
        model = new_model(name, parse_value(name, text), seed)
        model.fit(x_train, dev_labels)
        scores = model.predict_proba(x_test)[:, 1]
        predictions = (scores >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(test_labels, predictions, labels=[0, 1]).ravel()
        results.append({
            "model": name, "parameter": GRIDS[name][0], "best_value": text,
            "decision_threshold": threshold,
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
            **classification_metrics(test_labels, predictions, scores),
        })
    return results


def make_dev_test(frame: pd.DataFrame, setup: str, external, seed: int):
    if setup == "cross_source":
        split, report = cross_source_split(frame, external)
        return split.train, split.test, report
    split = make_split(frame, setup, seed=seed)
    return split.train, split.test, {}


def run_setup(frame: pd.DataFrame, setup: str, *, external: pd.DataFrame | None = None,
              canonicalize: bool = False, seed: int = 474, target_fpr: float = 0.01):
    dev, test, report = make_dev_test(frame, setup, external, seed)
    dev = dev.reset_index(drop=True)
    test = test.reset_index(drop=True)
    if canonicalize:
        dev["url"] = dev["url"].map(canonicalize_url)
        test["url"] = test["url"].map(canonicalize_url)
    fold_table, out_of_fold = cross_validate(dev, setup, seed)
    summary = summarize_folds(fold_table)
    best = best_values(summary)
    results = final_test(dev, test, best, out_of_fold, seed, target_fpr)

    name = setup + ("_canonical" if canonicalize else "")
    summary["setup"] = name
    fold_table["setup"] = name
    for row in results:
        row.update({"setup": name, "dev_rows": len(dev), "test_rows": len(test),
                    "test_phishing_rate": float(test["label"].mean()), **report})
    return fold_table, summary, results


def save_tables(folder: str | Path, fold_table: pd.DataFrame, summary: pd.DataFrame,
                results: list[dict]) -> None:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    fold_table.to_csv(folder / "cv_folds.csv", index=False, float_format="%.6f")
    summary.to_csv(folder / "cv_summary.csv", index=False, float_format="%.6f")
    pd.DataFrame(results).to_csv(folder / "test_results.csv", index=False,
                                 float_format="%.6f")
    text = json.dumps(results, indent=2, sort_keys=True) + "\n"
    (folder / "test_results.json").write_text(text, encoding="utf-8")

from __future__ import annotations

from pathlib import Path

import pandas as pd


URL_COLUMNS = ("url", "URL", "Url")
LABEL_COLUMNS = ("label", "Label", "class", "Class")


def _drop_conflicting_labels(frame: pd.DataFrame) -> pd.DataFrame:
    conflicts = frame.groupby("url")["label"].transform("nunique") > 1
    return frame.loc[~conflicts].reset_index(drop=True)


def _find_column(columns: pd.Index, candidates: tuple[str, ...], kind: str) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"Could not find a {kind} column; tried {candidates}")


def load_url_csv(path: str | Path, *, phiusiil_labels: bool = False) -> pd.DataFrame:
    frame = pd.read_csv(path)
    url_col = _find_column(frame.columns, URL_COLUMNS, "URL")
    label_col = _find_column(frame.columns, LABEL_COLUMNS, "label")
    result = frame[[url_col, label_col]].rename(
        columns={url_col: "url", label_col: "label"}
    )
    result["url"] = result["url"].astype(str).str.strip()
    result["label"] = pd.to_numeric(result["label"], errors="raise").astype(int)
    if phiusiil_labels:
        result["label"] = 1 - result["label"]
    invalid = set(result["label"].unique()) - {0, 1}
    if invalid:
        raise ValueError(f"Labels must be binary; found {sorted(invalid)}")
    result = result[result["url"].ne("")].drop_duplicates().reset_index(drop=True)
    return _drop_conflicting_labels(result)


def load_kaggle_malicious_urls(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["url", "type"])
    frame = frame[frame["type"].isin(["benign", "phishing"])].copy()
    frame["label"] = frame["type"].map({"benign": 0, "phishing": 1}).astype(int)
    frame["url"] = frame["url"].astype(str).str.strip()
    result = (
        frame.loc[frame["url"].ne(""), ["url", "label"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return _drop_conflicting_labels(result)

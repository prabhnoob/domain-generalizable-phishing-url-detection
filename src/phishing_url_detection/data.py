"""Dataset loading and label normalization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


URL_COLUMNS = ("url", "URL", "Url")
LABEL_COLUMNS = ("label", "Label", "class", "Class")


def _find_column(columns: pd.Index, candidates: tuple[str, ...], kind: str) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"Could not find a {kind} column; tried {candidates}")


def load_url_csv(path: str | Path, *, phiusiil_labels: bool = False) -> pd.DataFrame:
    """Load a URL CSV and return canonical ``url`` and ``label`` columns.

    Project labels are always 1 for phishing and 0 for legitimate. Set
    ``phiusiil_labels`` for the original UCI file, whose labels are reversed.
    """
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
    return result[result["url"].ne("")].drop_duplicates().reset_index(drop=True)

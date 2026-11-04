"""Deterministic evaluation splits with explicit leakage checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from .domains import normalized_host, registrable_domain


@dataclass(frozen=True)
class DatasetSplit:
    train: pd.DataFrame
    test: pd.DataFrame
    method: str
    group_column: str | None = None


def with_groups(frame: pd.DataFrame, *, drop_invalid: bool = False) -> pd.DataFrame:
    grouped = frame.copy()
    grouped["host"] = grouped["url"].map(normalized_host)
    grouped["registrable_domain"] = grouped["url"].map(registrable_domain)
    invalid = grouped[["host", "registrable_domain"]].eq("").any(axis=1)
    if drop_invalid:
        return grouped.loc[~invalid].reset_index(drop=True)
    if invalid.any():
        raise ValueError("Every URL must have a valid host and registrable domain")
    return grouped


def make_split(
    frame: pd.DataFrame,
    method: str,
    *,
    test_size: float = 0.2,
    seed: int = 474,
) -> DatasetSplit:
    """Create one of the proposal's within-source evaluation splits."""
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")
    grouped = with_groups(frame)
    methods = {
        "random": None,
        "host": "host",
        "domain": "registrable_domain",
    }
    if method not in methods:
        raise ValueError(f"Unknown split method {method!r}; choose from {sorted(methods)}")

    group_column = methods[method]
    indices = np.arange(len(grouped))
    if group_column is None:
        train_idx, test_idx = train_test_split(
            indices,
            test_size=test_size,
            random_state=seed,
            stratify=grouped["label"],
        )
    else:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_idx, test_idx = next(
            splitter.split(grouped, grouped["label"], groups=grouped[group_column])
        )

    split = DatasetSplit(
        train=grouped.iloc[train_idx].reset_index(drop=True),
        test=grouped.iloc[test_idx].reset_index(drop=True),
        method=method,
        group_column=group_column,
    )
    assert_no_group_leakage(split)
    return split


def assert_no_group_leakage(split: DatasetSplit) -> None:
    """Raise if a grouped split shares a host/domain across train and test."""
    if split.group_column is None:
        return
    train_groups = set(split.train[split.group_column])
    test_groups = set(split.test[split.group_column])
    overlap = train_groups & test_groups
    if overlap:
        sample = sorted(overlap)[:5]
        raise AssertionError(
            f"{split.method} split leaks {len(overlap)} groups; examples: {sample}"
        )

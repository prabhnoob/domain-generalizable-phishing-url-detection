"""URL-only lexical features for the interpretable baseline."""

from __future__ import annotations

import math
import re
from collections import Counter
from urllib.parse import urlsplit

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from .domains import normalized_host


SUSPICIOUS_TOKENS = (
    "account", "auth", "bank", "confirm", "login", "password",
    "secure", "signin", "update", "verify",
)


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def lexical_features(url: str) -> list[float]:
    """Extract URL-string features without loading the webpage."""
    value = str(url).strip().lower()
    parsed = urlsplit(value if "://" in value else f"http://{value}")
    host = normalized_host(value)
    path = parsed.path or ""
    query = parsed.query or ""
    tokens = [token for token in re.split(r"[^a-z0-9]+", value) if token]
    return [
        len(value), len(host), len(path), len(query),
        sum(char.isdigit() for char in value), value.count("."),
        value.count("-"), value.count("@"), value.count("%"),
        value.count("="), value.count("/"), len(tokens),
        sum(token in SUSPICIOUS_TOKENS for token in tokens),
        float(host.replace(".", "").isdigit()),
        float(parsed.scheme == "https"), _entropy(value),
    ]


class LexicalURLFeatures(TransformerMixin, BaseEstimator):
    """Scikit-learn transformer for lexical URL features."""

    def fit(self, X, y=None):  # noqa: N803 - sklearn API
        return self

    def transform(self, X):  # noqa: N803 - sklearn API
        return np.asarray([lexical_features(url) for url in X], dtype=float)

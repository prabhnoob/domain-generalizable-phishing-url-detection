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


def entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def lexical_features(url: str) -> list[float]:
    url = str(url).strip().lower()
    parts = urlsplit(url if "://" in url else "http://" + url)
    host = normalized_host(url)
    path = parts.path or ""
    query = parts.query or ""
    words = [w for w in re.split(r"[^a-z0-9]+", url) if w]

    return [
        len(url),
        len(host),
        len(path),
        len(query),
        sum(ch.isdigit() for ch in url),
        url.count("."),
        url.count("-"),
        url.count("@"),
        url.count("%"),
        url.count("="),
        url.count("/"),
        len(words),
        sum(w in SUSPICIOUS_TOKENS for w in words),
        float(host.replace(".", "").isdigit()),
        float(parts.scheme == "https"),
        entropy(url),
    ]


class LexicalURLFeatures(TransformerMixin, BaseEstimator):

    def __init__(self, view: str = "full"):
        if view not in {"full", "host"}:
            raise ValueError("view must be 'full' or 'host'")
        self.view = view

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        urls = [normalized_host(u) for u in X] if self.view == "host" else X
        return np.asarray([lexical_features(u) for u in urls], dtype=float)

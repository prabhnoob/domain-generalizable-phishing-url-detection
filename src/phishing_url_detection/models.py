"""Baseline model definitions from the project background review."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .features import LexicalURLFeatures


def build_model(name: str, *, seed: int = 474, feature_view: str = "full") -> Pipeline:
    """Build an interpretable lexical or learned character baseline."""
    if name == "char" and feature_view != "full":
        raise ValueError("feature_view applies only to the lexical model")
    classifier = LogisticRegression(
        class_weight="balanced", max_iter=1000, random_state=seed, solver="liblinear"
    )
    if name == "lexical":
        return Pipeline([
            ("features", LexicalURLFeatures(view=feature_view)),
            ("scale", StandardScaler()),
            ("classifier", classifier),
        ])
    if name == "char":
        return Pipeline([
            ("features", TfidfVectorizer(
                analyzer="char", lowercase=True, ngram_range=(3, 5), min_df=1,
                max_features=50_000, sublinear_tf=True,
            )),
            ("classifier", classifier),
        ])
    raise ValueError("Unknown model; choose 'lexical' or 'char'")

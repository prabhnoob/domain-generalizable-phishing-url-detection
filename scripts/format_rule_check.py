from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from phishing_url_detection.data import load_kaggle_malicious_urls, load_url_csv
from phishing_url_detection.domains import canonicalize_url
from phishing_url_detection.experiment import cross_source_split
from phishing_url_detection.metrics import classification_metrics
from phishing_url_detection.splits import make_split


def bare_homepage(url):
    text = str(url).strip().lower()
    return text.startswith("https://www.") and "/" not in canonicalize_url(text)


def rule_scores(test):
    predictions = np.array([0 if bare_homepage(u) else 1 for u in test["url"]])
    return classification_metrics(test["label"], predictions, predictions)


def main():
    phiusiil = load_url_csv("data/raw/PhiUSIIL_Phishing_URL_Dataset.csv",
                            phiusiil_labels=True)
    kaggle = load_kaggle_malicious_urls(
        "data/raw/kaggle-malicious-urls/malicious_phish.csv"
    )
    tests = {
        "random": make_split(phiusiil, "random").test,
        "host": make_split(phiusiil, "host").test,
        "domain": make_split(phiusiil, "domain").test,
        "cross_source": cross_source_split(phiusiil, kaggle)[0].test,
    }
    results = {name: rule_scores(test) for name, test in tests.items()}
    for name, test in tests.items():
        safe = test[test["label"] == 0]["url"]
        results[name]["safe_bare_homepage_share"] = float(safe.map(bare_homepage).mean())
    output = Path("evaluation/m4/format_rule.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

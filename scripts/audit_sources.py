from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from phishing_url_detection.data import load_kaggle_malicious_urls, load_url_csv


ROOT = Path(__file__).resolve().parents[1]


def _summary(frame: pd.DataFrame) -> dict:
    schemes = frame["url"].astype(str).str.contains("://", regex=False)
    class_rows = {}
    for label, name in ((0, "legitimate"), (1, "phishing")):
        selected = frame[frame["label"] == label]
        has_scheme = selected["url"].astype(str).str.contains("://", regex=False)
        class_rows[name] = {
            "rows": len(selected),
            "share": len(selected) / len(frame),
            "scheme_less_rows": int((~has_scheme).sum()),
            "scheme_less_share": float((~has_scheme).mean()),
        }

    label_counts = frame.groupby("url")["label"].nunique()
    return {
        "rows": len(frame),
        "scheme_less_rows": int((~schemes).sum()),
        "scheme_less_share": float((~schemes).mean()),
        "urls_with_conflicting_labels": int((label_counts > 1).sum()),
        "classes": class_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phiusiil",
        type=Path,
        default=ROOT / "data" / "raw" / "PhiUSIIL_Phishing_URL_Dataset.csv",
    )
    parser.add_argument(
        "--kaggle",
        type=Path,
        default=ROOT / "data" / "raw" / "kaggle-malicious-urls" / "malicious_phish.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "evaluation" / "reports" / "source_data_audit.json",
    )
    args = parser.parse_args()

    raw_phiusiil_columns = pd.read_csv(args.phiusiil, nrows=0).columns.tolist()
    raw_kaggle_columns = pd.read_csv(args.kaggle, nrows=0).columns.tolist()
    raw_phiusiil = pd.read_csv(args.phiusiil, usecols=["URL", "label"]).rename(
        columns={"URL": "url"}
    )
    raw_kaggle = pd.read_csv(args.kaggle, usecols=["url", "type"])
    raw_kaggle = raw_kaggle[raw_kaggle["type"].isin(["benign", "phishing"])]
    raw_kaggle["label"] = raw_kaggle["type"].map({"benign": 0, "phishing": 1})
    phiusiil_conflicts = int(
        (raw_phiusiil.groupby("url")["label"].nunique() > 1).sum()
    )
    kaggle_conflicts = int(
        (raw_kaggle.groupby("url")["label"].nunique() > 1).sum()
    )
    phiusiil_summary = _summary(load_url_csv(args.phiusiil, phiusiil_labels=True))
    kaggle_summary = _summary(load_kaggle_malicious_urls(args.kaggle))
    phiusiil_summary["raw_urls_with_conflicting_labels"] = phiusiil_conflicts
    kaggle_summary["raw_urls_with_conflicting_labels"] = kaggle_conflicts
    report = {
        "phiusiil": phiusiil_summary,
        "kaggle_binary_subset": kaggle_summary,
        "timestamp_columns": {
            "phiusiil": [name for name in raw_phiusiil_columns if "time" in name.lower()],
            "kaggle": [name for name in raw_kaggle_columns if "time" in name.lower()],
        },
        "notes": [
            "The audit uses project labels: 0=legitimate, 1=phishing.",
            "Scheme-less counts support the proposed canonicalization ablation; no model result is changed here.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

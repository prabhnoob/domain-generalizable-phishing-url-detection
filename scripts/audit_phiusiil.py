from __future__ import annotations

import argparse
import json
from pathlib import Path

from phishing_url_detection.data import load_url_csv
from phishing_url_detection.splits import make_split


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        default=ROOT / "data" / "raw" / "PhiUSIIL_Phishing_URL_Dataset.csv",
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=ROOT / "evaluation" / "reports" / "phiusiil_data_audit.json",
        type=Path,
    )
    parser.add_argument("--seed", type=int, default=474)
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    frame = load_url_csv(args.data, phiusiil_labels=True)
    split = make_split(frame, "domain", test_size=args.test_size, seed=args.seed)
    train_domains = set(split.train["registrable_domain"])
    test_domains = set(split.test["registrable_domain"])
    report = {
        "source": "UCI PhiUSIIL dataset 967",
        "project_label_mapping": {"0": "legitimate", "1": "phishing"},
        "seed": args.seed,
        "test_size": args.test_size,
        "rows_after_url_label_deduplication": len(frame),
        "class_counts": {
            "legitimate": int((frame["label"] == 0).sum()),
            "phishing": int((frame["label"] == 1).sum()),
        },
        "domain_split": {
            "train_rows": len(split.train),
            "test_rows": len(split.test),
            "train_registrable_domains": len(train_domains),
            "test_registrable_domains": len(test_domains),
            "overlapping_registrable_domains": len(train_domains & test_domains),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse

import pandas as pd

from phishing_url_detection.data import load_kaggle_malicious_urls, load_url_csv
from phishing_url_detection.evaluation import run_setup, save_tables
from phishing_url_detection.reproducibility import set_global_seed


SETUPS = ["random", "host", "domain", "cross_source", "cross_source_canonical"]


def parse_args():
    parser = argparse.ArgumentParser(description="Milestone 4 evaluation")
    parser.add_argument("--data", default="data/raw/PhiUSIIL_Phishing_URL_Dataset.csv")
    parser.add_argument("--phiusiil-labels", action="store_true")
    parser.add_argument("--external",
                        default="data/raw/kaggle-malicious-urls/malicious_phish.csv")
    parser.add_argument("--external-format", choices=("standard", "kaggle"),
                        default="kaggle")
    parser.add_argument("--setups", nargs="+", choices=SETUPS, default=SETUPS)
    parser.add_argument("--output", default="evaluation/m4")
    parser.add_argument("--seed", type=int, default=474)
    return parser.parse_args()


def load_external(args):
    if args.external_format == "kaggle":
        return load_kaggle_malicious_urls(args.external)
    return load_url_csv(args.external)


def main():
    args = parse_args()
    set_global_seed(args.seed)
    frame = load_url_csv(args.data, phiusiil_labels=args.phiusiil_labels)
    external = None
    if any(s.startswith("cross") for s in args.setups):
        external = load_external(args)

    folds, summaries, results = [], [], []
    for setup in args.setups:
        canonical = setup.endswith("_canonical")
        fold_table, summary, rows = run_setup(
            frame, setup.removesuffix("_canonical"), external=external,
            canonicalize=canonical, seed=args.seed,
        )
        folds.append(fold_table)
        summaries.append(summary)
        results.extend(rows)
        save_tables(f"{args.output}/{setup}", fold_table, summary, rows)

    save_tables(args.output, pd.concat(folds), pd.concat(summaries), results)


if __name__ == "__main__":
    main()

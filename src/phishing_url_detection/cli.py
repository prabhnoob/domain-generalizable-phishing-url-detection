from __future__ import annotations

import argparse
import json

from .data import load_kaggle_malicious_urls, load_url_csv
from .experiment import predict_urls, run_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Leakage-resistant phishing URL evaluation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate", help="train and evaluate one baseline")
    evaluate.add_argument("--data", required=True)
    evaluate.add_argument("--model", choices=("lexical", "char"), required=True)
    evaluate.add_argument("--split", choices=("random", "host", "domain"), default="domain")
    evaluate.add_argument("--output", required=True)
    evaluate.add_argument("--test-size", type=float, default=0.2)
    evaluate.add_argument("--seed", type=int, default=474)
    evaluate.add_argument("--phiusiil-labels", action="store_true")
    evaluate.add_argument("--external", help="optional second-source test CSV")
    evaluate.add_argument("--external-phiusiil-labels", action="store_true")
    evaluate.add_argument("--canonicalize", action="store_true")
    evaluate.add_argument("--feature-view", choices=("full", "host"), default="full")
    evaluate.add_argument("--target-fpr", type=float, default=0.01)
    evaluate.add_argument(
        "--external-format",
        choices=("standard", "kaggle-malicious-urls"),
        default="standard",
    )
    predict = subparsers.add_parser(
        "predict", help="score URLs with a model saved by 'evaluate'"
    )
    predict.add_argument(
        "--model-dir", required=True,
        help="folder containing model.joblib and metrics.json from 'evaluate'",
    )
    predict.add_argument("--url", action="append", required=True, help="URL to score")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "predict":
        for row in predict_urls(args.model_dir, args.url):
            print(json.dumps(row, sort_keys=True))
        return 0
    frame = load_url_csv(args.data, phiusiil_labels=args.phiusiil_labels)
    external = None
    if args.external:
        if args.external_format == "kaggle-malicious-urls":
            external = load_kaggle_malicious_urls(args.external)
        else:
            external = load_url_csv(
                args.external, phiusiil_labels=args.external_phiusiil_labels
            )
    result = run_experiment(
        frame, model_name=args.model, split_method=args.split, output_dir=args.output,
        test_size=args.test_size, seed=args.seed, external_test=external,
        canonicalize=args.canonicalize, feature_view=args.feature_view,
        target_fpr=args.target_fpr,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

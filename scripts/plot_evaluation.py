from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


MODELS = [
    ("knn", "kNN: k"),
    ("random_forest", "Random forest: max depth"),
    ("lexical_lr", "Lexical LR: C"),
    ("char_lr", "Character LR: C"),
]

SETUPS = [
    ("random", "Random folds", "#2a78d6", "o"),
    ("domain", "Domain-grouped folds", "#eb6834", "s"),
]


def kaggle_auc(results, model):
    row = results[(results["setup"] == "cross_source") & (results["model"] == model)]
    return float(row["roc_auc"].iloc[0])


def plot_grid(summary, results, output):
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False,
                         "axes.spines.right": False})
    figure, axes = plt.subplots(1, 4, figsize=(7.0, 1.4), sharey=True)
    for axis, (model, title) in zip(axes, MODELS):
        for setup, label, color, marker in SETUPS:
            rows = summary[(summary["model"] == model) & (summary["setup"] == setup)]
            values = rows["value"].astype(str).replace({"None": "none"})
            axis.plot(values, rows["roc_auc_mean"], color=color, marker=marker,
                      markersize=4, linewidth=1.5, label=label)
        axis.set_title(title)
        axis.text(0.97, 0.06, f"Kaggle test AUC = {kaggle_auc(results, model):.2f}",
                  transform=axis.transAxes, ha="right", fontsize=6.5, color="#555555")
        axis.grid(axis="y", color="#e1e0d9", linewidth=0.5)
    axes[0].set_ylabel("Mean 5-fold CV ROC-AUC")
    axes[0].set_ylim(0.990, 1.0)
    axes[3].legend(frameon=False, loc="center", fontsize=6.5)
    figure.tight_layout(pad=0.3)
    figure.savefig(output, bbox_inches="tight")
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description="Plot Milestone 4 CV results")
    parser.add_argument("--results", default="evaluation/m4")
    args = parser.parse_args()
    folder = Path(args.results)
    summary = pd.read_csv(folder / "cv_summary.csv", keep_default_na=False)
    results = pd.read_csv(folder / "test_results.csv")
    plot_grid(summary, results, folder / "cv_roc_auc.pdf")


if __name__ == "__main__":
    main()

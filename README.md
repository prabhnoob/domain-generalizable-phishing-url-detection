# Domain-Generalizable Phishing URL Detection

This project tests phishing URL detectors under realistic data splits. Its main rule is that a registrable domain (eTLD+1), such as `example.com`, must not appear in both training and test data.

## Current implementation

- deterministic random, host-disjoint, and registrable-domain-disjoint splits;
- explicit checks that grouped splits have no leakage;
- consistent labels (`1 = phishing`, `0 = legitimate`);
- lexical-feature and character n-gram logistic-regression baselines;
- accuracy, precision, recall, F1, macro-F1, MCC, false-positive rate, ROC-AUC, and Brier score;
- a small public-safe sample dataset for quick tests;
- automated unit tests.

## Repository structure

```text
src/phishing_url_detection/  Python package
tests/                       automated tests
data/sample/                 tiny quickstart dataset
data/raw/                    downloaded source datasets (not committed)
data/processed/              prepared datasets (not committed)
output/                      models and experiment results (not committed)
scripts/                     dataset download helpers
proposal/                    Milestone 1 report
background/                  Milestone 2 report
```

## Setup

Python 3.12 is recommended.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run tests

```powershell
python -m pytest
```

## Quick start

Run a complete deterministic sample experiment:

```powershell
python -m phishing_url_detection evaluate `
  --data data/sample/urls.csv `
  --model lexical `
  --split random `
  --test-size 0.25 `
  --output output/quickstart
```

The command writes `metrics.json`, `predictions.csv`, and `model.joblib`.

Available models are `lexical` (hand-made URL features) and `char` (character TF-IDF). Available within-source splits are `random`, `host`, and `domain`.

## Dataset

The main dataset is the [UCI PhiUSIIL Phishing URL dataset](https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset), containing 235,795 rows. UCI stores `1 = legitimate` and `0 = phishing`; our loader reverses these values to match the proposal (`1 = phishing`, `0 = legitimate`). Raw datasets are intentionally excluded from Git.

Download the official UCI file:

```powershell
python scripts/download_phiusiil.py
```

Then run the main domain-disjoint experiment:

```powershell
python -m phishing_url_detection evaluate `
  --data data/raw/PhiUSIIL_Phishing_URL_Dataset.csv `
  --phiusiil-labels `
  --model lexical `
  --split domain `
  --output output/phiusiil-lexical-domain
```

## Reproducibility

All randomized operations use an explicit seed. The default project seed is `474`.

## Authors

Prabhnoor Singh, Divraj Singh, and Dilraj Gulati — University of Victoria.

# Domain-Generalizable Phishing URL Detection

This project tests phishing URL detectors under realistic data splits. Its main rule is that a registrable domain (eTLD+1), such as `example.com`, must not appear in both training and test data.

## Current implementation

- deterministic random, host-disjoint, and registrable-domain-disjoint splits;
- explicit checks that grouped splits have no leakage;
- consistent labels (`1 = phishing`, `0 = legitimate`);
- a small public-safe sample dataset for quick tests;
- automated unit tests.

Model training and full-dataset experiments are being added incrementally.

## Repository structure

```text
src/phishing_url_detection/  Python package
tests/                       automated tests
data/sample/                 tiny quickstart dataset
data/raw/                    downloaded source datasets (not committed)
data/processed/              prepared datasets (not committed)
output/                      models and experiment results (not committed)
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

## Dataset

The main dataset is the [UCI PhiUSIIL Phishing URL dataset](https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset), containing 235,795 rows. UCI stores `1 = legitimate` and `0 = phishing`; our loader reverses these values to match the proposal (`1 = phishing`, `0 = legitimate`). Raw datasets are intentionally excluded from Git.

## Reproducibility

All randomized operations use an explicit seed. The default project seed is `474`.

## Authors

Prabhnoor Singh, Divraj Singh, and Dilraj Gulati — University of Victoria.

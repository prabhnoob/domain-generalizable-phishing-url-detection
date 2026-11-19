# Domain-Generalizable Phishing URL Detection

## Intro

This project tests whether phishing URL classifiers still work on registered domains and data sources that were not present during training. It compares random, host-disjoint, registrable-domain-disjoint, and strict cross-source evaluation.

The implementation contains our two URL-only models and, since Milestone 4, two baselines:

- `lexical`: 16 hand-made URL features, standardization, and logistic regression;
- `char`: character 3–5-gram TF-IDF and logistic regression;
- `knn` and `random_forest`: baselines on the same 16 lexical features (Milestone 4 evaluation only).

Project repository: <https://github.com/prabhnoob/domain-generalizable-phishing-url-detection>

## Illustrative Sample

Given `https://paypal.login-fraud.top/verify`, the system maps the URL to its registrable domain `login-fraud.top`, extracts URL-only features, and returns a phishing probability and a 0/1 label. For domain-disjoint testing, every URL under one registrable domain must appear entirely in either training or testing, never both.

After the quick start, this command reproduces the running example in the Milestone 3 report:

```sh
python -m phishing_url_detection predict --model-dir output/quickstart/char --url https://paypal.login-fraud.top/verify
```

Expected output (seed `474`; the last decimal places of the probability can differ slightly between computers):

```json
{"decision_threshold": 0.5340868955592305, "phishing_probability": 0.5840662465956155, "prediction": 1, "registrable_domain": "login-fraud.top", "url": "https://paypal.login-fraud.top/verify"}
```

The small hand-made file `data/sample/urls.csv` (48 URLs; phishing rows use reserved `.example`, `.test`, `.invalid` names and documentation IP ranges) exists only to verify installation and execution. It is not used as experimental evidence.

## Prerequisite

- Python 3.12
- Internet access only when downloading public datasets
- Approximately 150 MB of free space for the raw datasets and more for saved models

The project uses `numpy`, `pandas`, `scikit-learn`, `tldextract`, `joblib`, `matplotlib` (figure only), and `pytest`. Raw datasets are excluded from Git. The main operating point targets a 1% false-positive rate, with its decision threshold chosen on validation data only.

## Installation Guide

Clone the repository:

```sh
git clone https://github.com/prabhnoob/domain-generalizable-phishing-url-detection
cd domain-generalizable-phishing-url-detection
```

macOS or Linux:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Conda:

```powershell
conda env create -f environment.yml
conda activate phishing-url-detection
python -m pip install -e .
```

Download the official UCI PhiUSIIL and Kaggle data:

```powershell
python scripts/download_phiusiil.py
python scripts/download_kaggle_malicious_urls.py
```

## Quick Start

On Windows PowerShell:

```powershell
.\scripts\quickstart.ps1
```

On Linux or macOS:

```sh
bash scripts/quickstart.sh
```

The scripts create an isolated environment, install the project, run all tests, train both baselines on the sample with a registrable-domain-disjoint split and seed `474`, print `output/quickstart/{lexical,char}/metrics.json`, and score the report's running example with the saved character model. Running them twice gives identical files.

To run the main domain-disjoint experiment manually:

```powershell
python -m phishing_url_detection evaluate `
  --data data/raw/PhiUSIIL_Phishing_URL_Dataset.csv `
  --phiusiil-labels `
  --model lexical `
  --split domain `
  --output output/phiusiil-lexical-domain
```

To score new URLs with a saved run (model and validation threshold are reused):

```powershell
python -m phishing_url_detection predict --model-dir output/phiusiil-lexical-domain --url https://example.com/login
```

To run strict cross-source evaluation:

```powershell
python -m phishing_url_detection evaluate `
  --data data/raw/PhiUSIIL_Phishing_URL_Dataset.csv `
  --phiusiil-labels `
  --model lexical `
  --external data/raw/kaggle-malicious-urls/malicious_phish.csv `
  --external-format kaggle-malicious-urls `
  --output output/phiusiil-to-kaggle-lexical
```

## Milestone 4 Evaluation

This runs the full Milestone 4 study: random, host-disjoint, domain-disjoint, PhiUSIIL → Kaggle, and PhiUSIIL → Kaggle with cleaned URLs. For each setup it holds out 20% as the final test set, runs 5-fold cross-validation on the rest (the same folds for every model), picks each model's hyperparameter by mean CV ROC-AUC, picks the 1% false-positive threshold from out-of-fold predictions, and scores the test set once. It needs both datasets in `data/raw/` and takes about 50 minutes on 2 CPUs.

```sh
python scripts/run_evaluation.py --phiusiil-labels
python scripts/format_rule_check.py
python scripts/plot_evaluation.py
```

Outputs go to `evaluation/m4/`: `cv_folds.csv` (every fold, model, and value), `cv_summary.csv` (CV mean and standard deviation), `test_results.csv`/`.json` (final test metrics and confusion matrices), `format_rule.json`, and `cv_roc_auc.pdf` (the report figure). Running the study twice gives identical CSV tables.

Final test results (hyperparameter picked by CV; full metrics in `evaluation/m4/test_results.csv`):

| Model | Random ROC-AUC / F1 | Domain-disjoint ROC-AUC / F1 | PhiUSIIL → Kaggle ROC-AUC / F1 / FPR |
|---|---|---|---|
| kNN | 0.997 / 0.992 | 0.997 / 0.994 | 0.500 / 0.303 / 1.000 |
| Random forest | 0.998 / 0.989 | 0.998 / 0.992 | 0.520 / 0.303 / 1.000 |
| Lexical LR | 0.996 / 0.988 | 0.997 / 0.989 | 0.404 / 0.240 / 0.985 |
| Character LR | 0.999 / 0.992 | 0.999 / 0.993 | 0.441 / 0.303 / 1.000 |
| Format rule (no training) | – / 0.995 | – / 0.994 | – / 0.302 / 1.000 |

Every safe PhiUSIIL URL is a bare `https://www.` homepage, so a one-line rule matches the trained models inside PhiUSIIL and fails the same way on Kaggle. The Milestone 4 report is in `evaluation/4_Evaluation.pdf`.

## Milestone 3 Results

Only results stored under `evaluation/results/` are reported here.

| Model | Evaluation | Test rows | F1 | MCC | ROC-AUC | False-positive rate |
|---|---|---:|---:|---:|---:|---:|
| Lexical LR | PhiUSIIL domain-disjoint | 51,435 | 0.9936282243 | 0.9879317585 | 0.9968413596 | 0.0007064773 |
| Lexical LR | PhiUSIIL → Kaggle, strict domain filter | 428,140 | 0.2484560764 | -0.1358217679 | 0.4056098999 | 0.8217726370 |

These results are preliminary. They were recorded with an earlier version of the code that used a fixed 0.5 decision threshold, before validation-based threshold selection was added, and are kept unchanged as a record. They are superseded by the Milestone 4 results above. Reverse cross-source (Kaggle → PhiUSIIL) and Kaggle within-source experiments were not run.

New runs also report PR-AUC and record their decision threshold. Optional `--canonicalize` and `--feature-view host` flags support the approved representation ablations. They must write to new output/result names and must not overwrite the recorded results above.

## Citation

If this course project is used as a baseline, cite the repository and the original datasets. A final paper citation is not available yet.

- Prasad, A. and Chandra, S. (2024). PhiUSIIL Phishing URL Dataset, UCI Machine Learning Repository.
- Kaggle dataset `sid321axn/malicious-urls-dataset`, used as the independent cross-source collection.

## License

Project source code is licensed under the MIT License; see `LICENSE`. The UCI dataset is CC BY 4.0 and the selected Kaggle dataset is CC0. Those dataset licenses remain separate from the software license.

## Project Structure

```text
src/phishing_url_detection/  implementation package
tests/                       automated tests
scripts/                     download, audit, and quickstart scripts
data/sample/                 synthetic execution sample
data/raw/                    source datasets; ignored by Git
data/preprocessed/           generated data; ignored by Git
evaluation/reports/          data and split audits
evaluation/results/          Milestone 3 preliminary results
evaluation/m4/               Milestone 4 results and figure
evaluation/4_Evaluation.*    Milestone 4 report (evaluation)
output/                      models and row-level outputs; ignored by Git
proposal/                    Milestone 1
background/                  Milestone 2
solution/                    Milestone 3 report (proposed method)
```

## Authors

Prabhnoor Singh, Divraj Singh, and Dilraj Gulati — University of Victoria.

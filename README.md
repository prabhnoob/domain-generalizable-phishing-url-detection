# Domain-Generalizable Phishing URL Detection

## Intro

This project tests whether phishing URL classifiers still work on registered domains and data sources that were not present during training. It compares random, host-disjoint, registrable-domain-disjoint, and strict cross-source evaluation.

The implementation currently contains two URL-only baselines:

- `lexical`: 16 hand-made URL features, standardization, and logistic regression;
- `char`: character 3–5-gram TF-IDF and logistic regression.

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

The project uses `numpy`, `pandas`, `scikit-learn`, `tldextract`, `joblib`, and `pytest`. Raw datasets are excluded from Git. The main operating point targets a 1% false-positive rate, with its decision threshold chosen on validation data only.

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

## Results

Only results stored under `evaluation/results/` are reported here.

| Model | Evaluation | Test rows | F1 | MCC | ROC-AUC | False-positive rate |
|---|---|---:|---:|---:|---:|---:|
| Lexical LR | PhiUSIIL domain-disjoint | 51,435 | 0.9936282243 | 0.9879317585 | 0.9968413596 | 0.0007064773 |
| Lexical LR | PhiUSIIL → Kaggle, strict domain filter | 428,140 | 0.2484560764 | -0.1358217679 | 0.4056098999 | 0.8217726370 |

These results are preliminary. They were recorded with an earlier version of the code that used a fixed 0.5 decision threshold, before validation-based threshold selection was added; they will be re-run with the current code in Milestone 4. Random, host-disjoint, character-model, reverse cross-source, and Kaggle within-source experiments have not yet been recorded.

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
evaluation/results/          recorded aggregate experiment results
output/                      models and row-level outputs; ignored by Git
proposal/                    Milestone 1
background/                  Milestone 2
solution/                    Milestone 3 report (proposed method)
```

## Authors

Prabhnoor Singh, Divraj Singh, and Dilraj Gulati — University of Victoria.

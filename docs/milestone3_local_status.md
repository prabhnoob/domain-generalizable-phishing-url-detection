# Milestone 3 Local Status

This file records local, uncommitted work derived from the Nov. 4 prompt pack. It is not a submission document and has not been pushed.

## Implemented locally

- PowerShell and Bash quickstart scripts.
- Direct package list in `requirements.txt`.
- Python 3.12 Conda environment file.
- Central random/NumPy seed function using seed 474.
- Repeatability test comparing two complete `metrics.json` files.
- README sections required by the milestone manual.
- Source audit for class prevalence, scheme-less URLs, label conflicts, and timestamp columns.

## Model status

- Lexical logistic regression: implemented and trained.
- Character TF-IDF logistic regression: implemented, no recorded full-data result.
- Random forest: not implemented.
- XGBoost: not implemented.
- Character CNN: not implemented.

## Improvement status

- C1 canonicalization: audit completed; model change and ablation planned.
- C2 source-fingerprint classifier: planned.
- C3 host-only versus full-URL features: planned.
- C4 brand/subdomain/TLD features: planned; requires a cited brand list.
- C5 additional model families: planned; team must choose scope.
- C6 grouped hyperparameter selection: planned.
- C7 multi-source training: planned after C1–C6.
- C8 calibration and operating point: planned; target false-positive rate needs team choice.
- C9 PR-AUC, several seeds, confidence intervals: planned.
- C10 data hygiene: audit completed; conflicting-label removal and private-suffix policy planned.

## Confirmed by the local source audit

- PhiUSIIL has no scheme-less URLs after URL/label deduplication.
- After dropping six conflicting-label URLs, the Kaggle binary subset has 461,935 scheme-less rows out of 522,160 (88.47%).
- Kaggle legitimate rows are 91.73% scheme-less; phishing rows are 73.61% scheme-less.
- Kaggle phishing prevalence is 18.02% before invalid/domain-overlap filtering.
- Six exact Kaggle URLs occur with conflicting labels in the raw file; the loader now removes all rows for those URLs.
- Neither source exposes a timestamp column.

## Decisions made locally for team review

- MIT software license.
- Rename `data/processed` to `data/preprocessed`.
- Keep the lexical LR and character TF-IDF LR promised in the literature review; defer additional model families.
- Use a 1% false-positive-rate target chosen on domain-disjoint validation data.
- Approve C1, C2, C3, C6, C8, C9, and C10; defer the expansion items C4, C5 (extra models), and C7.

## Team decision still required

Identify the graduate student and final author order.

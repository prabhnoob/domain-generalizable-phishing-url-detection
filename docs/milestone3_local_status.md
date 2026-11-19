# Milestone 3 Status

This file records the state of the Milestone 3 implementation. It is a working note, not a submission document.

## Implemented

- PowerShell and Bash quickstart scripts.
- Direct package list in `requirements.txt`.
- Python 3.12 Conda environment file.
- Central random/NumPy seed function using seed 474.
- Repeatability test comparing two complete `metrics.json` files.
- `predict` command that scores new URLs with a saved model and its validation threshold.
- 48-URL synthetic sample used by the quickstart (reserved `.example`, `.test`, `.invalid` names and documentation IPs).
- README sections required by the milestone manual.
- Source audit for class prevalence, scheme-less URLs, label conflicts, and timestamp columns.

## Model status

- Lexical logistic regression: implemented and trained.
- Character TF-IDF logistic regression: implemented, no recorded full-data result.
- Random forest: not implemented.
- XGBoost: not implemented.
- Character CNN: not implemented.

## Improvement status

- C1 canonicalization: done (`--canonicalize`); test runs in Milestone 4.
- C2 source-fingerprint check: moved to Milestone 4.
- C3 host-only versus full-URL features: done (`--feature-view host`); test runs in Milestone 4.
- C4 brand/subdomain/TLD features: planned; requires a cited brand list.
- C5 additional model families: planned; team must choose scope.
- C6 grouped validation: done for the threshold; hyperparameter tuning planned.
- C7 multi-source training: planned after C1–C6.
- C8 operating point: done (1% false-positive rate, chosen on validation data); calibration planned.
- C9 PR-AUC: done; several seeds and confidence intervals planned.
- C10 data cleaning: done (URLs with both labels are removed; all `*.github.io` pages count as one site).

## Confirmed by the source audit

- PhiUSIIL has no scheme-less URLs after URL/label deduplication.
- After dropping six conflicting-label URLs, the Kaggle binary subset has 461,935 scheme-less rows out of 522,160 (88.47%).
- Kaggle legitimate rows are 91.73% scheme-less; phishing rows are 73.61% scheme-less.
- Kaggle phishing prevalence is 18.02% before invalid/domain-overlap filtering.
- Six exact Kaggle URLs occur with conflicting labels in the raw file; the loader now removes all rows for those URLs.
- Neither source exposes a timestamp column.

## Team decisions

- MIT software license.
- Rename `data/processed` to `data/preprocessed`.
- Keep the lexical LR and character TF-IDF LR promised in the literature review; defer additional model families.
- Use a 1% false-positive-rate target chosen on validation data only.
- Approve C1, C3, C6, C8, C9, and C10; move C2 to Milestone 4; defer C4, C5 (extra models), and C7.

## Team decision still required

Identify the graduate student and final author order.
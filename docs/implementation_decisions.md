# Milestone 3 Implementation Decisions

Team decisions made for Milestone 3.

## 1. Software license

Use the MIT License for project source code. It is short, permissive, and does not change the separate CC BY 4.0 and CC0 licenses of the two datasets. Dataset files remain excluded from Git.

## 2. Generated-data directory

Rename `data/processed` to `data/preprocessed` so the repository matches Appendix A of the milestone manual.

## 3. Models in Milestone 3

Implement and describe only the two model families promised in the literature review:

1. lexical URL features with logistic regression;
2. character 3–5-gram TF-IDF with logistic regression.

Random forest, XGBoost, and a character CNN are deferred. Adding them now would expand the claimed solution beyond the approved proposal and leave insufficient time for a fair four-split comparison.

## 4. Operating point

Use a target false-positive rate of 1%. Select the probability threshold using a validation subset of the training source only. The validation split uses the same split type as the test (domain for cross-source). Never choose or tune the threshold on the final within-source or cross-source test set. Continue reporting threshold-free ROC-AUC and PR-AUC alongside threshold-dependent metrics.

The 1% value is a team design target, not a claim that every deployment requires the same rate. It must be stated as such in the report.

## 5. C1–C10 scope

| Item | Decision | Milestone 3 scope |
|---|---|---|
| C1 | Approved | Add optional canonicalization and compare it as an ablation. |
| C2 | Moved to Milestone 4 | Audit how well lexical features distinguish PhiUSIIL from Kaggle. |
| C3 | Approved | Compare full-URL and host-only lexical views. |
| C4 | Deferred | Requires a defensible external brand list and changes the feature definition. |
| C5 | Partially approved | Complete the two promised LR baselines; defer RF, XGBoost, and CNN. |
| C6 | Approved | Use grouped validation (same split type as the test) for the threshold and later hyperparameter selection. |
| C7 | Deferred | Multi-source training changes the present train-on-PhiUSIIL evaluation design. |
| C8 | Approved | Select a 1% FPR threshold on validation data; calibration remains planned. |
| C9 | Approved | Add PR-AUC now; multi-seed runs and domain bootstrap remain planned. |
| C10 | Approved | Drop conflicting-label URLs, record removals, and document suffix/timestamp policy. |

## Non-negotiable evaluation rules

- Project labels remain `1 = phishing`, `0 = legitimate`.
- No registered domain may occur in both training and test data for domain-disjoint evaluation.
- Cross-source test rows sharing a registered domain with training are removed.
- Recorded result JSON files are never edited by hand or overwritten by a changed method.
- New method variants write new result files with explicit configuration fields.

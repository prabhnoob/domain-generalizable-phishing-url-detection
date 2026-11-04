# Domain-Generalizable Phishing URL Detection

This repository contains the course project milestones for evaluating phishing URL detectors under realistic, leakage-resistant data splits.

## Research problem

Random train/test splits can place closely related URLs from the same registered domain in both partitions, producing inflated estimates of real-world performance. This project studies whether a phishing URL classifier can generalize to previously unseen registered domains when evaluated using disjoint effective top-level domain plus one (eTLD+1) groups.

## Research objective

Given labeled URLs collected from multiple domains, learn a binary mapping from a URL to either phishing or benign while evaluating on domains excluded from training. The project will compare conventional random splitting with domain-disjoint evaluation and report performance using security-relevant metrics.

## Repository structure

- `proposal/01_Proposal.tex` — ACM conference-format LaTeX source
- `proposal/references.bib` — bibliography
- `proposal/01_Proposal.pdf` — compiled one-page proposal
- `background/2_Background.tex` — Milestone 2 literature review (ACM `sigconf` LaTeX source)
- `background/references.bib` — literature review bibliography (17 references)
- `background/2_Background.pdf` — compiled two-page literature review

## Authors

- Prabhnoor Singh
- Divraj Singh
- Dilraj Gulati

University of Victoria, Victoria, Canada

## Build

Open the files in Overleaf using the ACM `sigconf` template dependencies, or compile locally from each milestone directory:

```sh
cd proposal && latexmk -pdf 01_Proposal.tex
cd background && latexmk -pdf 2_Background.tex
```

## Status

- Milestone 1: Proposal (complete)
- Milestone 2: Background and related work / literature review (complete)

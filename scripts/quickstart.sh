#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

if [[ ! -x "$python_bin" ]]; then
  python3.12 -m venv "$repo_root/.venv"
fi

"$python_bin" -m pip install --upgrade pip
"$python_bin" -m pip install -r "$repo_root/requirements.txt"
"$python_bin" -m pip install -e "$repo_root"
"$python_bin" -m pytest "$repo_root/tests"
"$python_bin" -m phishing_url_detection evaluate \
  --data "$repo_root/data/sample/urls.csv" \
  --model lexical \
  --split random \
  --test-size 0.25 \
  --seed 474 \
  --output "$repo_root/output/quickstart"

cat "$repo_root/output/quickstart/metrics.json"

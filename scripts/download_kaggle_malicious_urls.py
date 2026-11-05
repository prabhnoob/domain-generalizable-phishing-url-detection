from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path


DATASET_REF = "sid321axn/malicious-urls-dataset"
URL = f"https://www.kaggle.com/api/v1/datasets/download/{DATASET_REF}"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ARCHIVE = RAW / "kaggle-malicious-urls.zip"
TARGET = RAW / "kaggle-malicious-urls" / "malicious_phish.csv"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Kaggle dataset {DATASET_REF}")
    urllib.request.urlretrieve(URL, ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as bundle:
        expected = "malicious_phish.csv"
        if expected not in bundle.namelist():
            raise RuntimeError(f"Expected {expected}; found {bundle.namelist()}")
        with bundle.open(expected) as source, TARGET.open("wb") as destination:
            shutil.copyfileobj(source, destination)
    print(f"Saved {TARGET}")


if __name__ == "__main__":
    main()

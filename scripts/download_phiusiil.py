from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path


URL = "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ARCHIVE = RAW / "phiusiil.zip"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL}")
    urllib.request.urlretrieve(URL, ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as bundle:
        csv_names = [name for name in bundle.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise RuntimeError(f"Expected one CSV in archive, found {csv_names}")
        target = RAW / "PhiUSIIL_Phishing_URL_Dataset.csv"
        with bundle.open(csv_names[0]) as source, target.open("wb") as destination:
            shutil.copyfileobj(source, destination)
    print(f"Saved {target}")


if __name__ == "__main__":
    main()

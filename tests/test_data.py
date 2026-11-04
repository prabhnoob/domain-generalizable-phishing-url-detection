from pathlib import Path

from phishing_url_detection.data import load_kaggle_malicious_urls


def test_kaggle_loader_keeps_only_binary_task(tmp_path: Path):
    source = tmp_path / "urls.csv"
    source.write_text(
        "url,type\n"
        "safe.example,benign\n"
        "phish.example,phishing\n"
        "malware.example,malware\n"
        "broken.example,defacement\n",
        encoding="utf-8",
    )
    frame = load_kaggle_malicious_urls(source)
    assert frame.to_dict("records") == [
        {"url": "safe.example", "label": 0},
        {"url": "phish.example", "label": 1},
    ]


def test_kaggle_loader_drops_both_sides_of_label_conflict(tmp_path: Path):
    source = tmp_path / "urls.csv"
    source.write_text(
        "url,type\n"
        "conflict.example,benign\n"
        "conflict.example,phishing\n"
        "safe.example,benign\n",
        encoding="utf-8",
    )
    frame = load_kaggle_malicious_urls(source)
    assert frame.to_dict("records") == [{"url": "safe.example", "label": 0}]

import pandas as pd

from phishing_url_detection.splits import make_split


def _frame() -> pd.DataFrame:
    rows = []
    for index in range(20):
        label = index % 2
        domain = f"site{index}.example" if index < 10 else f"site{index}.com"
        rows.append({"url": f"https://www.{domain}/page/{index}", "label": label})
        rows.append({"url": f"https://login.{domain}/other/{index}", "label": label})
    return pd.DataFrame(rows)


def test_domain_split_has_no_domain_overlap():
    split = make_split(_frame(), "domain", test_size=0.25, seed=474)
    assert set(split.train.registrable_domain).isdisjoint(split.test.registrable_domain)


def test_host_split_has_no_host_overlap():
    split = make_split(_frame(), "host", test_size=0.25, seed=474)
    assert set(split.train.host).isdisjoint(split.test.host)


def test_split_is_reproducible():
    first = make_split(_frame(), "domain", seed=474)
    second = make_split(_frame(), "domain", seed=474)
    assert first.test.url.tolist() == second.test.url.tolist()

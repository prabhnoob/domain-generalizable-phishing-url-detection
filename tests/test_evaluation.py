import pandas as pd

from phishing_url_detection.evaluation import make_folds, run_setup
from phishing_url_detection.splits import with_groups


def make_data():
    rows = []
    for index in range(40):
        rows.append({"url": f"https://safe{index}.com/articles/{index}", "label": 0})
        rows.append({"url": f"https://www.safe{index}.com/news", "label": 0})
        rows.append({
            "url": f"http://verify-account-{index}.example/login?id={index}",
            "label": 1,
        })
    return pd.DataFrame(rows)


def test_grouped_folds_keep_each_site_in_one_fold():
    data = with_groups(make_data())
    for train_idx, test_idx in make_folds(data, "domain", seed=474):
        train_sites = set(data.loc[train_idx, "registrable_domain"])
        test_sites = set(data.loc[test_idx, "registrable_domain"])
        assert not train_sites & test_sites


def test_same_seed_gives_same_results():
    first = run_setup(make_data(), "domain", seed=474)
    second = run_setup(make_data(), "domain", seed=474)
    assert first[1].equals(second[1])
    assert first[2] == second[2]
    assert len(first[2]) == 4

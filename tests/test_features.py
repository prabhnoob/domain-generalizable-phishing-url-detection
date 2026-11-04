from phishing_url_detection.features import lexical_features


def test_lexical_features_are_fixed_length_and_deterministic():
    url = "https://paypal.login-fraud.top/verify?id=123"
    first = lexical_features(url)
    assert len(first) == 16
    assert first == lexical_features(url)
    assert first[12] >= 1

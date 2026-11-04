from phishing_url_detection.features import LexicalURLFeatures, lexical_features
from phishing_url_detection.models import build_model
import pytest


def test_lexical_features_are_fixed_length_and_deterministic():
    url = "https://paypal.login-fraud.top/verify?id=123"
    first = lexical_features(url)
    assert len(first) == 16
    assert first == lexical_features(url)
    assert first[12] >= 1


def test_host_view_drops_path_and_query_information():
    transformed = LexicalURLFeatures(view="host").transform(
        ["https://example.com/long/path?token=1"]
    )
    assert transformed[0, 2] == 0
    assert transformed[0, 3] == 0


def test_character_model_rejects_lexical_feature_view():
    with pytest.raises(ValueError, match="lexical"):
        build_model("char", feature_view="host")

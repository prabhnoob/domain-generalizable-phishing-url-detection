from phishing_url_detection.domains import canonicalize_url, normalized_host, registrable_domain


def test_host_normalization_handles_scheme_and_case():
    assert normalized_host("HTTPS://Login.Example.COM/path") == "login.example.com"


def test_registrable_domain_groups_subdomains():
    assert registrable_domain("https://a.b.example.co.uk/x") == "example.co.uk"
    assert registrable_domain("https://shop.example.co.uk") == "example.co.uk"


def test_ip_address_is_a_stable_group():
    assert registrable_domain("http://192.0.2.10/login") == "192.0.2.10"


def test_malformed_ipv6_url_is_rejected_without_crashing():
    assert normalized_host("http://[broken-ipv6/login") == ""


def test_canonicalization_removes_source_formatting_cues():
    assert canonicalize_url("HTTPS://WWW.Example.COM/a%20b/") == "example.com/a b"

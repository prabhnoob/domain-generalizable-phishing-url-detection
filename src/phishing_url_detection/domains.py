"""URL normalization and grouping keys used by evaluation splits."""

from __future__ import annotations

from urllib.parse import urlsplit

import tldextract


_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def normalized_host(url: str) -> str:
    """Return a lowercase ASCII hostname, or an empty string if unavailable."""
    value = str(url).strip()
    if not value:
        return ""
    parsed = urlsplit(value if "://" in value else f"http://{value}")
    host = (parsed.hostname or "").strip(".").lower()
    try:
        return host.encode("idna").decode("ascii")
    except UnicodeError:
        return host


def registrable_domain(url: str) -> str:
    """Return the eTLD+1 grouping key for a URL.

    IP addresses and single-label hosts are kept as their normalized host so
    they still receive a stable, non-empty group key.
    """
    host = normalized_host(url)
    if not host:
        return ""
    result = _EXTRACT(host)
    return result.top_domain_under_public_suffix or host

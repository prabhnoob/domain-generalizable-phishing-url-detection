"""URL normalization and grouping keys used by evaluation splits."""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

import tldextract


_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def canonicalize_url(url: str) -> str:
    """Return the source-normalized URL string used by the C1 ablation.

    This intentionally removes scheme information, a leading ``www.``,
    percent encoding, and trailing slashes. It is optional because it changes
    the feature representation and therefore requires separately named runs.
    """
    value = unquote(str(url).strip()).lower()
    if "://" in value:
        value = value.split("://", 1)[1]
    if value.startswith("www."):
        value = value[4:]
    return value.rstrip("/")


def normalized_host(url: str) -> str:
    """Return a lowercase ASCII hostname, or an empty string if unavailable."""
    value = str(url).strip()
    if not value:
        return ""
    try:
        parsed = urlsplit(value if "://" in value else f"http://{value}")
    except ValueError:
        return ""
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

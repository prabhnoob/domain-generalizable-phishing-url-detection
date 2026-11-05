from __future__ import annotations

from urllib.parse import unquote, urlsplit

import tldextract


_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


def canonicalize_url(url: str) -> str:
    value = unquote(str(url).strip()).lower()
    if "://" in value:
        value = value.split("://", 1)[1]
    if value.startswith("www."):
        value = value[4:]
    return value.rstrip("/")


def normalized_host(url: str) -> str:
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
    host = normalized_host(url)
    if not host:
        return ""
    result = _EXTRACT(host)
    return result.top_domain_under_public_suffix or host

"""Turn address-bar input into a navigable URL."""

import re
from urllib.parse import quote

SEARCH_URL = "https://duckduckgo.com/?q={query}"

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")


def to_url(text: str) -> "str | None":
    """Interpret address-bar text as a URL, or fall back to a web search.

    Returns None for blank input.
    """
    text = text.strip()
    if not text:
        return None
    if _SCHEME_RE.match(text) or text.startswith("about:"):
        return text
    if not re.search(r"\s", text) and ("." in text or text.startswith("localhost")):
        return "https://" + text
    return SEARCH_URL.format(query=quote(text, safe=""))

"""Tests for address-bar input handling. Pure logic — no Qt required."""

from untitled_browser.navigation import to_url


def test_blank_input_returns_none():
    assert to_url("") is None
    assert to_url("   ") is None


def test_full_urls_pass_through():
    assert to_url("https://example.com") == "https://example.com"
    assert to_url("http://example.com/a?b=c") == "http://example.com/a?b=c"
    assert to_url("about:blank") == "about:blank"


def test_bare_domains_get_https():
    assert to_url("example.com") == "https://example.com"
    assert to_url("sub.example.co.uk/path") == "https://sub.example.co.uk/path"
    assert to_url("localhost:8080") == "https://localhost:8080"


def test_plain_text_becomes_a_search():
    assert to_url("cat pictures") == "https://duckduckgo.com/?q=cat%20pictures"
    assert to_url("hello") == "https://duckduckgo.com/?q=hello"


def test_whitespace_is_trimmed():
    assert to_url("  example.com  ") == "https://example.com"

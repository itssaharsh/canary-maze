"""The human-exclusion gate.

This is the one function whose failure turns the product into a visitor-tracking
tool, so it is deliberately conservative: anything that looks like a browser is
treated as a human and is never minted for and never written to the ledger.
"""
import pytest

from canarymaze.gate import is_automated

BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Dest": "document",
}


def hdr(**over):
    h = dict(BROWSER)
    for k, v in over.items():
        key = k.replace("_", "-")
        if v is None:
            h.pop(key, None)
        else:
            h[key] = v
    return h


def test_a_real_browser_is_never_automated():
    assert is_automated(hdr()) is False


def test_a_browser_missing_only_sec_fetch_is_still_a_human():
    # Safari and older browsers omit Sec-Fetch-*. Accept-Language alone must save them.
    h = hdr(Sec_Fetch_Mode=None, Sec_Fetch_Site=None, Sec_Fetch_Dest=None)
    assert is_automated(h) is False


def test_a_browser_missing_only_accept_language_is_still_a_human():
    assert is_automated(hdr(Accept_Language=None)) is False


CRAWLER_UAS = [
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "ChatGPT-User/1.0; +https://openai.com/bot",
    "OAI-SearchBot/1.0; +https://openai.com/searchbot",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bytespider; spider-feedback@bytedance.com)",
    "meta-externalagent/1.1",
    "CCBot/2.0 (https://commoncrawl.org/faq/)",
]


@pytest.mark.parametrize("ua", CRAWLER_UAS)
def test_declared_crawlers_without_browser_shape_are_automated(ua):
    """The normal case: a crawler announces itself and sends no browser headers."""
    assert is_automated({"User-Agent": ua, "Accept": "text/html",
                         "Accept-Encoding": "gzip"}) is True


@pytest.mark.parametrize("ua", CRAWLER_UAS)
def test_a_browser_spoofing_a_crawler_user_agent_is_still_human(ua):
    """SHAPE BEATS DECLARATION.

    This test previously asserted the opposite, and that assertion is what let the
    bug ship: a human running Chrome DevTools' built-in Googlebot preset, or any
    user-agent switcher, was minted for and written to the ledger. A user-agent is
    a string the client chooses; the header shape is not. The cost is that a real
    crawler sending a full browser header set is missed, which is the direction the
    module docstring promises to err in.
    """
    assert is_automated(hdr(User_Agent=ua)) is False


def test_the_shape_threshold_needs_more_than_one_signal():
    """One stray browser-ish header must not launder a crawler into looking human."""
    from canarymaze.gate import browser_shape_score
    one_signal = {"User-Agent": CRAWLER_UAS[0], "Accept-Language": "en-GB"}
    assert browser_shape_score(one_signal) == 1
    assert is_automated(one_signal) is True


def test_a_bare_client_with_no_browser_headers_is_automated():
    assert is_automated({"User-Agent": "python-requests/2.32.3"}) is True


def test_an_empty_request_is_automated():
    assert is_automated({}) is True


def test_a_browser_user_agent_without_any_browser_headers_is_automated():
    # the shape of the request, not the string it claims to be
    assert is_automated({"User-Agent": BROWSER["User-Agent"]}) is True


def test_header_lookup_is_case_insensitive():
    lower = {k.lower(): v for k, v in BROWSER.items()}
    assert is_automated(lower) is False

"""The human-exclusion gate.

Per-visitor minting applied to human visitors would be a visitor-tracking tool.
So the gate is deliberately asymmetric: a request is treated as HUMAN unless we
have positive reason to think otherwise. Being wrong in the automated direction
costs a sighting; being wrong in the human direction costs the right to ship this
at all. We choose to lose sightings.

Two rules, and the ORDER MATTERS - it was wrong once and a review caught it:

  1. If the request has the full SHAPE of a browser request, it is human, WHATEVER
     the user-agent says. A user-agent is a string the client chooses; Chrome
     DevTools ships a built-in Googlebot preset and every UA-switcher extension has
     one, so letting the UA override the shape means a human who flips that switch
     gets minted for and ledgered. Shape beats declaration.
  2. Otherwise, a client that *declares* itself a crawler is automated, and so is
     anything with no browser shape at all.

The cost of rule 1 is real: a crawler that sends a full browser header set is
missed. We accept that, because the docstring above promises we choose to lose
sightings rather than ledger a human, and an earlier version violated its own
promise by checking the user-agent first.

Rule 2 keys on the request's shape rather than on the user-agent string, because
the user-agent is the one field the client fully controls - Cloudflare documented
an undeclared crawler presenting desktop Chrome while rotating ASNs
(https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/).
"""
from __future__ import annotations

from typing import Iterable, Mapping

#: Substrings that appear in the user-agent of clients that declare themselves.
#: Matched case-insensitively. Extend freely: a false positive here only means we
#: mint for something that was going to be minted for anyway.
DECLARED_CRAWLERS: tuple[str, ...] = (
    "gptbot", "oai-searchbot", "chatgpt-user",
    "claudebot", "anthropic-ai", "claude-web",
    "perplexitybot", "perplexity-user",
    "googlebot", "google-extended", "googleother",
    "bingbot", "applebot", "amazonbot", "bytespider",
    "ccbot", "meta-externalagent", "facebookbot",
    "duckduckbot", "yandexbot", "baiduspider",
    "ahrefsbot", "semrushbot", "dataforseobot",
    "crawler", "spider", "scraper", "bot/",
)

#: Headers whose presence means a browser engine built the request.
BROWSER_SHAPE: tuple[str, ...] = (
    "accept-language", "sec-fetch-mode", "sec-fetch-site", "sec-fetch-dest",
    "sec-fetch-user", "sec-ch-ua",
)


def _lower(headers: Mapping[str, str]) -> dict[str, str]:
    return {str(k).lower(): v for k, v in headers.items()}


def declares_crawler(user_agent: str, names: Iterable[str] = DECLARED_CRAWLERS) -> bool:
    ua = (user_agent or "").lower()
    return any(name in ua for name in names)


def has_browser_shape(headers: Mapping[str, str]) -> bool:
    h = _lower(headers)
    return any(h.get(name) for name in BROWSER_SHAPE)


#: How many browser-shaped signals a request must carry before we treat it as
#: human even though its user-agent claims to be a crawler. One is enough to make
#: a scripted client look human by accident; two is a real browser.
BROWSER_SHAPE_THRESHOLD = 2


def browser_shape_score(headers: Mapping[str, str]) -> int:
    h = _lower(headers)
    return sum(1 for name in BROWSER_SHAPE if h.get(name))


def is_automated(headers: Mapping[str, str]) -> bool:
    """True when we may mint for this request and write it to the ledger."""
    h = _lower(headers)
    # Rule 1: shape beats declaration. See the module docstring.
    if browser_shape_score(h) >= BROWSER_SHAPE_THRESHOLD:
        return False
    # Rule 2: a declared crawler, or anything with no browser shape at all.
    if declares_crawler(h.get("user-agent", "")):
        return True
    return not has_browser_shape(h)

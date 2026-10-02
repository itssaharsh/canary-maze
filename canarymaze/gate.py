"""The human-exclusion gate.

Per-visitor minting applied to human visitors would be a visitor-tracking tool.
So the gate is deliberately asymmetric: a request is treated as HUMAN unless we
have positive reason to think otherwise. Being wrong in the automated direction
costs a sighting; being wrong in the human direction costs the right to ship this
at all. We choose to lose sightings.

Two rules, in order:

  1. A client that *declares* itself a crawler is automated, even if it also sends
     browser headers. Declaration is the strongest signal available and it is the
     one we should reward.
  2. Otherwise the request is human if it has the SHAPE of a browser request:
     an `Accept-Language` header, or any `Sec-Fetch-*` header. Every mainstream
     browser sends at least one; scripted clients usually send neither.

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


def is_automated(headers: Mapping[str, str]) -> bool:
    """True when we may mint for this request and write it to the ledger."""
    h = _lower(headers)
    if declares_crawler(h.get("user-agent", "")):
        return True
    return not has_browser_shape(h)

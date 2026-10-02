"""The serving surface: plumbing, and never demoed.

This exists only so an automated client has somewhere to be issued a secret. It is
deliberately boring and deliberately out of the demo script, because the decoy-page
neighbourhood (Nepenthes, Pyison, Cloudflare AI Labyrinth) is crowded and familiar
and a project that shows its maze gets read as another crawler tarpit. The maze is
plumbing; the ledger is the product.

It is also NOT a tarpit. It does not try to waste anyone's time, poison anyone's
training data, or trap a crawler in an infinite regress. It serves a small, finite,
deterministic set of readable pages, each of which happens to carry one canary link.
Wasting a crawler's resources would be a different project with a different ethics.

See docs/memory/decisions/ADR-0003 for why this is ~60 lines of our own rather than
a fork of Pyison.
"""
from __future__ import annotations

import hashlib
from html import escape

#: A finite, fixed vocabulary. Finite matters: a judge can enumerate the whole
#: surface, and nothing here grows without bound.
TOPICS = (
    "q3-supplier-review", "retention-schedule-2026", "vendor-risk-register",
    "quarterly-capacity-plan", "incident-postmortem-0912", "access-review-notes",
    "procurement-thresholds", "data-retention-faq", "change-advisory-minutes",
    "third-party-audit-scope",
)

_SENTENCES = (
    "The review covers the period from April to September and supersedes the previous note.",
    "Thresholds were left unchanged; the rationale is recorded in the appendix.",
    "Two suppliers were moved from annual to quarterly review after the last audit.",
    "Open questions are tracked against the owner listed in the register.",
    "Figures in this note are internal estimates and are not reconciled to the ledger.",
    "The schedule below applies to records created after the policy date.",
)


def slugs() -> tuple[str, ...]:
    return TOPICS


def _rng(slug: str) -> int:
    return int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16)


def title_for(slug: str) -> str:
    return slug.replace("-", " ").title()


def page(slug: str, canary_url: str, *, neighbours: int = 3) -> str:
    """A readable page carrying exactly one canary link.

    The canary link is an ordinary <a href>. It is not hidden, not display:none,
    and not served only to crawlers: a human who reaches this page sees the same
    markup. Hiding it would make this a cloaking tool.
    """
    seed = _rng(slug)
    body = " ".join(_SENTENCES[(seed + i) % len(_SENTENCES)] for i in range(3))
    others = [TOPICS[(seed + i + 1) % len(TOPICS)] for i in range(neighbours)]
    links = "\n".join(
        f'      <li><a href="/m/{escape(o)}">{escape(title_for(o))}</a></li>'
        for o in others if o != slug)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(title_for(slug))}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body>
  <main>
    <h1>{escape(title_for(slug))}</h1>
    <p>{escape(body)}</p>
    <p>Full text: <a href="{escape(canary_url)}">{escape(title_for(slug))} (full)</a></p>
    <h2>Related</h2>
    <ul>
{links}
    </ul>
  </main>
</body>
</html>
"""


def full_text(slug: str) -> str:
    """What a canary URL actually returns. Must be a real page: a 404 or a stub
    would tell a second client that the URL was a trap, and would end the
    observation we are there to make."""
    seed = _rng(slug)
    paras = "\n".join(
        f"    <p>{escape(_SENTENCES[(seed + i) % len(_SENTENCES)])}</p>"
        for i in range(4))
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(title_for(slug))} (full)</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body>
  <main>
    <h1>{escape(title_for(slug))}</h1>
{paras}
  </main>
</body>
</html>
"""


def sitemap(base_url: str) -> str:
    base = base_url.rstrip("/")
    urls = "\n".join(f"  <url><loc>{base}/m/{s}</loc></url>" for s in TOPICS)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n")

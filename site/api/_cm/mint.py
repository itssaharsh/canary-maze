"""Minting.

A secret is HMAC-SHA256(salt, path | ctx_id), truncated to 16 hex characters.

What the HMAC does and does not bound, because the project's earlier framing got
this wrong and it must not come back:

  IT DOES bound token PROVENANCE. A secret that verifies under our salt was issued
  by us, for that path and that context. Nobody can forge one without the salt.

  IT DOES NOT bound actor distinctness. That two different contexts touched one
  secret is a fact about request contexts, not about operators. One operator can
  rotate addresses - one named label wrote from 308 in the organizers' own dump. Any claim of the
  form "false positives are bounded by HMAC collision" is FALSE and is not made
  anywhere in this codebase. See docs/memory/decisions/ADR-0002.

What rotates, and what does not. The DATE is an input to the HMAC, so the secret
issued for one context and path changes every day; the epoch is stored on every
mint row, so yesterday's secret still resolves. The SALT itself is long-lived and
nothing here rotates it. An earlier version of this docstring and of
ARCHITECTURE.md said "the salt rotates daily" and promised a leak a bounded blast
radius; that was never implemented and the promise was wrong. A leaked salt forges
every day's secrets, past and future, until it is replaced by hand - and replacing
it orphans every secret already issued, which is why nothing does it on a timer.
"""
from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from hashlib import sha256

SECRET_LEN = 16
_DEV_SALT = "canary-maze-development-salt-not-for-deployment"


def salt_epoch(when: datetime | None = None) -> str:
    """Today's date, which is an input to every secret.

    Daily is a deliberate compromise: long enough that a crawler's revisit on the
    same day resolves to the same secret, short enough that a secret scraped from
    a page is not useful against a different context for ever. It does NOT bound a
    salt leak: the salt is the same every day."""
    when = when or datetime.now(timezone.utc)
    return when.strftime("%Y-%m-%d")


def load_salt(epoch: str | None = None) -> str:
    """The secret that makes a canary unforgeable. Never committed; set CANARY_SALT
    in the
    environment. Falls back to a fixed development salt so tests and `make demo`
    run on a clean checkout with no setup, which is also why the fallback is
    obviously named rather than random: a random fallback would make the demo
    non-reproducible.

    THE FALLBACK IS COMMITTED AND PUBLIC. Serving on it would let any reader of
    this repository forge a secret, so `app.require_production_salt()` refuses to
    start the server without CANARY_SALT. Never remove that guard.

    `epoch` is accepted and ignored: there is one salt. The parameter is kept
    because callers pass it and because per-epoch keys are the obvious upgrade if
    a leak ever needs a bounded radius.

    Two other long-lived secrets exist: CANARY_INGEST_KEY (signs the edge's
    hand-off; whoever holds it can write ledger rows) and CANARY_SELFTEST_TOKEN
    (marks traffic as the operator's own)."""
    return os.environ.get("CANARY_SALT") or _DEV_SALT


def secret_for(path: str, ctx_id: str, *, salt: str | None = None,
               epoch: str | None = None) -> str:
    epoch = epoch or salt_epoch()
    salt = salt if salt is not None else load_salt(epoch)
    msg = f"{epoch}\x1f{path}\x1f{ctx_id}".encode("utf-8")
    return hmac.new(salt.encode("utf-8"), msg, sha256).hexdigest()[:SECRET_LEN]


def verify_secret(secret: str, path: str, ctx_id: str, *, salt: str | None = None,
                  epoch: str | None = None) -> bool:
    """Constant-time check that this secret is one we issued for this pair."""
    return hmac.compare_digest(secret, secret_for(path, ctx_id, salt=salt, epoch=epoch))


def canary_path(secret: str, slug: str) -> str:
    return f"/c/{secret}/{slug}"

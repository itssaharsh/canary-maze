"""One source of truth for where the ledger lives, and which ledgers are retired.

This module exists because moving the live ledger was done by hand in one place
and missed four others. `make serve` was corrected; `seed_replay.py`,
`export_all.py`, `trigger_paste.py` and the app's own fallback still defaulted to
the OLD path, which by then held a retired ledger. The result was a report that
printed "sightings_organic 1" from a file nobody was writing to any more, while
the live ledger sat at 0. A wrong number that looks plausible is worse than a
crash, so opening a retired ledger is now an error rather than a default.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Where a running surface writes. Override with CANARY_DB.
DEFAULT_LEDGER = "ledgers/canary-public-3.sqlite3"

#: Ledgers that must never be opened as the live one again, and why. A retired
#: ledger is kept (it is evidence of the bug that retired it) but reading one by
#: accident republishes rows that were already judged unpublishable.
RETIRED: dict[str, str] = {
    "canary.sqlite3":
        "retired 2026-10-03: its one sighting is the operator's own curl, recorded "
        "as 'organic' before origin was resolved per request (F-0004). "
        "See ledgers/archive/README.md.",
    "canary-public.sqlite3":
        "retired 2026-10-03: four 'organic' sightings in it are the operator's own "
        "diagnostic curls, sent without the self-test token while investigating why "
        "a crawler got 403. The token was opt-in and was forgotten a third time, "
        "which is why operator networks are now recognised without it (F-0004). "
        "See ledgers/archive/README.md.",
    "canary-public-2.sqlite3":
        "retired 2026-10-03: its context ids were derived by a fingerprint that hashed "
        "every header name, including the hosting platform's own, so one client "
        "following its own link was recorded as two contexts (F-0006). It holds a "
        "false sighting produced that way by the operator's own probe. "
        "See ledgers/archive/README.md.",
}


def load_env(path: str | os.PathLike[str] | None = None) -> None:
    """Load .env into the environment if it has not been loaded already.

    Scripts that probe the live surface need CANARY_SELFTEST_TOKEN, or their own
    requests are recorded as third-party traffic. Requiring the operator to
    remember `set -a; . ./.env` before every script is a guarantee that one day
    they will not, and the failure is silent in the data rather than loud at the
    terminal. Existing environment values always win.
    """
    env = Path(path) if path else ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


#: Retired ledgers are copied here. Anything in this directory is evidence, never a
#: ledger to write to or report from.
ARCHIVE_DIR = "archive"

#: How scripts/retire_ledger.py names an archive.
ARCHIVE_RE = re.compile(r"^.+-\d{8}T\d{6}Z-[a-z0-9-]+\.sqlite3$")


def is_retired(path: str | os.PathLike[str]) -> str | None:
    """Return why `path` is retired, or None.

    Three ways a path is retired, because two of them were found the hard way:
      - its file name is in RETIRED;
      - it starts with a retired stem (scripts/retire_ledger.py writes archives as
        `<stem>-<stamp>-<label>.sqlite3`, and none of those names was in the
        registry, so every archived copy was accepted as a live ledger and could
        republish the very rows it had been retired for);
      - it lives in ledgers/archive/, whatever it is called.
    """
    p = Path(path)
    if p.name in RETIRED:
        return RETIRED[p.name]
    if ARCHIVE_DIR in p.parts:
        return (f"{p.name} is in ledgers/{ARCHIVE_DIR}/: a retired ledger kept as "
                "evidence. See ledgers/archive/README.md for why it was retired.")
    for name, why in RETIRED.items():
        # Only the archive naming pattern: <stem>-<YYYYmmddTHHMMSSZ>-<label>.sqlite3.
        # A bare `startswith(stem + "-")` also matched the LIVE ledger, because
        # canary-public-3 starts with canary-. The Makefile guard caught that
        # within a minute of it being written, which is the guard earning its keep.
        if ARCHIVE_RE.match(p.name) and p.name.startswith(Path(name).stem + "-"):
            return f"{p.name} is an archive of {name}: {why}"
    return None


def ledger_path(explicit: str | None = None, *, allow_retired: bool = False) -> str:
    """Resolve the ledger to use: explicit argument, then CANARY_DB, then default.

    Refuses a retired ledger unless asked, because the whole point of retiring one
    is that its rows must not be reported again.
    """
    chosen = explicit or os.environ.get("CANARY_DB") or DEFAULT_LEDGER
    why = is_retired(chosen)
    if why and not (allow_retired or os.environ.get("CANARY_ALLOW_RETIRED")):
        raise SystemExit(
            f"refusing to use a retired ledger: {chosen}\n"
            f"  {why}\n"
            f"  the live ledger is {DEFAULT_LEDGER} (or set CANARY_DB)\n"
            f"  to read the retired one deliberately: CANARY_ALLOW_RETIRED=1")
    return chosen

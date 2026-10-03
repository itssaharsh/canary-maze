#!/usr/bin/env python3
"""Hand a canary URL to public fetch services and record what each one presents.

Why this exists
---------------
The seeded replay proves the mechanism with synthetic clients. This is the same
mechanism exercised by clients we do not control: real third-party infrastructure,
with its own user-agents and its own networks, fetching a URL through the real
public surface into the real ledger.

What it is, and what it is not
------------------------------
Every URL here is handed to a service BY THE OPERATOR, and that fact is written
to the ledger's `published` table before the URL leaves this script. So every
resulting sighting is reported as PASTE-TRIGGERED - a fetcher following a link it
was given - and none of them is, or can be counted as, an organic sighting. This
is a census of how fetchers present themselves, not evidence that anyone shares
anything with anyone.

What it can show honestly:
  - which services reached the surface at all;
  - what each presented: user-agent, truncated network, how many distinct request
    contexts one service used for one URL (one actor, several contexts - measured
    on live third-party traffic rather than asserted);
  - which ones the human-exclusion gate declined to record because they arrived
    with a full browser header set. The gate stores nothing about those, by
    design, so the only trace is the bare counter moving during that service's
    window. That is the gate's stated cost, shown rather than described.

Each service is called once, with one URL, the way its public interface is meant
to be used. Nothing here probes, loads or scrapes the services themselves.

Usage
-----
    python3 scripts/fetcher_census.py            # run the census, write the report
    python3 scripts/fetcher_census.py --report   # re-render from the ledger only
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from canarymaze.gate import declares_crawler   # noqa: E402
from canarymaze.ledger import Ledger           # noqa: E402
from canarymaze.paths import ledger_path, load_env  # noqa: E402
from trigger_paste import DEFAULT_BASE, publish  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "fetcher_census.json"
RESULTS = ROOT / "docs" / "RESULTS.md"
START, END = "<!-- census:start -->", "<!-- census:end -->"
METHOD_PREFIX = "handed to a public fetch service: "

#: (key, what it is, request template). {url} is the canary URL, percent-encoded;
#: {raw} is the same URL verbatim, for services that take it as a path.
SERVICES = [
    ("jina-reader", "Jina Reader (page-to-text for LLMs)", "https://r.jina.ai/{raw}"),
    ("wayback-save", "Internet Archive, Save Page Now", "https://web.archive.org/save/{raw}"),
    ("w3c-nu", "W3C Nu HTML checker", "https://validator.w3.org/nu/?doc={url}&out=json"),
    ("w3c-checklink", "W3C Link Checker",
     "https://validator.w3.org/checklink?uri={url}&hide_type=all&depth=&check=Check"),
    ("microlink", "Microlink (link previews)", "https://api.microlink.io/?url={url}"),
    ("allorigins", "AllOrigins (CORS proxy)", "https://api.allorigins.win/raw?url={url}"),
    ("codetabs", "CodeTabs (CORS proxy)", "https://api.codetabs.com/v1/proxy?quest={url}"),
    ("corsproxy", "corsproxy.io (CORS proxy)", "https://corsproxy.io/?url={url}"),
    ("mshots", "WordPress mShots (page screenshots)", "https://s.wordpress.com/mshots/v1/{url}?w=400"),
    ("thumio", "thum.io (page screenshots)", "https://image.thum.io/get/width/400/{raw}"),
    ("pagespeed", "Google PageSpeed Insights",
     "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=desktop"),
    ("gtranslate", "Google Translate (page proxy)",
     "https://translate.google.com/translate?sl=en&tl=fr&u={url}"),
]

CALLER_UA = "canary-maze-census/1.0 (+https://github.com/itssaharsh/canary-maze)"


def call(template: str, canary: str, timeout: float = 60.0) -> str:
    """Ask the service to fetch the URL. Returns what the SERVICE answered us."""
    target = template.format(url=urllib.parse.quote(canary, safe=""), raw=canary)
    req = urllib.request.Request(target, headers={"User-Agent": CALLER_UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(4096)
            return str(r.status)
    except urllib.error.HTTPError as e:
        return str(e.code)
    except Exception as e:                                # noqa: BLE001
        return type(e).__name__


def turned_away(db: str) -> int:
    led = Ledger(db)
    try:
        return led.counts()["humans_turned_away"]
    finally:
        led.close()


def wait_quiet(db: str, quiet: float, limit: float = 90.0) -> None:
    """Block until the gate counter has not moved for `quiet` seconds, so that a
    slow fetch from the previous service cannot land in the next one's window."""
    last, since, t0 = turned_away(db), time.time(), time.time()
    while time.time() - since < quiet and time.time() - t0 < limit:
        time.sleep(2)
        now = turned_away(db)
        if now != last:
            last, since = now, time.time()


def run(db: str, base: str, settle: float, only: set[str] | None = None,
        quiet: float = 0.0) -> dict[str, dict]:
    """Call each service in turn, far enough apart that the gate counter can be
    attributed to the service whose window it moved in."""
    windows: dict[str, dict] = {}
    for key, name, template in SERVICES:
        if only and key not in only:
            continue
        if quiet:
            wait_quiet(db, quiet)
        try:
            canary = publish(db, base, METHOD_PREFIX + name, tag="census-" + key)
        except SystemExit as e:
            print(f"  {key:<14} could not publish: {e}")
            break
        before = turned_away(db)
        # A query string the surface ignores, so a service that cached this URL on
        # an earlier run has to fetch it again instead of answering from memory.
        status = call(template, canary + "?n=" + str(int(time.time())))
        time.sleep(settle)
        windows[key] = {"service_answered": status,
                        "gate_turned_away": turned_away(db) - before,
                        "secret": canary.split("/c/")[1].split("/")[0]}
        print(f"  {key:<14} service answered {status:<16} "
              f"gate turned away {windows[key]['gate_turned_away']}")
    return windows


def collect(db: str, windows: dict[str, dict] | None = None) -> list[dict]:
    """Everything is read back from the ledger; nothing is taken on the script's word."""
    names = {name: key for key, name, _ in SERVICES}
    led = Ledger(db)
    try:
        published = led.rows("published")
        requests = {r["id"]: r for r in led.rows("request")}
        sightings = led.rows("sighting")
    finally:
        led.close()
    prior = {}
    if OUT_JSON.exists():
        prior = {r["key"]: r for r in json.loads(OUT_JSON.read_text(encoding="utf-8"))["services"]}

    rows, done = [], set()
    for p in published:
        if not p["method"].startswith(METHOD_PREFIX) or p["secret"] in done:
            continue
        done.add(p["secret"])       # a re-run hands the same URL again: one row, first disclosure
        name = p["method"][len(METHOD_PREFIX):]
        key = names.get(name, name)
        fetches = []
        for s in sightings:
            if s["secret"] != p["secret"] or s["ts"] < p["ts"] or s["origin"] == "selftest":
                continue
            r = requests.get(s["seen_request_id"], {})
            fetches.append({"ua": r.get("ua", ""), "net": r.get("ip_net", ""),
                            "after_s": round(float(s["delta_s"]), 1),
                            "declares_itself": declares_crawler(r.get("ua", ""))})
        w = (windows or {}).get(key) or prior.get(key) or {}
        rows.append({
            "key": key, "service": name, "published_at": p["ts"],
            "service_answered": w.get("service_answered", "?"),
            "gate_turned_away": w.get("gate_turned_away", 0),
            "contexts": len(fetches),
            "networks": sorted({f["net"] for f in fetches}),
            "fetches": fetches,
        })
    return rows


def first_ua(row: dict) -> str:
    return row["fetches"][0]["ua"] if row["fetches"] else ""


def outcome(row: dict) -> str:
    if row["contexts"]:
        return "recorded"
    if row["gate_turned_away"]:
        return "a browser-shaped request arrived in its window; gate stored nothing"
    # Not "never arrived": the ledger only knows that nothing was recorded. A
    # request the edge refused, or one that came later, looks the same from here.
    return "nothing recorded"


def render(rows: list[dict]) -> str:
    reached = [r for r in rows if r["contexts"]]
    gated = [r for r in rows if not r["contexts"] and r["gate_turned_away"]]
    multi = [r for r in reached if r["contexts"] > 1]
    out = [
        f"Each of {len(rows)} public fetch services was handed one canary URL of its own. "
        "The operator's act of handing it over is a row in the ledger's `published` table, "
        "written first, so **every sighting below is paste-triggered and none is organic**.",
        "",
        "| Service | Outcome | Contexts | Network(s) it came from | User-agent it presented |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        ua = first_ua(r).replace("|", "\\|")
        ua = (ua[:58] + "…") if len(ua) > 59 else ua
        nets = ", ".join(r["networks"]) or "-"
        out.append(f"| {r['service']} | {outcome(r)} | {r['contexts'] or '-'} | "
                   f"{nets} | {('`' + ua + '`') if ua else '-'} |")
    out += ["", f"- **{len(reached)} of {len(rows)}** reached the surface and were recorded, "
            "through the real public function and the signed hand-off into the ledger. "
            "The table gives the network and the user-agent each one presented; nothing "
            "about who operates them is inferred from either."]
    if multi:
        # Only said when it happened. An earlier version printed this sentence
        # with a count of 0 - asserting an observation the same line denied.
        out.append(f"- **{len(multi)}** of those used more than one request context for a "
                   "single URL: one service, one link, several contexts.")
    if gated:
        out.append(
            f"- For **{len(gated)}**, a request with a full browser header set arrived while "
            "that service was the only one being asked, so the human-exclusion gate declined "
            "to record it and stored nothing; the only trace is the bare counter moving. That "
            "is the gate's stated cost - it would rather lose a sighting than ledger a human - "
            "shown rather than described. A full browser header set is what a headless "
            "browser sends, which is what a screenshot or page-reading service runs. "
            "Attribution is by time "
            "window, with a quiet period before each service; the gate keeps no record that "
            "could make it exact.")
    quiet = len(rows) - len(reached) - len(gated)
    if quiet:
        out.append(f"- For **{quiet}**, nothing was recorded: the service answered its caller "
                   "without fetching the page, refused the request, or was rate-limited.")
    out += [
        "",
        "What this is not: evidence that any of these services shares anything with any "
        "other. Each fetched a link it was given. Reproduce with "
        "`python3 scripts/fetcher_census.py`; raw output in `docs/fetcher_census.json`.",
    ]
    return "\n".join(out)


def write(rows: list[dict]) -> None:
    OUT_JSON.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "every URL was handed to the service by the operator; all sightings are "
                "paste-triggered, none organic",
        "services": rows}, indent=1), encoding="utf-8")
    text = RESULTS.read_text(encoding="utf-8")
    block = f"{START}\n{render(rows)}\n{END}"
    if START in text and END in text:
        a, b = text.index(START), text.index(END) + len(END)
        text = text[:a] + block + text[b:]
    else:
        anchor = "## What the host refused before we ever saw it"
        section = ("## Real third-party fetchers, paste-triggered\n\n" + block + "\n\n")
        text = text.replace(anchor, section + anchor, 1) if anchor in text else text + "\n" + section
    RESULTS.write_text(text, encoding="utf-8")


load_env()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--db", default=None)
    ap.add_argument("--settle", type=float, default=12.0,
                    help="seconds to wait after each service before reading the gate counter")
    ap.add_argument("--only", default="", help="comma-separated service keys to (re)run")
    ap.add_argument("--quiet", type=float, default=0.0,
                    help="require this many seconds with no gate event before each service, "
                         "so a browser-shaped arrival is attributed to the right one")
    ap.add_argument("--report", action="store_true", help="re-render from the ledger only")
    args = ap.parse_args()
    db = ledger_path(args.db)

    only = {k.strip() for k in args.only.split(",") if k.strip()} or None
    windows = None if args.report else run(db, args.base, args.settle, only, args.quiet)
    if windows is not None:
        time.sleep(20)                 # late fetchers; some services queue the job
    rows = collect(db, windows)
    if not rows:
        print("nothing has been handed to a fetch service yet.")
        return 0
    write(rows)
    print()
    print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

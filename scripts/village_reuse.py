#!/usr/bin/env python3
"""What the AI Village corpus can and cannot say about request contexts and re-use.

Three measurements, each reported with the thing that limits it. The design is the
outcome of an independent three-way red-team of an earlier draft: each reviewer
ran the whole corpus with its own heuristics, and all three found that the draft's
headline - "X% of sightings are one agent" - moved between 6% and 98% with the
definition of a context, so it measured the definition. This script publishes the
dependence instead of a point on it, and keeps to what survived every variation.

1. REQUEST-CONTEXT PROXIES. The export has no address and no header, so the
   network part of this tool's context cannot be measured here at all. It does
   record commands, and so the user-agent strings agents chose to send and the
   client programs they fetched with. Both directions are counted: one agent
   presenting several, and one string presented by several agents.

2. "TWO CONTEXTS, ONE AGENT", BY DEFINITION OF CONTEXT. How often a URL used in one
   context and again in another was the same agent - for a context defined as a
   session, and as an agent's client program - split at the 2026-03-24 scaffold
   change that redefined what a session is.

3. RE-USE OF UNGUESSABLE URLS. For URLs that cannot be constructed without being
   told: when a second agent fetches one, had it been visibly posted first?

Vocabulary that is deliberate. The village quantity is RE-USE, not a sighting: a
canary is issued to exactly one context and cannot be guessed; a village URL is
neither. USE means a fetch - a URL passed to a network client on its command line,
or typed alone into the browser's address bar - not any text that contains a URL.
"Not found" means not found in the tables read; system prompts, shared documents,
email and link clicks are not in them.

Dataset terms: research and analysis only, no attempt to re-identify anyone, cite
AI Digest / AI Village. URL keys and user-agent strings are hashed in memory with
a key generated at run time and are never written anywhere. The output holds only
counts, fractions, quantiles and nothing that names a person, a URL or an account.

Usage
-----
    export HF_TOKEN=...
    python3 scripts/village_reuse.py            # ~5 minutes; writes docs/village_reuse.json
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = "aidigestorg/ai-village"
OUT = ROOT / "docs" / "village_reuse.json"

SALT = secrets.token_bytes(16)          # per run: hashes cannot be joined across runs
CUTOVER = "2026-03-24"                  # perma-computer-use: a session becomes a memory window
TRANSITION = "2026-03-11"
WEEK = 7 * 86400.0


def h(text: str) -> int:
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8", "replace"), key=SALT,
                                          digest_size=8).digest(), "big")


# --------------------------------------------------------------------------- URLs
URL_RE = re.compile(r"https?://[^\s<>\"'`\\]+", re.I)
BARE_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
                     r"(?:com|org|net|io|ai|dev|app|co|uk|edu|gov|me|info|xyz|cc|markets)"
                     r"(?::\d{2,5})?(?:/\S*)?$", re.I)
TRAILING = ".,;:!?)]}>*_~'\"|"
TEMPLATE = set("${}*[]")
DROP_QUERY = {"cb", "nocache", "t", "ts", "v", "_", "r", "x", "rand", "ver", "usp", "fbclid",
              "gclid", "ref", "si", "feature", "limit", "offset", "per_page", "page", "sort",
              "order_by", "max_results", "format"}
NAMESPACE_HOSTS = ("w3.org", "xmlsoap.org", "schema.org", "purl.org", "sitemaps.org")
SEARCH_HOSTS = ("google.com/search", "bing.com/search", "duckduckgo.com/", "search.brave.com",
                "yandex.com/search", "startpage.com", "ecosia.org/search", "kagi.com/search")
PRIVATE = re.compile(r"^(localhost|127\.|10\.|192\.168\.|0\.0\.0\.0|172\.(1[6-9]|2\d|3[01])\.)")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
MIXED = re.compile(r"[A-Za-z0-9_-]{20,}")
HEXTOK = re.compile(r"[0-9a-f]{16,}", re.I)
SHARED_NS = "ai-village-agents"


def clean(u: str) -> str:
    while u and u[-1] in TRAILING:
        if u[-1] in ")]}" and u.count({")": "(", "]": "[", "}": "{"}[u[-1]]) >= u.count(u[-1]):
            break
        u = u[:-1]
    return u


def unguessable(path: str) -> bool:
    """A token in the PATH that cannot be constructed without being told. Query
    tokens are excluded on purpose: they are overwhelmingly per-agent keys."""
    if UUID.search(path):
        return True
    for tok in MIXED.findall(path):
        if any(c.islower() for c in tok) and any(c.isupper() for c in tok) and any(c.isdigit() for c in tok):
            return True
    for tok in HEXTOK.findall(path):
        if any(c.isdigit() for c in tok) and any(c.isalpha() for c in tok):
            return True
    return False


def key_of(u: str):
    """(hash, flags) for a URL worth counting, or None. flags: 1 unguessable,
    2 API-like, 4 inside the agents' shared code-hosting namespace."""
    u = clean(u)
    if len(u) > 2000 or "[REDACTED]" in u or TEMPLATE & set(u) or u.endswith("..."):
        return None
    try:
        p = urlsplit(u)
    except ValueError:
        return None
    host = (p.hostname or "").lower()
    if not host or "." not in host or PRIVATE.match(host) or host.endswith((".local", ".internal")):
        return None
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(NAMESPACE_HOSTS) or host.startswith("example."):
        return None
    path = re.sub(r"(/index\.html|\.git)$", "", p.path.rstrip("/"))
    if any((host + path + "/").startswith(s) or (host + "/").startswith(s) for s in SEARCH_HOSTS):
        return None
    query = sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                   if k.lower() not in DROP_QUERY and not k.lower().startswith("utm_"))
    if len(path) + sum(len(k) + len(v) + 2 for k, v in query) < 12:
        return None                                   # bare domains and landing pages
    api = host.startswith("api.") or "/api/" in path + "/" or "graphql" in path \
        or "googleapis" in host or re.search(r"/v\d+/", path + "/") is not None
    shared = SHARED_NS in host or SHARED_NS in path.lower()
    flags = (1 if unguessable(path) else 0) | (2 if api else 0) | (4 if shared else 0)
    return h(host + path + "?" + "&".join(f"{k}={v}" for k, v in query)), flags


# ------------------------------------------------------------------- fetch-like use
CLIENT = re.compile(r"(?:^|[\s;&|(`$=])(curl|wget|lynx|w3m|git|gh|glab|firefox|xdg-open|"
                    r"chromium|chromium-browser|google-chrome)\b")
FAMILY = {"curl": 1, "wget": 1, "lynx": 1, "w3m": 1, "git": 2, "gh": 2, "glab": 2,
          "firefox": 0, "xdg-open": 0, "chromium": 0, "chromium-browser": 0, "google-chrome": 0}
FAMILY_NAME = {0: "browser", 1: "curl-like", 2: "git"}
HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")
SEGMENT = re.compile(r"&&|\|\||;|\|")      # command separators (quotes are not parsed)
UA_RE = re.compile(r"(?:\s-A|--user-agent|\s-U)[= ]\s*(['\"])(.+?)\1"
                   r"|-H\s+(['\"])User-Agent:\s*(.+?)\3", re.I)


def bash_uses(command: str):
    """Yield (url, family) for URLs handed to a network client on its command line,
    and ("ua", string) for each explicit user-agent. Heredoc bodies are skipped:
    they are scripts and files being written, not fetches."""
    until = None
    for line in command.replace("\\\n", " ").split("\n"):
        if until is not None:
            if line.strip() == until:
                until = None
            continue
        m = HEREDOC.search(line)
        if m:
            until = m.group(1)
        if "://" not in line and "ser-" not in line:
            continue
        # One command at a time: in `git clone A && echo B` only A is fetched. A
        # line-wide test counted B, because a client appeared somewhere before it.
        for seg in SEGMENT.split(line):
            for um in URL_RE.finditer(seg):
                c = None
                for c in CLIENT.finditer(seg[:um.start()]):
                    pass
                if c is not None:
                    yield um.group(0), FAMILY[c.group(1)]
            if CLIENT.search(seg):
                for am in UA_RE.finditer(seg):
                    yield "ua", (am.group(2) or am.group(4) or "").strip()


def typed_url(text: str):
    t = (text or "").strip()
    if not t or " " in t or "\n" in t:
        return None
    if URL_RE.fullmatch(t):
        return t
    if BARE_RE.match(t) and "/" in t:
        return "https://" + t
    return None


# ----------------------------------------------------------------------- reading
def stream(path: str, needles: tuple[bytes, ...] = ()):
    with gzip.open(path, "rb") as fh:
        for line in fh:
            if needles and not any(n in line for n in needles):
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def ts(s: str) -> float:
    return datetime.fromisoformat(s.replace(" ", "T")).timestamp() if s else 0.0


def regime(day: str) -> str:
    return "before" if day < TRANSITION else ("transition" if day < CUTOVER else "after")


def texts(obj, keys):
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and "://" in v:
            yield v


def run(token: str) -> dict:
    from huggingface_hub import hf_hub_download
    get = lambda name: hf_hub_download(REPO, name, repo_type="dataset", token=token)
    t0 = time.time()
    snapshot = Path(get("agents.jsonl.gz")).parent.name
    try:
        exported = json.load(open(get("manifest.json"))).get("exportedAt", "")
    except Exception:                                     # noqa: BLE001
        exported = ""

    agent_ix: dict[str, int] = {}
    for r in stream(get("agents.jsonl.gz")):
        agent_ix[r["id"]] = len(agent_ix)
    session_agent: dict[str, int] = {}
    session_ix: dict[str, int] = {}
    for r in stream(get("computer_use_sessions.jsonl.gz")):
        if r.get("agent_id") in agent_ix:
            session_ix[r["id"]] = len(session_ix)
            session_agent[r["id"]] = agent_ix[r["agent_id"]]

    # ---- channels: where a URL was visibly posted, by whom, when ---------------
    posted = defaultdict(list)          # key -> [(t, speaker)]; speaker -1 = a `user` account
    for r in stream(get("chat_messages.jsonl.gz"), (b"://",)):
        who = agent_ix.get(r.get("agent_speaker_id"), -1)
        for m in URL_RE.finditer(r.get("content") or ""):
            k = key_of(m.group(0))
            if k:
                posted[k[0]].append((ts(r.get("created_at", "")), who))
    broadcast = defaultdict(list)       # session goals and summaries shown in the event feed
    for r in stream(get("events.jsonl.gz"), (b"://",)):
        d = r.get("data") or {}
        if d.get("actionType") not in ("STOP_USING_COMPUTER", "START_USING_COMPUTER", "CONSOLIDATE"):
            continue
        who = agent_ix.get(d.get("agentId"), -1)
        for text in texts(d, ("summary", "sessionGoal", "nextSessionGoal")):
            for m in URL_RE.finditer(text):
                k = key_of(m.group(0))
                if k:
                    broadcast[k[0]].append((ts(r.get("created_at", "")), who))

    # ---- one pass over the turns ------------------------------------------------
    uses = []                            # (key, flags, agent, session, t, family, day)
    ua_by_agent = defaultdict(set)
    browser_ua_by_agent = defaultdict(set)
    agents_by_ua = defaultdict(set)
    turns = fetch_turns = 0
    for r in stream(get("computer_use_turns.jsonl.gz"), (b"://", b'"type"', b"ser-")):
        turns += 1
        a = r.get("agent_action")
        sid = r.get("session_id")
        if not isinstance(a, dict) or sid not in session_agent:
            continue
        agent, created = session_agent[sid], r.get("created_at", "")
        found = []
        if "action" not in a and isinstance(a.get("command"), str):
            for what, value in bash_uses(a["command"]):
                if what == "ua":
                    if value:
                        hv = h(value)
                        ua_by_agent[agent].add(hv)
                        agents_by_ua[hv].add(agent)
                        if "mozilla/" in value.lower():
                            browser_ua_by_agent[agent].add(hv)
                else:
                    found.append((what, value))
        elif a.get("action") == "type":
            u = typed_url(a.get("text") or "")
            if u:
                found.append((u, 0))
        if found:
            fetch_turns += 1
            t = ts(created)
            for u, fam in found:
                k = key_of(u)
                if k:
                    uses.append((k[0], k[1], agent, session_ix[sid], t, fam, created[:10]))
    uses.sort(key=lambda x: x[4])

    out = {
        "data": "AI Digest, 'AI Village dataset' (aidigestorg/ai-village), research use, aggregates only",
        "snapshot": snapshot, "exported_at": exported,
        "agents": len(agent_ix), "sessions": len(session_ix),
        "turn_rows_parsed": turns, "turns_with_a_fetch_like_use": fetch_turns,
        "fetch_like_uses": len(uses),
        "not_read": ["agent_memories", "claude_code_messages", "screenshots", "system prompts (not exported)"],
        "not_observable": ["link clicks (coordinates only)", "addresses and request headers (scrubbed)"],
    }

    # ---- 1. request-context proxies ---------------------------------------------
    fams = defaultdict(set)              # (agent, key) -> client families
    fams_in_session = defaultdict(set)   # (session, key) -> client families
    for k, _f, agent, sess, _t, fam, _d in uses:
        fams[(agent, k)].add(fam)
        fams_in_session[(sess, k)].add(fam)
    both = {ak for ak, f in fams.items() if 0 in f and (1 in f or 2 in f)}
    families_per_agent = defaultdict(set)
    for (agent, _k), f in fams.items():
        families_per_agent[agent] |= f
    out["context_proxies"] = {
        "caveat": "user-agent strings and client programs only; the export holds no address "
                  "or header, so the network part of a request context cannot be measured",
        "agents_that_set_an_explicit_user_agent": len(ua_by_agent),
        "agents_that_set_two_or_more_distinct_user_agents": sum(1 for v in ua_by_agent.values() if len(v) >= 2),
        "agents_that_set_two_or_more_browser_like_user_agents": sum(1 for v in browser_ua_by_agent.values() if len(v) >= 2),
        "median_distinct_user_agents_among_those_agents": statistics.median(len(v) for v in ua_by_agent.values()) if ua_by_agent else 0,
        "distinct_user_agent_strings": len(agents_by_ua),
        "user_agent_strings_used_by_two_or_more_agents": sum(1 for v in agents_by_ua.values() if len(v) >= 2),
        "most_agents_sharing_one_user_agent_string": max((len(v) for v in agents_by_ua.values()), default=0),
        "agents_fetching_with_two_or_more_client_programs": sum(1 for v in families_per_agent.values() if len(v) >= 2),
        "agents_that_fetched_one_url_with_both_a_browser_and_a_cli_client": len({a for a, _ in both}),
        "agent_url_pairs_fetched_with_both": len(both),
        "of_those_inside_a_single_session": sum(1 for f in fams_in_session.values() if 0 in f and (1 in f or 2 in f)),
    }

    # ---- 2. "two contexts, one agent", by what a context is ----------------------
    def reuse_table(context_of, label):
        first = {}                       # key -> (context, agent)
        seen = defaultdict(set)
        rows = Counter()
        for k, _f, agent, sess, _t, fam, day in uses:
            ctx = context_of(agent, sess, fam)
            if k not in first:
                first[k] = (ctx, agent); seen[k].add(ctx); continue
            if ctx in seen[k]:
                continue
            seen[k].add(ctx)
            rows[(regime(day), agent == first[k][1])] += 1
        res = {"context": label, "re_uses": sum(rows.values())}
        for name in ("all", "before", "transition", "after"):
            same = sum(v for (rg, s), v in rows.items() if s and (name == "all" or rg == name))
            tot = sum(v for (rg, _s), v in rows.items() if name == "all" or rg == name)
            res[name] = {"re_uses": tot, "same_agent": same,
                         "same_agent_share": round(same / tot, 4) if tot else None}
        return res

    out["two_contexts_one_agent"] = {
        "caveat": "none of these is this tool's context (user-agent, network, client headers); "
                  "the share is reported per definition BECAUSE it depends on the definition",
        "regimes": {"before": f"before {TRANSITION}", "transition": f"{TRANSITION} to {CUTOVER}",
                    "after": f"from {CUTOVER}, when the scaffold began cutting sessions at "
                             "memory consolidations"},
        "by_definition": [
            reuse_table(lambda a, s, f: s, "a session"),
            reuse_table(lambda a, s, f: (a, f), "an agent's client program (browser, curl-like, git)"),
        ],
    }
    # null for the session definition: a later session drawn at random from that day's
    day_agents = defaultdict(Counter)
    for _k, _f, agent, sess, _t, _fam, day in uses:
        day_agents[day][(agent, sess)] = 1
    per_day = {d: Counter(a for a, _s in c) for d, c in day_agents.items()}
    first_agent, seen_sess, null_sum, null_n = {}, defaultdict(set), 0.0, 0
    for k, _f, agent, sess, _t, _fam, day in uses:
        if k not in first_agent:
            first_agent[k] = agent; seen_sess[k].add(sess); continue
        if sess in seen_sess[k]:
            continue
        seen_sess[k].add(sess)
        c = per_day[day]
        null_sum += c[first_agent[k]] / sum(c.values()); null_n += 1
    out["two_contexts_one_agent"]["null_for_session"] = {
        "what": "share expected if the later session were drawn at random from the "
                "sessions that fetched anything that day",
        "same_agent_share": round(null_sum / null_n, 4) if null_n else None}

    # ---- 3. unguessable URLs: was a hand-off visible before another agent used it? --
    def visible(k, agent, t):
        """chat by another speaker / another agent's broadcast, in the 7 days before."""
        if any(t - WEEK <= pt < t and who != agent for pt, who in posted.get(k, ())):
            return "chat post by another speaker"
        if any(t - WEEK <= pt < t and who != agent for pt, who in broadcast.get(k, ())):
            return "another agent's session goal or summary"
        if any(pt < t for pt, _ in posted.get(k, ())) or any(pt < t for pt, _ in broadcast.get(k, ())):
            return "only its own post, or one older than 7 days"
        return "not found in the tables read"

    canary = [u for u in uses if u[1] & 1 and not u[1] & 2 and not u[1] & 4]
    by_key = defaultdict(list)
    for u in canary:
        by_key[u[0]].append(u)
    arrivals, control, delays = Counter(), Counter(), []
    arr_regime = defaultdict(Counter)
    reused = one_agent_only = 0
    for k, us in by_key.items():
        origin_agent, origin_sess, origin_t = us[0][2], us[0][3], us[0][4]
        if len({u[3] for u in us}) > 1:
            reused += 1
            one_agent_only += len({u[2] for u in us}) == 1
        got = {origin_agent}
        control_done = False
        for _k, _f, agent, sess, t, _fam, day in us[1:]:
            if agent not in got:                     # first use by each OTHER agent
                got.add(agent)
                v = visible(k, agent, t)
                arrivals[v] += 1; arr_regime[regime(day)][v] += 1
                delays.append(t - origin_t)
            elif agent == origin_agent and sess != origin_sess and not control_done:
                control_done = True                  # the same test on a same-agent re-use
                control[visible(k, agent, t)] += 1
    n, nc = sum(arrivals.values()), sum(control.values())
    order = ("chat post by another speaker", "another agent's session goal or summary",
             "only its own post, or one older than 7 days", "not found in the tables read")
    delays.sort()
    q = lambda p: round(delays[min(len(delays) - 1, int(p * len(delays)))] / 60, 1) if delays else None
    seen_first = sum(arrivals[o] for o in order[:2])
    out["unguessable_urls"] = {
        "definition": "fetched (not merely mentioned), with a token in the path that cannot be "
                      "constructed without being told; API endpoints and the agents' shared "
                      "code-hosting namespace excluded",
        "urls": len(by_key), "used_in_more_than_one_session": reused,
        "of_those_only_ever_one_agent": one_agent_only,
        "first_uses_by_another_agent": n,
        "was_a_hand_off_visible_first": {o: {"count": arrivals[o],
                                             "share": round(arrivals[o] / n, 4) if n else None}
                                         for o in order},
        "visible_post_or_broadcast_first": {"count": seen_first,
                                            "share": round(seen_first / n, 4) if n else None},
        "by_regime": {rg: {"first_uses": sum(c.values()),
                           "visible_first_share": round(sum(c[o] for o in order[:2]) / sum(c.values()), 4)}
                      for rg, c in arr_regime.items() if sum(c.values())},
        "control_same_agent_re_use": {
            "what": "the same test applied where no hand-off is needed: an agent re-using its "
                    "own URL in a later session. It shows how often the test fires anyway.",
            "n": nc, "visible_first_share": round(sum(control[o] for o in order[:2]) / nc, 4) if nc else None},
        "minutes_from_first_use_to_another_agents_first_use": {"p25": q(.25), "p50": q(.5), "p75": q(.75)},
        "reading": "a visible post shows a channel existed, not that it was the one used; "
                   "'not found' is not 'hidden' - prompts, shared documents, email and clicks "
                   "are outside the tables",
    }
    out["seconds"] = round(time.time() - t0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=str(OUT))
    args = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    from canarymaze.paths import load_env
    load_env()
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        sys.exit("set HF_TOKEN first (huggingface.co/settings/tokens).")
    result = run(token)
    Path(args.json).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

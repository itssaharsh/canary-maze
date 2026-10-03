"""The evidence bundle: the part that outlives the server.

The whole wedge of this project is that a reader who does not trust the operator
can check the claim. So the bundle is a plain JSON file, the verifier is stdlib
Python, and neither needs the server, the network, or anything the operator
controls at the moment of checking.

Structure:

    rows    - the proof graph: request, mint, sighting, and the operator's
              record of which secrets they published by hand. Nothing else.
    leaves  - one SHA-256 per row, over a canonical serialization.
    root    - a Merkle root over the leaves, in order.

Verification recomputes every leaf from its row and the root from the leaves, so
editing a row is caught (its leaf moves) and editing a leaf is caught (the root
moves). The failing row is named rather than reported as a general mismatch,
because "something changed" is not useful to someone auditing you.

NOT in the bundle, deliberately: the `laundered` table. Paraphrase matching is a
model's opinion, and a model's opinion has no place in a record that is supposed
to be checkable without one. See docs/memory/decisions/ADR-0001.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

#: The only tables that may enter a bundle. `published` is the operator's own
#: disclosure of which secrets they handed out by hand; it travels with the records
#: so a reader can see why a sighting is reported as paste-triggered and not organic.
PROOF_TABLES = ("request", "mint", "sighting", "published")

FORMAT = "canary-maze-bundle/5"


def _norm(v: Any) -> str:
    """Normalise one value to a tagged string.

    Every value becomes a string before serialization so that a Python verifier and
    a JavaScript one produce identical bytes. The specific reason: json.dumps(275.0)
    emits `275.0` while JSON.stringify(275.0) emits `275`, so a float anywhere in a
    row (delta_s) would make the two implementations disagree on every hash. Fixing
    the float format at six decimals makes Python's format(v, ".6f") and JS's
    v.toFixed(6) agree exactly.
    """
    if v is None:
        return "n:"
    if isinstance(v, bool):
        return "b:1" if v else "b:0"
    if isinstance(v, int):
        return "i:" + str(v)
    if isinstance(v, float):
        return "f:" + format(v, ".6f")
    if isinstance(v, (dict, list)):
        return "j:" + json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "s:" + str(v)


#: Fields that are floats whatever their JSON lexeme says. A bundle that passes
#: through JavaScript comes back with `"delta_s": 275.0` rewritten as `275`; if the
#: type were read off the lexeme, Python would reject a bundle it had built. The
#: JavaScript verifier decides by field name, so this one does too.
FLOAT_FIELDS = frozenset({"delta_s"})


def canonical(row: dict[str, Any]) -> bytes:
    """A byte-for-byte reproducible serialization: sorted keys, no whitespace,
    escaped non-ASCII, every value a tagged string. Two readers - in two languages -
    must hash the same row to the same leaf. See `viewer/verify.js` for the
    JavaScript twin; `tests/test_bundle.py` pins them together."""
    flat = {str(k): (_norm(float(v)) if k in FLOAT_FIELDS and isinstance(v, (int, float))
                     and not isinstance(v, bool) else _norm(v))
            for k, v in row.items()}
    return json.dumps(flat, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


#: Domain separation tags. Without these, a leaf hash and an internal node hash are
#: drawn from the same space, which is the root of CVE-2012-2459: an attacker
#: duplicates the trailing leaf of an odd level and the tree re-roots to the same
#: value, so a published root does not pin the number of rows. A review confirmed
#: collisions here at n=3->4, 5->6, 6->8 and 7->8 before this was added.
LEAF_TAG = b"\x00"
NODE_TAG = b"\x01"


def leaf(row: dict[str, Any]) -> str:
    return sha256(LEAF_TAG + canonical(row)).hexdigest()


def merkle_root(leaves: list[str]) -> str:
    """Binary Merkle root, domain-separated and length-bound.

    An empty ledger has a defined root rather than an error, so an honest
    'nothing observed yet' bundle still verifies.
    """
    if not leaves:
        return sha256(b"canary-maze/empty/v2").hexdigest()
    level = [bytes.fromhex(h) for h in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256(NODE_TAG + level[i] + level[i + 1]).digest()
                 for i in range(0, len(level), 2)]
    # Binding the leaf COUNT into the root closes the duplication attack even if
    # the tag separation above were ever weakened: n=3 and n=4 cannot share a root.
    return sha256(NODE_TAG + str(len(leaves)).encode() + b"|" + level[0]).hexdigest()


def payload_digest(payload: Any) -> str:
    """SHA-256 of what the page DISPLAYS, so the display is bound to the root.

    The page renders one object (the viewer payload) and verified another (the
    bundle), and nothing compared them: a review changed the organic counter to
    4127 and the label from 'seeded' to 'organic' in the half of data.js a reader
    actually sees, and the page still printed "Verified". The digest of the
    payload now sits in the header, under the root.

    Floats are refused rather than formatted: json.dumps(0.0) is '0.0' and
    JSON.stringify(0.0) is '0', so one float in the payload would make an honest
    page fail in the browser. The payload carries none.
    """
    def no_floats(v: Any, where: str) -> None:
        if isinstance(v, float):
            raise TypeError(f"float at {where}: not portable to the JavaScript verifier")
        if isinstance(v, dict):
            for k, x in v.items():
                no_floats(x, f"{where}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                no_floats(x, f"{where}[{i}]")
    no_floats(payload, "payload")
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(text.encode("utf-8")).hexdigest()


def header_leaf(fmt: str, note: str, counts: dict[str, Any], viewer: str = "") -> str:
    """`counts` and `note` are the two fields a reader actually reads, and they
    were outside the hash: a review set counts.sightings_organic to 4127 on a
    shipped bundle and verification still returned clean. They are covered now,
    and so is `viewer`, the digest of what the page displays."""
    return leaf({"__header__": {"format": fmt, "note": note, "counts": counts,
                                "viewer": viewer}})


def build(ledger, *, note: str = "", viewer: str = "") -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = {t: ledger.rows(t) for t in PROOF_TABLES}
    counts = ledger.counts()
    leaves = [header_leaf(FORMAT, note, counts, viewer)] + \
        [leaf(r) for t in PROOF_TABLES for r in rows[t]]
    return {
        "format": FORMAT,
        "note": note,
        "counts": counts,
        "viewer": viewer,
        "rows": rows,
        "leaves": leaves,
        "root": merkle_root(leaves),
    }


def write(bundle: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(bundle, indent=1, sort_keys=True), encoding="utf-8")
    return p


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (ok, problems). Makes no network call and needs no server."""
    problems: list[str] = []

    if bundle.get("format") != FORMAT:
        problems.append(f"unknown bundle format {bundle.get('format')!r}")
        return False, problems

    rows = bundle.get("rows") or {}
    stored = list(bundle.get("leaves") or [])
    flat = [(t, r) for t in PROOF_TABLES for r in rows.get(t, [])]

    if len(stored) != len(flat) + 1:
        problems.append(f"bundle lists {len(stored)} leaves for {len(flat)} rows "
                        f"plus one header leaf")
        return False, problems

    want_header = header_leaf(bundle.get("format"), bundle.get("note", ""),
                              bundle.get("counts") or {}, bundle.get("viewer", ""))
    if stored[0] != want_header:
        problems.append("the header (format, note, counts, viewer) does not match its "
                        "leaf: one of those fields was edited after the bundle was built")

    for i, ((table, row), want) in enumerate(zip(flat, stored[1:])):
        got = leaf(row)
        if got != want:
            rid = row.get("id", "?")
            problems.append(
                f"row {i} ({table} id={rid}) does not match its leaf: "
                f"expected {want[:12]}…, recomputed {got[:12]}…")

    root = merkle_root(stored)
    if root != bundle.get("root"):
        problems.append(
            f"the root does not match the leaves: expected {bundle.get('root', '')[:12]}…, "
            f"recomputed {root[:12]}…")

    # Self-consistency. The bundle is what a third party reads, so it has to hold
    # together on its own terms: a reviewer produced a bundle asserting a secret
    # moved A->B with every mint row deleted, and it verified clean.
    minted = {m.get("secret") for m in rows.get("mint", [])}
    mint_ts = {m.get("secret"): m.get("ts") for m in rows.get("mint", [])}
    req_ids = {r.get("id") for r in rows.get("request", [])}

    for s in rows.get("sighting", []):
        sid = s.get("id")
        if s.get("mint_ctx_id") == s.get("seen_ctx_id"):
            problems.append(f"sighting id={sid} names one context on both sides; "
                            "that is not a sighting")
        if s.get("secret") not in minted:
            problems.append(f"sighting id={sid} cites secret "
                            f"{str(s.get('secret'))[:8]}… with no mint row in this "
                            "bundle; nothing shows it was ever issued")
        for key in ("mint_request_id", "seen_request_id"):
            if s.get(key) not in req_ids:
                problems.append(f"sighting id={sid} cites {key}={s.get(key)} "
                                "with no matching request row in this bundle")
        mt = mint_ts.get(s.get("secret"))
        if mt and s.get("ts") and s["ts"] < mt:
            problems.append(f"sighting id={sid} is dated {s['ts']}, before its mint "
                            f"at {mt}; a secret cannot be fetched before it exists")

    for pub in rows.get("published", []):
        if pub.get("secret") not in minted:
            problems.append(f"published id={pub.get('id')} names secret "
                            f"{str(pub.get('secret'))[:8]}… with no mint row in this "
                            "bundle; a secret that was never issued cannot be published")

    return (not problems), problems


def verify_display(bundle: dict[str, Any], shown: dict[str, Any]) -> list[str]:
    """Problems with what a page DISPLAYS, given the bundle it shipped with.

    Two separate things are checked, because they fail differently:

    1. The digest. What is displayed must be byte-for-byte the payload whose hash
       is in the header, so nothing was edited after the bundle was built.
    2. The records. Every record on screen must BE one of the rows under the root:
       same secret, same raw log lines, same counts. A payload exported from a
       different snapshot than its bundle would pass (1) and still show records
       the root never covered.

    viewer/verify.js makes the same two checks; tests/test_js_parity.py runs both.
    """
    problems: list[str] = []
    if not bundle.get("viewer"):
        return ["this bundle does not commit to what the page displays"]
    try:
        digest = payload_digest(shown)
    except TypeError as e:
        return [f"the display cannot be hashed portably: {e}"]
    if digest != bundle["viewer"]:
        problems.append("what this page displays (claim, counters, records) does not "
                        "match the digest in the bundle header: the display half of "
                        "data.js was edited after the bundle was built")

    rows = bundle.get("rows") or {}
    requests = {r.get("id"): r for r in rows.get("request", [])}
    sightings = {s.get("id"): s for s in rows.get("sighting", [])}
    if (shown.get("counts") or {}) != (bundle.get("counts") or {}):
        problems.append("the displayed counters are not the counts under the root")
    for s in shown.get("sightings") or []:
        row = sightings.get(s.get("id"))
        if row is None:
            problems.append(f"displayed record: sighting id={s.get('id')} is not a row "
                            "in this bundle")
            continue
        a = requests.get(row.get("mint_request_id"), {})
        b = requests.get(row.get("seen_request_id"), {})
        same = (s.get("secret") == row.get("secret")
                and s.get("recorded_origin") == row.get("origin")
                and (s.get("issued") or {}).get("raw") == a.get("raw_line")
                and (s.get("requested") or {}).get("raw") == b.get("raw_line")
                and (s.get("issued") or {}).get("ua") == a.get("ua")
                and (s.get("requested") or {}).get("ua") == b.get("ua")
                and (s.get("issued") or {}).get("net") == a.get("ip_net")
                and (s.get("requested") or {}).get("net") == b.get("ip_net"))
        if not same:
            problems.append(f"displayed record for sighting id={s.get('id')} is not the "
                            "request rows under the root")
    return problems


def verify_file(path: str | Path) -> tuple[bool, list[str]]:
    return verify(load(path))


if __name__ == "__main__":  # pragma: no cover
    import sys
    ok, problems = verify_file(sys.argv[1])
    b = load(sys.argv[1])
    n = len(b.get("leaves") or [])
    if ok:
        print(f"PASS  {n} rows checked · root {b['root'][:4]}…{b['root'][-2:]} · "
              f"server not contacted")
    else:
        print("FAIL")
        for p in problems:
            print(f"  - {p}")
    sys.exit(0 if ok else 1)

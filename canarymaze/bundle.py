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

FORMAT = "canary-maze-bundle/4"


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


def canonical(row: dict[str, Any]) -> bytes:
    """A byte-for-byte reproducible serialization: sorted keys, no whitespace,
    escaped non-ASCII, every value a tagged string. Two readers - in two languages -
    must hash the same row to the same leaf. See `viewer/verify.js` for the
    JavaScript twin; `tests/test_bundle.py` pins them together."""
    flat = {str(k): _norm(v) for k, v in row.items()}
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


def header_leaf(fmt: str, note: str, counts: dict[str, Any]) -> str:
    """`counts` and `note` are the two fields a reader actually reads, and they
    were outside the hash: a review set counts.sightings_organic to 4127 on a
    shipped bundle and verification still returned clean. They are covered now."""
    return leaf({"__header__": {"format": fmt, "note": note, "counts": counts}})


def build(ledger, *, note: str = "") -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = {t: ledger.rows(t) for t in PROOF_TABLES}
    counts = ledger.counts()
    leaves = [header_leaf(FORMAT, note, counts)] + [leaf(r) for t in PROOF_TABLES for r in rows[t]]
    return {
        "format": FORMAT,
        "note": note,
        "counts": counts,
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
                              bundle.get("counts") or {})
    if stored[0] != want_header:
        problems.append("the header (format, note, counts) does not match its leaf: "
                        "one of those fields was edited after the bundle was built")

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

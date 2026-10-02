"""The evidence bundle: the part that outlives the server.

The whole wedge of this project is that a reader who does not trust the operator
can check the claim. So the bundle is a plain JSON file, the verifier is stdlib
Python, and neither needs the server, the network, or anything the operator
controls at the moment of checking.

Structure:

    rows    - the proof graph: request, mint, sighting. Nothing else.
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

#: The only tables that may enter a bundle.
PROOF_TABLES = ("request", "mint", "sighting")

FORMAT = "canary-maze-bundle/1"


def canonical(row: dict[str, Any]) -> bytes:
    """A byte-for-byte reproducible serialization: sorted keys, no whitespace,
    escaped non-ASCII. Two readers must hash the same row to the same leaf."""
    return json.dumps(row, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def leaf(row: dict[str, Any]) -> str:
    return sha256(canonical(row)).hexdigest()


def merkle_root(leaves: list[str]) -> str:
    """Binary Merkle root. An empty ledger has a defined root rather than an
    error, so an honest 'nothing observed yet' bundle still verifies."""
    if not leaves:
        return sha256(b"canary-maze/empty").hexdigest()
    level = [bytes.fromhex(h) for h in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256(level[i] + level[i + 1]).digest()
                 for i in range(0, len(level), 2)]
    return level[0].hex()


def build(ledger, *, note: str = "") -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = {t: ledger.rows(t) for t in PROOF_TABLES}
    leaves = [leaf(r) for t in PROOF_TABLES for r in rows[t]]
    return {
        "format": FORMAT,
        "note": note,
        "counts": ledger.counts(),
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

    if len(flat) != len(stored):
        problems.append(f"bundle lists {len(stored)} leaves for {len(flat)} rows")
        return False, problems

    for i, ((table, row), want) in enumerate(zip(flat, stored)):
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

    # A sighting that points at a context equal to its own mint context would be
    # a claim the detector should never have made. Check it here too, because the
    # bundle is what a third party reads and it should be self-consistent.
    for s in rows.get("sighting", []):
        if s.get("mint_ctx_id") == s.get("seen_ctx_id"):
            problems.append(
                f"sighting id={s.get('id')} names one context on both sides; "
                "that is not a sighting")

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

"""Address handling, kept apart from the ledger so it can travel.

`truncate_ip` is a privacy control, not a storage detail: it is the only reason a
full address never reaches disk. It used to live in ledger.py, which meant that
importing it dragged sqlite3 and the schema along - fine on the operator's
machine, wrong for a serverless function that holds no database and must stay
dependency-free. Context derivation needs it on both sides, so it lives here and
ledger.py re-exports it for the callers that already had it.
"""
from __future__ import annotations

import ipaddress


def truncate_ip(addr: str) -> str:
    """Reduce an address to the network we are allowed to keep.

    IPv4 -> /24, IPv6 -> /48. An unparseable address becomes 'unknown' rather than
    being stored verbatim, because the failure mode we refuse is storing a full
    address by accident.
    """
    try:
        ip = ipaddress.ip_address(addr.strip())
    except ValueError:
        return "unknown"
    prefix = 24 if ip.version == 4 else 48
    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return str(net)

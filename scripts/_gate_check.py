#!/usr/bin/env python3
"""Drive one real browser-shaped request through the app and report both gate
numbers: rows that reached storage (must be 0) and refusals (must be >= 1)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze.app import create_app
from canarymaze.ledger import Ledger

BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-GB,en;q=0.9",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
}

db = sys.argv[1]
app = create_app(db_path=db)
with app.test_client() as c:
    c.get("/m/q3-supplier-review", headers=BROWSER,
          environ_overrides={"REMOTE_ADDR": "81.2.3.4"})
led = Ledger(db)
counts = led.counts()
led.close()
print(f"{counts['human_requests']} {counts['humans_turned_away']}")

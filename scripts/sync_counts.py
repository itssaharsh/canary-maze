#!/usr/bin/env python3
"""Write the real test count into every document that states one.

Four judge-facing files once gave four different counts while the suite had
another. Syncing them by hand lasted one commit, so tests/test_results_drift.py
now fails when any of them is wrong, and this is the one command that fixes it.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("README.md", "SUBMISSION.md", "SUBMIT.md",
         "docs/RESULTS.md", "docs/FORM-ANSWERS.md", "site/index.html")


def main() -> int:
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "--co", "-p", "no:cacheprovider"],
                         capture_output=True, text=True, cwd=ROOT).stdout
    n = len(re.findall(r"^\S+::", out, re.M))
    if n < 100:
        print("could not collect the suite", file=sys.stderr)
        return 1
    for name in FILES:
        f = ROOT / name
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8")
        new = re.sub(r"(\d{2,4})(\s+tests\b)", lambda m: f"{n}{m.group(2)}", s)
        new = re.sub(r"(expect:\s*)\d{2,4}(\s+passed)", lambda m: f"{m.group(1)}{n}{m.group(2)}", new)
        if new != s:
            f.write_text(new, encoding="utf-8")
            print(f"  {name}")
    print(f"test count: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

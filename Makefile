.PHONY: install test demo verify results serve clean clean-ledger
PY ?= python3
# Resolved through canarymaze/paths.py, never typed here. A ledger path written
# into this file named a RETIRED ledger as "the live ledger" for two generations,
# and `make clean-ledger` would have deleted the only copy of the evidence behind
# F-0004 while leaving the real live ledger untouched.
LEDGER ?= $(shell $(PY) -c "from canarymaze.paths import ledger_path; print(ledger_path())")

install:
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt

test:
	$(PY) -m pytest -q

demo:
	@bash scripts/demo.sh

verify:
	@bash scripts/verify.sh
	@$(PY) scripts/build_results.py --check

results:
	@$(PY) scripts/build_results.py

# Runs the ledger's own process on the live ledger. Retired ledgers are refused by
# canarymaze/paths.py; see ledgers/archive/README.md for why each one was retired.
# For the public surface use scripts/keep_alive.sh, which also runs the tunnel and
# keeps Vercel pointed at it.
serve:
	CANARY_DB=$(PWD)/$(LEDGER) $(PY) -m canarymaze.app

# NEVER delete a ledger here. `make clean` gets run reflexively between demo runs - including while the public
# surface is live, which silently unlinks the file the server is still writing to
# and loses every piece of evidence collected so far (F-0002). Only demo/verify
# artefacts go here, and they are named distinctly so no glob can catch a ledger.
clean:
	rm -f demo.sqlite3 demo.sqlite3-wal demo.sqlite3-shm
	rm -f verify.sqlite3 verify.sqlite3-wal verify.sqlite3-shm
	rm -rf bundles viewer/data.js viewer/data.json .pytest_cache
	find . -name __pycache__ -type d -not -path "./.venv/*" -prune -exec rm -rf {} +

# Explicit, separate, and never run by accident.
clean-ledger:
	@echo "This deletes the LIVE ledger at $(LEDGER) and every record in it."
	@echo "Nothing in ledgers/archive/ is touched; retired ledgers are kept on purpose."
	@echo "Export a bundle first if you want to keep the evidence:"
	@echo "    python3 scripts/export_all.py --db $(LEDGER) --bundle bundles/keep.json"
	@read -p "type DELETE to confirm: " ok; [ "$$ok" = "DELETE" ] && rm -f $(LEDGER)* || echo "aborted"

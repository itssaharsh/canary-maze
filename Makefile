.PHONY: install test demo verify serve clean clean-ledger
PY ?= python3

install:
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt

test:
	$(PY) -m pytest -q

demo:
	@bash scripts/demo.sh

verify:
	@bash scripts/verify.sh

serve:
	CANARY_DB=$(PWD)/canary.sqlite3 $(PY) -m canarymaze.app

# NEVER delete canary.sqlite3 here. It is the production ledger, and `make clean`
# gets run reflexively between demo runs - including while the public surface is
# live, which silently unlinks the file the server is still writing to and loses
# every piece of evidence collected so far. Only demo/verify artefacts go here.
clean:
	rm -f demo.sqlite3 demo.sqlite3-wal demo.sqlite3-shm
	rm -f verify.sqlite3 verify.sqlite3-wal verify.sqlite3-shm
	rm -rf bundles viewer/data.js viewer/data.json .pytest_cache
	find . -name __pycache__ -type d -not -path "./.venv/*" -prune -exec rm -rf {} +

# Explicit, separate, and never run by accident.
clean-ledger:
	@echo "This deletes the PRODUCTION ledger at canary.sqlite3 and every record in it."
	@echo "Export a bundle first if you want to keep the evidence:"
	@echo "    python3 scripts/export_all.py --db canary.sqlite3 --bundle bundles/keep.json"
	@read -p "type DELETE to confirm: " ok; [ "$$ok" = "DELETE" ] && rm -f canary.sqlite3* || echo "aborted"

.PHONY: install test demo verify serve clean
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

clean:
	rm -f canary.sqlite3 canary.sqlite3-wal canary.sqlite3-shm
	rm -rf bundles viewer/data.json .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

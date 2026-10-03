"""A retired ledger must not be readable by default, and .env must load itself.

Both of these were real failures within minutes of each other. The live ledger
was moved and four defaults were left pointing at the old path, so `--report`
printed "sightings_organic 1" out of a file nobody was writing to while the live
ledger sat at 0. Separately, a script that needed CANARY_SELFTEST_TOKEN was run
in a shell that had not sourced .env, so the operator's own request was recorded
as third-party traffic.
"""
from __future__ import annotations

import pytest

from canarymaze.paths import DEFAULT_LEDGER, is_retired, ledger_path, load_env


def test_default_is_the_live_ledger(monkeypatch):
    monkeypatch.delenv("CANARY_DB", raising=False)
    assert ledger_path() == DEFAULT_LEDGER


def test_canary_db_overrides_the_default(monkeypatch):
    monkeypatch.setenv("CANARY_DB", "/tmp/other.sqlite3")
    assert ledger_path() == "/tmp/other.sqlite3"


def test_explicit_argument_wins_over_the_environment(monkeypatch):
    monkeypatch.setenv("CANARY_DB", "/tmp/other.sqlite3")
    assert ledger_path("/tmp/explicit.sqlite3") == "/tmp/explicit.sqlite3"


def test_a_retired_ledger_is_refused(monkeypatch):
    monkeypatch.delenv("CANARY_ALLOW_RETIRED", raising=False)
    with pytest.raises(SystemExit) as e:
        ledger_path("canary.sqlite3")
    msg = str(e.value)
    assert "retired" in msg
    assert DEFAULT_LEDGER in msg, "the error must say which ledger to use instead"


def test_a_retired_ledger_is_refused_however_the_path_is_spelled(monkeypatch):
    monkeypatch.delenv("CANARY_ALLOW_RETIRED", raising=False)
    for spelling in ("./canary.sqlite3", "/home/x/ai_swarm/canary.sqlite3"):
        with pytest.raises(SystemExit):
            ledger_path(spelling)


def test_a_retired_ledger_can_be_read_deliberately(monkeypatch):
    monkeypatch.delenv("CANARY_ALLOW_RETIRED", raising=False)
    assert ledger_path("canary.sqlite3", allow_retired=True) == "canary.sqlite3"
    monkeypatch.setenv("CANARY_ALLOW_RETIRED", "1")
    assert ledger_path("canary.sqlite3") == "canary.sqlite3"


def test_is_retired_explains_why():
    why = is_retired("canary.sqlite3")
    assert why and "F-0004" in why


def test_load_env_sets_missing_keys_and_never_overwrites(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('FRESH_KEY=from-file\nALREADY_SET="should not win"\n', encoding="utf-8")
    monkeypatch.delenv("FRESH_KEY", raising=False)
    monkeypatch.setenv("ALREADY_SET", "from-environment")

    load_env(env)

    import os
    assert os.environ["FRESH_KEY"] == "from-file"
    assert os.environ["ALREADY_SET"] == "from-environment", \
        "an exported value must beat the file, or a one-off override is impossible"


def test_load_env_is_quiet_when_there_is_no_env_file(tmp_path):
    load_env(tmp_path / "does-not-exist")   # must not raise

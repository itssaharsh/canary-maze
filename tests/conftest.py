import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canarymaze.ledger import Ledger  # noqa: E402


@pytest.fixture()
def ledger():
    led = Ledger(":memory:")
    yield led
    led.close()

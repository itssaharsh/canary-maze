from canarymaze.mint import (canary_path, salt_epoch, secret_for, verify_secret)


def test_same_inputs_give_the_same_secret():
    a = secret_for("/m/x", "ctx1", salt="s", epoch="2026-10-03")
    b = secret_for("/m/x", "ctx1", salt="s", epoch="2026-10-03")
    assert a == b and len(a) == 16


def test_a_different_context_gets_a_different_secret():
    assert secret_for("/m/x", "ctx1", salt="s", epoch="E") != \
           secret_for("/m/x", "ctx2", salt="s", epoch="E")


def test_a_different_path_gets_a_different_secret():
    assert secret_for("/m/x", "c", salt="s", epoch="E") != \
           secret_for("/m/y", "c", salt="s", epoch="E")


def test_rotation_changes_the_secret_but_old_epochs_still_verify():
    old = secret_for("/m/x", "c", salt="s", epoch="2026-10-03")
    new = secret_for("/m/x", "c", salt="s", epoch="2026-10-04")
    assert old != new
    # history stays checkable because the epoch is carried on the mint row
    assert verify_secret(old, "/m/x", "c", salt="s", epoch="2026-10-03")
    assert not verify_secret(old, "/m/x", "c", salt="s", epoch="2026-10-04")


def test_a_secret_cannot_be_forged_without_the_salt():
    assert not verify_secret(secret_for("/m/x", "c", salt="real", epoch="E"),
                             "/m/x", "c", salt="guess", epoch="E")


def test_salt_epoch_is_a_date():
    assert len(salt_epoch()) == 10 and salt_epoch().count("-") == 2


def test_canary_path_shape():
    assert canary_path("abc123", "q3-supplier-review") == "/c/abc123/q3-supplier-review"

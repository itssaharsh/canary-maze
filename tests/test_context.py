"""A context identifier must be stable, must not be an identity, and must survive
the address rotation that one operator does routinely."""
from canarymaze.context import derive, header_order_fingerprint, label

H = {
    "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "Accept": "text/html,*/*;q=0.8",
    "Accept-Encoding": "gzip, br",
}


def test_same_client_gives_the_same_context():
    assert derive(H, "20.171.207.14") == derive(H, "20.171.207.14")


def test_a_different_address_in_the_same_24_is_the_same_context():
    # the whole point of truncating: one client changing its last octet is still
    # one request context, so we do not manufacture a second one
    assert derive(H, "20.171.207.14") == derive(H, "20.171.207.200")


def test_a_different_network_is_a_different_context():
    assert derive(H, "20.171.207.14") != derive(H, "104.28.52.9")


def test_a_different_user_agent_is_a_different_context():
    other = dict(H, **{"User-Agent": "Chrome/124.0.0.0"})
    assert derive(H, "1.2.3.4") != derive(other, "1.2.3.4")


def test_header_order_changes_the_context():
    reordered = {"Accept": H["Accept"], "Accept-Encoding": H["Accept-Encoding"],
                 "User-Agent": H["User-Agent"]}
    assert header_order_fingerprint(H) != header_order_fingerprint(reordered)
    assert derive(H, "1.2.3.4") != derive(reordered, "1.2.3.4")


def test_volatile_headers_do_not_change_the_context():
    noisy = dict(H)
    noisy["Cookie"] = "session=abc"
    noisy["Referer"] = "https://example.invalid/"
    assert derive(noisy, "1.2.3.4") == derive(H, "1.2.3.4")


def test_the_identifier_leaks_neither_address_nor_user_agent():
    ctx = derive(H, "20.171.207.14")
    assert len(ctx) == 12 and all(c in "0123456789abcdef" for c in ctx)
    assert "20.171" not in ctx and "GPTBot" not in ctx


def test_labels_are_display_only_and_follow_first_appearance():
    seen = []
    assert label("aaa", seen) == "A"
    assert label("bbb", seen) == "B"
    assert label("aaa", seen) == "A"

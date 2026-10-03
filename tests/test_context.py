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


def test_header_order_alone_does_not_change_the_context():
    """An earlier version fingerprinted the ORDER of header names. Order is a real
    property of an HTTP stack, but it is also the first thing an intermediary
    disturbs, and a context that splits when a proxy reorders headers turns one
    client into two and manufactures a sighting. The gate chooses to lose
    sightings rather than ledger a human; the context makes the same choice and
    loses a distinction rather than invent a second context."""
    reordered = {"Accept": H["Accept"], "Accept-Encoding": H["Accept-Encoding"],
                 "User-Agent": H["User-Agent"]}
    assert header_order_fingerprint(H) == header_order_fingerprint(reordered)
    assert derive(H, "1.2.3.4") == derive(reordered, "1.2.3.4")


def test_platform_injected_headers_do_not_change_the_context():
    """Reproduces a false sighting recorded on the live surface (F-0006).

    One client, one user-agent, seconds apart: it fetched a maze page and then
    followed its own canary link. The hosting platform injected a different set of
    its own headers on the two routes, the fingerprint hashed every header name it
    saw, and the same client came out as two contexts - so the commonest harmless
    event there is, a crawler re-reading its own link, was written as a sighting.
    """
    on_maze_route = {
        "host": "example.invalid", "x-vercel-id": "bom1::aaaa", **H,
        "x-forwarded-for": "20.171.207.14", "x-real-ip": "20.171.207.14",
        "x-matched-path": "/api/surface", "x-vercel-ip-country": "IN",
        "x-now-route-matches": "1=q3-supplier-review", "forwarded": "for=20.171.207.14",
    }
    on_canary_route = {
        "x-vercel-proxy-signature": "Bearer zzz", "host": "example.invalid", **H,
        "x-vercel-id": "bom1::bbbb", "x-forwarded-for": "20.171.207.14",
        "x-vercel-sc-host": "example.invalid", "x-vercel-ip-city": "Mumbai",
        "x-now-route-matches": "1=deadbeef&2=q3-supplier-review",
        "x-vercel-forwarded-for": "20.171.207.14", "cdn-loop": "edge; loops=1",
    }
    assert derive(on_maze_route, "20.171.207.14") == derive(on_canary_route, "20.171.207.14")
    assert derive(on_maze_route, "20.171.207.14") == derive(H, "20.171.207.14")


def test_an_arbitrary_extra_header_does_not_manufacture_a_context():
    """Adding `X-Trace: 1` used to be enough to present as a second context."""
    assert derive(dict(H, **{"X-Trace": "1"}), "1.2.3.4") == derive(H, "1.2.3.4")


def test_a_different_set_of_client_headers_is_a_different_context():
    """What still distinguishes two HTTP stacks behind one address: which of the
    standard request headers they send at all."""
    fuller = dict(H, **{"Accept-Language": "en-GB", "Cache-Control": "no-cache"})
    assert derive(fuller, "1.2.3.4") != derive(H, "1.2.3.4")


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

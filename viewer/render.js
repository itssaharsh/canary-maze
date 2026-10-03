/* Canary Maze viewer.
 *
 * Every line of copy on this page comes from CANARY_DATA, which the server
 * computes in canarymaze/export.py. Nothing here invents a sentence, a count or a
 * state. That is a correctness requirement: a fresh evaluator given screenshots of
 * an earlier hardcoded version found three on-screen contradictions, including a
 * state whose headline said no second context had been seen while a fully
 * populated second-context card sat beside it. A tool whose thesis is honesty
 * cannot contradict itself on screen. See docs/memory/feedback/U-0001.
 *
 * Data arrives as a plain global from data.js rather than fetch(), so the page
 * works from file:// with no server and no network - which is how a judge who
 * never got dataset access will open it.
 */
(function () {
  "use strict";

  var D = window.CANARY_DATA || null;
  var $ = function (id) { return document.getElementById(id); };
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function text(el, s) { el.textContent = s == null ? "" : String(s); }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* The one marked run of characters on the page, in both records. */
  function markSecret(raw, secret) {
    /* No secret, nothing to mark. Without this guard an undefined secret was
     * searched for as the text "undefined", and a user-agent containing that word
     * made the awaiting state throw and take the whole page down with it. */
    if (!secret) return esc(raw);
    var i = raw.indexOf(secret);
    if (i < 0) return esc(raw);
    return esc(raw.slice(0, i)) +
      '<mark><b>' + esc(secret) + '</b></mark>' +
      esc(raw.slice(i + secret.length));
  }

  /* Edge fades, shown only when there is more text that way. The earlier version
   * pre-scrolled records to centre the secret and produced lines that began
   * mid-token with no affordance, which read as corrupted text at 390px. */
  function wireScroller(pre) {
    var box = pre.parentNode;
    function update() {
      var max = pre.scrollWidth - pre.clientWidth;
      box.setAttribute("data-more-left", pre.scrollLeft > 2 ? "1" : "0");
      box.setAttribute("data-more-right", pre.scrollLeft < max - 2 ? "1" : "0");
    }
    pre.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
    return update;
  }

  /* Bring the secret into view without leaving a half-token at the left edge:
   * scroll to it, then snap back to the nearest whitespace boundary before it. */
  function revealSecret(pre, update) {
    var m = pre.querySelector("mark");
    if (!m) return;
    var pr = pre.getBoundingClientRect(), mr = m.getBoundingClientRect();
    if (mr.left >= pr.left + 8 && mr.right <= pr.right - 8) { update(); return; }
    var want = pre.scrollLeft + (mr.left - pr.left) - 24;
    pre.scrollLeft = Math.max(0, want);
    update();
  }

  function renderDiff(s) {
    /* Who saw the request. "direct" means the ledger's own process held the
     * connection; anything else is a REPORT from a named edge, and a reader is
     * entitled to weigh the two differently. */
    function seenBy(v) {
      return !v || v === "direct" ? "seen directly by the ledger"
                                  : "reported by the " + v + " edge";
    }
    var rows = [
      ["user-agent", s.issued.ua, s.requested.ua],
      ["network", s.issued.net, s.requested.net],
      ["first seen", s.issued.at, s.requested.at],
      ["observed", seenBy(s.issued.via), seenBy(s.requested.via)]
    ];
    var html = '<caption>What separates the two request contexts</caption>' +
      '<thead><tr><td></td>' +
      '<th scope="col">context ' + esc(s.issued.label) + '</th>' +
      '<th scope="col">context ' + esc(s.requested.label) + '</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      var differs = String(r[1]) !== String(r[2]) && r[0] !== "observed";
      html += '<tr class="' + (differs ? "differs" : "same") + '">' +
        '<th scope="row">' + esc(r[0]) + '</th>' +
        '<td>' + esc(r[1] || "not recorded") + '</td>' +
        '<td>' + esc(r[2] || "not recorded") + '</td></tr>';
    });
    return html + "</tbody>";
  }

  function render() {
    if (!D) {
      text($("claim"), "No data loaded. Run `make demo` to build the viewer.");
      $("records").hidden = true; $("diff").hidden = true; $("verify").hidden = true;
      return;
    }

    text($("claim"), D.claim);
    text($("scope"), D.scope_line);

    var c = D.counts || {};
    $("foot").innerHTML =
      "<span>Organic sightings <b>" + (c.sightings_organic || 0) + "</b></span>" +
      "<span>Seeded <b>" + (c.sightings_seeded || 0) + "</b></span>" +
      "<span>Paste-triggered <b>" + (c.sightings_paste || 0) + "</b></span>" +
      "<span>Operator self-test <b>" + (c.sightings_selftest || 0) + "</b></span>" +
      "<span>Human requests in ledger <b class=\"" +
        ((c.human_requests || 0) === 0 ? "zero" : "") + "\">" +
        (c.human_requests || 0) + "</b></span>";
    text($("ledgerline"), (c.mints || 0) + " mints · " + (c.requests || 0) + " requests");

    /* The scope line only bounds a claim that was actually made. In every other
     * state it would be asserting something about a sighting that does not exist. */
    $("scope").hidden = D.state !== "sighting";

    if (D.state === "sighting") {
      var s = D.sightings[0];
      $("diff").innerHTML = renderDiff(s);
      $("diff").hidden = false;
      /* Every origin is named explicitly. The earlier version fell through to
       * "organic traffic" for anything it did not recognise, so a self-test row
       * was published to a reader as third-party evidence. An unknown origin now
       * says it is unknown rather than claiming the strongest reading. */
      var ORIGINS = {
        seeded: "seeded replay · not organic traffic",
        paste: "paste-triggered · a fetcher followed a link the operator published",
        selftest: "the operator's own probe · not third-party traffic",
        organic: "organic traffic"
      };
      $("origin").textContent = ORIGINS[s.origin] || ("origin: " + s.origin + " · unrecognised");
      $("role-a").textContent = "Issued to context " + s.issued.label;
      $("role-b").textContent = "Requested by context " + s.requested.label;
      $("pre-a").innerHTML = markSecret(s.issued.raw, s.secret);
      $("pre-b").innerHTML = markSecret(s.requested.raw, s.secret);
      $("records").hidden = false;
      $("verify").hidden = false;

      var ua = wireScroller($("pre-a")), ub = wireScroller($("pre-b"));
      var marks = document.querySelectorAll("mark");
      function light() {
        revealSecret($("pre-a"), ua); revealSecret($("pre-b"), ub);
        if (reduced) { marks.forEach(function (m) { m.classList.add("lit"); }); return; }
        requestAnimationFrame(function () {
          if (marks[0]) marks[0].classList.add("lit");
          setTimeout(function () { if (marks[1]) marks[1].classList.add("lit"); }, 80);
        });
      }
      light();

    } else if (D.state === "awaiting") {
      /* No second context exists, so none is shown. This is the state the earlier
       * version contradicted itself in. */
      $("diff").hidden = true;
      var m = D.mint_sample;
      $("origin").textContent = "no sighting yet";
      $("role-a").textContent = "Most recent secret issued";
      /* The awaiting record is the page request; the payload deliberately does
       * not carry the secret, so there is nothing here to mark. */
      $("pre-a").innerHTML = esc(m ? m.raw : "");
      $("rec-b").hidden = true;
      $("records").hidden = false;
      $("verify").hidden = false;
      var u = wireScroller($("pre-a"));
      revealSecret($("pre-a"), u);
      var k = document.querySelector("mark");
      if (k) k.classList.add("lit");

    } else {
      $("diff").hidden = true;
      $("records").hidden = true;
      $("verify").hidden = false;     // an empty ledger still produces a valid bundle
    }
  }

  /* Verification runs HERE, in the page, over the bundle the page was shipped.
   * It recomputes every hash with crypto.subtle and contacts nothing. */
  function wireVerify() {
    var btn = $("verify-btn"), out = $("verify-result");
    if (!btn) return;
    btn.addEventListener("click", async function () {
      btn.disabled = true;
      var label = btn.textContent;
      btn.textContent = "Recomputing…";
      out.hidden = true;
      try {
        /* The page is given BOTH objects: the bundle, and what is displayed. A
         * review found that passing only the bundle let a reader edit the claim,
         * the label and the counters on screen and still be told "Verified". */
        var r = await window.CanaryVerify.verifyBundle(window.CANARY_BUNDLE, window.CANARY_DATA);
        out.className = "result " + (r.ok ? "ok" : "bad");
        if (r.ok) {
          out.innerHTML = '<span class="headline">Verified. The server was not contacted.</span>' +
            esc(r.rows) + " hashes recomputed in this page with crypto.subtle · root " +
            esc(String(r.root).slice(0, 4)) + "\u2026" + esc(String(r.root).slice(-2)) +
            " · matches the root shipped with the bundle · and what this page " +
            "displays is what that bundle commits to";
          $("status").textContent = r.rows + " hashes recomputed in the page. The root matches. The server was not contacted.";
        } else {
          out.innerHTML = '<span class="headline">Verification failed.</span>' +
            "<ul>" + r.problems.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") +
            "</ul>The records above are unchanged.";
          $("status").textContent = "Verification failed. " + r.problems.length + " problem(s).";
        }
      } catch (e) {
        out.className = "result bad";
        out.innerHTML = '<span class="headline">Could not verify.</span>' + esc(String(e));
        $("status").textContent = "Could not verify: " + String(e);
      }
      out.hidden = false;
      btn.disabled = false;
      btn.textContent = label;
    });
  }

  render();
  wireVerify();
})();

/* The JavaScript twin of canarymaze/bundle.py.
 *
 * This file exists because an earlier version of this page LIED. It printed
 * "Verified. The server was not contacted." by reading a boolean the server had
 * already computed and shipped in data.js. The page could not verify anything: it
 * was never given the rows or the leaves, and `grep -i crypto viewer/` returned
 * nothing. Editing a record in data.js left the page still saying "Verified".
 *
 * That was the product's single differentiating claim, and it was theatre. So this
 * is the real thing: the bundle ships to the browser, and every hash below is
 * recomputed here with crypto.subtle. If it disagrees with the shipped root, the
 * page says so and names the row.
 *
 * The two implementations must produce identical bytes, which is why bundle.py
 * normalises every value to a tagged string first — JSON.stringify(275.0) is "275"
 * in JavaScript and "275.0" in Python, and that one difference would break every
 * hash. See bundle.py::_norm; tests/test_bundle.py pins the two together.
 */
(function (global) {
  "use strict";

  var LEAF_TAG = 0x00, NODE_TAG = 0x01;
  /* Exactly bundle.py::FORMAT. A prefix match accepted "canary-maze-bundle/99-anything"
   * and verified a format this code had never seen. */
  var FORMAT = "canary-maze-bundle/5";
  /* Same tables, same ORDER, as bundle.py::PROOF_TABLES - the leaves are listed in
   * this order, so a difference here misaligns every hash after the first table. */
  var PROOF_TABLES = ["request", "mint", "sighting", "published"];

  function norm(v) {
    if (v === null || v === undefined) return "n:";
    if (typeof v === "boolean") return v ? "b:1" : "b:0";
    if (typeof v === "number") {
      return Number.isInteger(v) && !Object.is(v, -0) && !isFloatTagged(v)
        ? "i:" + String(v)
        : "f:" + v.toFixed(6);
    }
    /* A nested value is serialised to JSON *before* it is hashed, and Python does
     * that with ensure_ascii=True - so the nested text already holds \uXXXX escapes
     * when the outer serialisation runs, and the outer one then escapes their
     * backslashes. Escaping here, inside, reproduces that. Leaving it to the outer
     * pass alone produced a single backslash where Python has two, and the header
     * leaf of any bundle with a non-ASCII note disagreed between the two sides. */
    if (typeof v === "object") return "j:" + escapeNonAscii(stableStringify(v));
    return "s:" + String(v);
  }

  /* Python distinguishes int from float by type; JSON does not. The bundle marks
   * which fields are floats so the two sides agree. Only delta_s is a float. */
  var FLOAT_FIELDS = { delta_s: true };
  var currentKey = null;
  function isFloatTagged() { return FLOAT_FIELDS[currentKey] === true; }

  function stableStringify(v) {
    if (v === null) return "null";
    if (Array.isArray(v)) return "[" + v.map(stableStringify).join(",") + "]";
    if (typeof v === "object") {
      return "{" + Object.keys(v).sort().map(function (k) {
        return JSON.stringify(k) + ":" + stableStringify(v[k]);
      }).join(",") + "}";
    }
    return JSON.stringify(v);
  }

  /* Python's json.dumps(ensure_ascii=True) escapes every non-ASCII character as
   * \\uXXXX. JSON.stringify does not, so we do it afterwards. */
  function escapeNonAscii(s) {
    /* From U+007F, not U+0080: json.dumps(ensure_ascii=True) escapes DEL too. The
     * range is written with escapes so no invisible character lives in this file. */
    return s.replace(/[\u007f-\uffff]/g, function (c) {
      return "\\u" + ("0000" + c.charCodeAt(0).toString(16)).slice(-4);
    });
  }

  function canonical(row) {
    var keys = Object.keys(row).sort();
    var parts = keys.map(function (k) {
      currentKey = k;
      var out = JSON.stringify(k) + ":" + JSON.stringify(norm(row[k]));
      currentKey = null;
      return out;
    });
    return escapeNonAscii("{" + parts.join(",") + "}");
  }

  function utf8(s) { return new TextEncoder().encode(s); }

  function concat() {
    var arrays = [].slice.call(arguments);
    var len = arrays.reduce(function (n, a) { return n + a.length; }, 0);
    var out = new Uint8Array(len), off = 0;
    arrays.forEach(function (a) { out.set(a, off); off += a.length; });
    return out;
  }

  function hex(buf) {
    return [].map.call(new Uint8Array(buf), function (b) {
      return ("0" + b.toString(16)).slice(-2);
    }).join("");
  }

  async function sha256(bytes) {
    return hex(await crypto.subtle.digest("SHA-256", bytes));
  }

  async function sha256raw(bytes) {
    return new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  }

  async function leaf(row) {
    return sha256(concat(new Uint8Array([LEAF_TAG]), utf8(canonical(row))));
  }

  function fromHex(h) {
    var out = new Uint8Array(h.length / 2);
    for (var i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
    return out;
  }

  async function merkleRoot(leaves) {
    if (!leaves.length) return sha256(utf8("canary-maze/empty/v2"));
    var level = leaves.map(fromHex);
    while (level.length > 1) {
      if (level.length % 2) level.push(level[level.length - 1]);
      var next = [];
      for (var i = 0; i < level.length; i += 2) {
        next.push(await sha256raw(concat(new Uint8Array([NODE_TAG]), level[i], level[i + 1])));
      }
      level = next;
    }
    return sha256(concat(new Uint8Array([NODE_TAG]), utf8(String(leaves.length) + "|"), level[0]));
  }

  async function headerLeaf(fmt, note, counts, viewer) {
    return leaf({ __header__: { format: fmt, note: note, counts: counts, viewer: viewer } });
  }

  /* bundle.py::payload_digest - the hash of what the page displays. */
  async function payloadDigest(shown) {
    return sha256(utf8(escapeNonAscii(stableStringify(shown))));
  }

  function sameCounts(a, b) {
    return stableStringify(a || {}) === stableStringify(b || {});
  }

  /* bundle.py::verify_display. Two checks that fail differently: the digest pins
   * the display to what was committed when the bundle was built; the row
   * comparison requires every record on screen to BE a row under the root. */
  async function displayProblems(b, shown) {
    var problems = [];
    if (!b.viewer) return ["this bundle does not commit to what the page displays"];
    if ((await payloadDigest(shown)) !== b.viewer) {
      problems.push("what this page displays (claim, counters, records) does not match " +
                    "the digest in the bundle header: the display half of data.js was " +
                    "edited after the bundle was built");
    }
    var rows = b.rows || {}, requests = new Map(), sightings = new Map();
    (rows.request || []).forEach(function (r) { requests.set(r.id, r); });
    (rows.sighting || []).forEach(function (x) { sightings.set(x.id, x); });
    if (!sameCounts(shown.counts, b.counts)) {
      problems.push("the displayed counters are not the counts under the root");
    }
    (shown.sightings || []).forEach(function (x) {
      var row = sightings.get(x.id);
      if (!row) {
        problems.push("displayed record: sighting id=" + x.id + " is not a row in this bundle");
        return;
      }
      var a = requests.get(row.mint_request_id) || {}, q = requests.get(row.seen_request_id) || {};
      var i = x.issued || {}, r = x.requested || {};
      var same = x.secret === row.secret && x.recorded_origin === row.origin &&
                 i.raw === a.raw_line && r.raw === q.raw_line &&
                 i.ua === a.ua && r.ua === q.ua && i.net === a.ip_net && r.net === q.ip_net;
      if (!same) {
        problems.push("displayed record for sighting id=" + x.id +
                      " is not the request rows under the root");
      }
    });
    return problems;
  }

  /* Returns {ok, problems, rows, root}. Contacts nothing.
   * `shown` is what the page displays. When it is given, "ok" also means the
   * display is the bundle's: see displayProblems. */
  async function verifyBundle(b, shown) {
    var problems = [];
    if (!b) return { ok: false, problems: ["no bundle was shipped with this page"] };
    if (b.format !== FORMAT) {
      return { ok: false, problems: ["unknown bundle format " + b.format] };
    }

    var rows = b.rows || {}, stored = b.leaves || [];
    var flat = [];
    PROOF_TABLES.forEach(function (t) {
      (rows[t] || []).forEach(function (r) { flat.push([t, r]); });
    });

    if (stored.length !== flat.length + 1) {
      return { ok: false, rows: stored.length,
               problems: ["bundle lists " + stored.length + " leaves for " +
                          flat.length + " rows plus one header leaf"] };
    }

    var wantHeader = await headerLeaf(b.format, b.note || "", b.counts || {}, b.viewer || "");
    if (wantHeader !== stored[0]) {
      problems.push("the header (format, note, counts, viewer) does not match its leaf: " +
                    "one of those fields was edited after the bundle was built");
    }
    if (shown !== undefined) {
      problems = problems.concat(await displayProblems(b, shown));
    }

    for (var i = 0; i < flat.length; i++) {
      var got = await leaf(flat[i][1]);
      if (got !== stored[i + 1]) {
        problems.push("row " + i + " (" + flat[i][0] + " id=" +
                      (flat[i][1].id != null ? flat[i][1].id : "?") +
                      ") does not match its leaf: expected " +
                      stored[i + 1].slice(0, 12) + "…, recomputed " + got.slice(0, 12) + "…");
      }
    }

    var root = await merkleRoot(stored);
    if (root !== b.root) {
      problems.push("the root does not match the leaves: expected " +
                    String(b.root).slice(0, 12) + "…, recomputed " + root.slice(0, 12) + "…");
    }

    // the same self-consistency checks the Python verifier makes
    /* Sets and a Map, not plain objects: {}["constructor"] is truthy, so a sighting
     * citing the secret "constructor" and request ids "valueOf" / "toString" passed
     * every check below with no mint or request rows at all. */
    var minted = new Set(), mintTs = new Map(), reqIds = new Set();
    (rows.mint || []).forEach(function (m) { minted.add(m.secret); mintTs.set(m.secret, m.ts); });
    (rows.request || []).forEach(function (r) { reqIds.add(r.id); });
    (rows.sighting || []).forEach(function (s) {
      if (s.mint_ctx_id === s.seen_ctx_id) {
        problems.push("sighting id=" + s.id + " names one context on both sides; that is not a sighting");
      }
      if (!minted.has(s.secret)) {
        problems.push("sighting id=" + s.id + " cites a secret with no mint row in this bundle");
      }
      ["mint_request_id", "seen_request_id"].forEach(function (k) {
        if (!reqIds.has(s[k])) {
          problems.push("sighting id=" + s.id + " cites " + k + "=" + s[k] +
                        " with no matching request row in this bundle");
        }
      });
      if (mintTs.get(s.secret) && s.ts && s.ts < mintTs.get(s.secret)) {
        problems.push("sighting id=" + s.id + " is dated before its mint; a secret " +
                      "cannot be fetched before it exists");
      }
    });

    (rows.published || []).forEach(function (p) {
      if (!minted.has(p.secret)) {
        problems.push("published id=" + p.id + " names a secret with no mint row in this " +
                      "bundle; a secret that was never issued cannot be published");
      }
    });

    return { ok: problems.length === 0, problems: problems,
             rows: stored.length, root: root };
  }

  global.CanaryVerify = { verifyBundle: verifyBundle, canonical: canonical,
                          leaf: leaf, merkleRoot: merkleRoot, payloadDigest: payloadDigest,
                          FORMAT: FORMAT };
})(window);

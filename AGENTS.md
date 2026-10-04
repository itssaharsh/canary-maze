# AI assistance in this project

The README and the write-up point here, so this says plainly what was done.

**This project was built with heavy AI assistance, throughout.** An AI agent wrote
most of the code, the tests, the documents and this file, working from a human's
direction. The event permits it; stating it is the honest minimum.

What that means for a reader:

- **Every claim in this repository is reproducible by a command, or it is not
  made.** That is not a stylistic choice. An agent that writes its own write-up
  will state things it believes rather than things it checked, and this one did:
  the figure "one actor label carries 899 revisions across 741 distinct addresses"
  was on the product's own face, in the viewer, until an independent review opened
  the file and found that row's label is the empty string. So the numbers a reader
  sees are generated from the data by `scripts/build_results.py`,
  `scripts/label_spread.py` and `scripts/village_reuse.py`, and `make verify`
  fails if a document has drifted from them.
- **The review was adversarial and independent.** Seven reviewers with no part in
  the build read the repository along separate dimensions, and every finding was
  re-verified by a further agent instructed to refute it. Twenty-five were
  confirmed and fixed, each with a test that fails without the fix. Several were
  mutation-checked: the fix is reverted in a scratch copy to prove the test bites.
- **The mistakes are in the repository, not edited out.** `docs/memory/failures/`
  holds seven failure records with the root cause and the cheapest check that
  would have caught each one. Three are self-inflicted: a `make clean` that
  destroyed a live ledger, a verification button that computed nothing while
  claiming it did, and an origin label that published the operator's own `curl` as
  third-party evidence four times over. Two claims that reached the write-up and
  did not survive checking are recorded as withdrawn, in the text a judge reads.

The human direction was: what to build, which risks mattered, and - repeatedly -
to go back and check rather than accept a plausible answer.

## For an agent working on this repository

Read `docs/memory/INDEX.md` before changing a component, and search
`docs/memory/failures/` by error text before retrying anything. A record is a hint
until the files it cites still match. "Done" means a check passed, not that code
was written: run `make verify` and `python3 -m pytest -q`, and regenerate the
reported numbers with `python3 scripts/build_results.py` rather than editing them.

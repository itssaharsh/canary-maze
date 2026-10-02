---
id: F-0002
type: failure
title: make clean deleted the live production ledger during a demo gate
status: active
scope: global-candidate
components: Makefile, canarymaze/ledger.py
triggers: running make clean, adding a clean target, running demo gates while a surface is live
evidence: Makefile
verified_at: 2026-10-02@fb8e250
relates: 
supersedes: 
helpful: 0
harmful: 0
cite_hash: f3e92ddb8baa0e6d
created: 2026-10-02
source: unknown
---

ATTEMPTED: run the hackathon evidence gate 'demo flow three times with a reset between' by calling make clean before each make demo, while the public canary surface was live and serving real traffic against canary.sqlite3. ERROR SIGNATURE: no error at all - the ledger silently reported 0 requests afterwards. ROOT CAUSE: the clean target removed canary.sqlite3, which is the PRODUCTION ledger, not a build artefact. On Linux the running Flask process kept its open handle to the now-unlinked inode, so it carried on writing to a file with no name while a later query created a fresh empty canary.sqlite3 on disk. Evidence collected up to that point, including a human browser visit that was the live test of the human-exclusion gate, was unrecoverable. FIX: clean now removes only demo.sqlite3 and verify.sqlite3 artefacts; deleting the production ledger moved to an explicit clean-ledger target with a typed DELETE confirmation and a reminder to export a bundle first. Verified by writing a sentinel row, running make clean, and confirming the row survives. LESSON: a clean target must never be able to delete state that a running process owns. Name build artefacts distinctly from production state (demo.sqlite3 vs canary.sqlite3) so a glob can never catch both. CHEAPEST EARLY CHECK: read every rm in the build file and ask 'could a long-running process be holding this open right now?'
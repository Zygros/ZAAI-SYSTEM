# Phoenix Ledger Startup Guard — 2026-10-31

## Finding
The existing `Ledger.verify_chain()` detected tampering when called explicitly, but `Ledger.__init__` previously loaded the final stored hash and line count without first verifying the existing file. A caller could therefore initialize a ledger over corrupted history and append new records before discovering the earlier corruption.

## Implemented correction
- `phoenix/core/ledger.py`: constructor now calls `verify_chain()` before loading the last hash and sequence.
- Invalid history raises `ValueError` with a line-specific verification error.
- No existing ledger bytes are rewritten or repaired automatically.
- Added a regression test that tampers with the first event, confirms initialization fails with `hash_mismatch:1`, and confirms the tampered file remains byte-for-byte unchanged.

## Reproducible verification
- Repository: `Zygros/ZAAI-SYSTEM`
- Source PR: #2, open and unmerged.
- Code commit: `4209ea883181629b310511e44e7d1007e00e00ee`
- Regression-test commit: `1371dadfe481dc882377d4f61180fa00389f73af`
- Evidence-bearing branch head: `1371dadfe481dc882377d4f61180fa00389f73af`
- Phoenix Bot Tests run: `41233397444` — SUCCESS, **6 passed in 0.12s**.
- Phoenix Audit run: `41233397451` — SUCCESS.

The suite includes the existing sequential 1,000-cycle stress test and the new fail-closed initialization regression.

## Evidence boundary
This verifies the local hash-chain implementation's startup refusal when the existing file fails its current digest/link checks. It does not prevent a privileged actor from rewriting the entire ledger and recomputing hashes, provide multi-writer locking or fsync durability, establish an external signature/timestamp, or prove production deployment. PR #2 remains open and unmerged.


## Evidence-file chronology addendum
The initial code/test verification above ran on head `1371dadfe481dc882377d4f61180fa00389f73af`. The paired evidence files were then appended without changing the runtime or test logic:
- Markdown evidence commit: `cd5866a2c2ca2cb8433fdf15470bb502f8e7467f`
- JSON receipt commit: `61ce4eeeb9f73e3d96dabedd7eb03a07196aa9c4`

The evidence-bearing head `61ce4eeeb9f73e3d96dabedd7eb03a07196aa9c4` was rechecked:
- Phoenix Bot Tests run `41233446600`: SUCCESS, **6 passed in 0.17s**.
- Phoenix Audit run `41233446244`: SUCCESS.

The earlier test run remains a valid observation on the earlier code/test head; the later runs validate the evidence-bearing head.

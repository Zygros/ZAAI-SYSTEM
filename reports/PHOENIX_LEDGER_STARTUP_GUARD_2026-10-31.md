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

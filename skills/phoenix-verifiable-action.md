# Skill: phoenix-verifiable-action

**Input:** request + optional tool + constraints.

**Output:** result + evidence + verification + provenance.

**Procedure:**
1. Parse intent.
2. Produce explicit plan.
3. Check permissions.
4. Execute.
5. Capture evidence.
6. Verify.
7. If failed, preserve failure and generate repair plan.
8. Retest.
9. Append ledger event.
10. Update memory only with verified state.

**Recovery:** never erase a failed attempt; add a corrective event as a new ledger sequence.

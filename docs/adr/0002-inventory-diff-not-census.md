# 2. A diffable inventory, because the deliverable is progress

Date: 2026-08-24
Status: Accepted

## Context
A post-quantum migration is a multi-year program. A one-shot "here are your 400
RSA usages" report is read once and ignored; what a program needs is to see the
number go down, and to catch backsliding when a new service introduces RSA.

## Decision
Content-address each finding by (surface, location, algorithm) so scans are
comparable, and provide `diff` that reports fixed / new / remaining vulnerable
crypto against a saved baseline, with a net-progress number. `diff` exits non-zero
when new vulnerable crypto appears.

## Consequences
- Progress is measurable ("RSA endpoints 340 -> 180") and regressions are caught
  in CI at the moment they are introduced.
- The identity excludes line numbers within a location only where it would cause
  churn; certificate/config identity is stable across unrelated edits.
- A limitation: moving a usage to a new file reads as fixed-here + new-there. Net
  progress stays correct; the per-item view shows the move. Documented.

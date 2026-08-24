# Threat model & scope

## What this is
A **static crypto-inventory and migration-tracking** tool for post-quantum
readiness. It classifies cryptographic algorithms by quantum vulnerability across
certificates, config/source, and dependencies, and tracks migration progress.

## What it is for
The "harvest now, decrypt later" threat: inventorying quantum-vulnerable crypto so
migration to NIST PQC standards (ML-KEM, ML-DSA, SLH-DSA) can be planned and
measured. It is a planning/compliance aid — directly useful for crypto-agility
requirements in frameworks like CNSA 2.0.

## Trust boundaries
- **Inputs are operator-supplied text** (repos, config, cert dumps). No network,
  no crypto execution, so the tool cannot leak keys or be a pivot.
- **Findings are advice.** The tool never changes crypto; a human migrates.

## Coverage and limits (stated plainly)
- **Static and pattern-based.** It finds algorithm names and parsed certificate
  fields. It does NOT find: algorithms selected at runtime, crypto reached through
  heavy indirection, binary-embedded keys (needs a binary scanner), or the actual
  negotiated cipher of a live endpoint (needs a TLS handshake).
- **Dependency findings are `unknown`, not `broken`.** A crypto library's presence
  is not vulnerable use; these are flagged for review, deliberately not counted as
  vulnerabilities, to avoid the false-positive noise that gets scanners ignored.
- **Classification is a curated map.** A novel or misspelled algorithm token is
  `unknown`; extending the map is a one-line change.
- **Not a proof of quantum-safety.** A clean scan means "no vulnerable crypto found
  on these surfaces", not "quantum-safe".

## Reporting
A misclassification (a broken algorithm rated safe, or vice versa) is a
correctness bug — report to **gabejar@usa.com**.

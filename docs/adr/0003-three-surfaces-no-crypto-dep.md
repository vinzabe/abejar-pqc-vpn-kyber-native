# 3. Scan three surfaces, statically, with no cryptographic dependency

Date: 2026-08-24
Status: Accepted

## Context
The instinct is to scan TLS endpoints by connecting to them. That finds the
visible 30% and misses the crypto that actually causes migration pain: keys in
config, algorithms in source, pinned certs, library choices. It also requires
network access and a crypto library, coupling the tool to a runtime.

## Decision
Scan statically across three surfaces — certificates (parsed from text dumps),
config/source (pattern-based), and declared dependencies. No network, no crypto
library; the tool reads text and classifies algorithm tokens.

## Consequences
- Runs offline, in CI, against a repo or a config export — catching vulnerable
  crypto before deployment, not just on live endpoints.
- Pattern-based source scanning has the usual limits: it finds algorithm *names*,
  not dynamically-selected algorithms or crypto reached through indirection.
  Dependency findings are `unknown` (review-required), never false-positive
  "broken", precisely because presence is not vulnerable use. Stated as a non-goal.
- No live handshake means it cannot report negotiated ciphers of a running
  service; pair with a TLS scanner for that surface. Complementary, not redundant.

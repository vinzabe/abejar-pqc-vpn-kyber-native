"""pqcscan — find every place your estate depends on quantum-vulnerable crypto,
then sequence the migration.

"Harvest now, decrypt later" makes this urgent today: an adversary can capture
encrypted traffic now and decrypt it once a cryptographically-relevant quantum
computer exists. Migrating to post-quantum algorithms starts with knowing where
the vulnerable crypto *is* — and the easy 30% (TLS handshakes) is not the hard
part. The hard part is the crypto that hides: pinned certificates in mobile
binaries, hardcoded keys in config, signing algorithms buried in CI, libraries
statically linked.

This scanner inventories crypto across three surfaces (certificates, config/source,
and declared dependencies), classifies each finding by quantum vulnerability, and
produces a migration plan whose progress you can diff over time.
"""
__version__ = "1.0.0"

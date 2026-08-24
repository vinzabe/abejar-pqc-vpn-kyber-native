# pqc-scanner

**Find every place your estate depends on quantum-vulnerable cryptography — including where it hides — then sequence the migration and track progress.**

"Harvest now, decrypt later" makes this urgent *today*: an adversary can capture your encrypted traffic now and decrypt it once a cryptographically-relevant quantum computer exists. Migrating to NIST's post-quantum algorithms starts with an inventory — and the easy 30% (TLS handshakes) is not the hard part. The hard part is the crypto that hides: RSA keys in config, signing algorithms in source, pinned certificates, crypto libraries whose PQC readiness nobody has checked.

```
$ pqcscan scan ./infra --plan
# Post-quantum migration plan (highest risk first)

1. Migrate to ML-KEM (key exchange) + ML-DSA (signatures)
   5 location(s): app.py:1 (rsa), cert.pem (rsaEncryption), nginx.conf:2 (RSA) …
2. Migrate to SHA-256 or SHA3-256
   1 location(s): app.py:5 (MD5)
```

## What's quantum-vulnerable, and why

| Class | Examples | Quantum status | Migrate to |
|---|---|---|---|
| Asymmetric | RSA, DSA, DH, ECDSA, ECDH, Ed25519, X25519 | 🔴 **broken** by Shor | ML-KEM (Kyber), ML-DSA (Dilithium) |
| Symmetric-128 | AES-128, 3DES | 🟠 weakened by Grover | AES-256 |
| Weak hashes | SHA-1, MD5 | 🟠 weakened | SHA-256 / SHA3-256 |
| Modern symmetric | AES-256, ChaCha20, SHA-256+ | 🟢 safe | — |
| PQC | ML-KEM, ML-DSA, SLH-DSA, Falcon | 🟢 safe | — |

Elliptic curve is **broken**, not "quantum-resistant because it's newer" — a common and dangerous misconception this tool corrects.

## Three surfaces, because crypto hides

1. **Certificates** — signature and public-key algorithms, RSA key sizes, parsed from PEM / `openssl x509 -text` output (no crypto dependency).
2. **Config & source** — `ssl_ciphers` lines, algorithm names in code, PEM key blocks, in `.conf/.yaml/.py/.go/.js/…`.
3. **Dependencies** — crypto libraries flagged for a crypto-agility review (presence ≠ vulnerable use, so these are `unknown`, not hard findings).

## Progress, not a census

Re-scans are comparable, so the deliverable is **migration progress over time**, not a one-off report:

```
$ pqcscan scan ./infra --save baseline.json    # snapshot before migrating
# ...do the work...
$ pqcscan diff baseline.json ./infra
Migration progress: +7 (fixed 8, new 1, remaining 12)

New (regressions):
  ✗ config newservice.conf:4 rsa
```

That regression line — a newly introduced RSA dependency — is what keeps a migration from silently backsliding.

## Quickstart (60 seconds)

```bash
git clone https://github.com/vinzabe/pqc-scanner && cd pqc-scanner
python -m pip install -e ".[dev]"

pqcscan scan ./infra                    # inventory, worst first
pqcscan scan ./infra --plan             # grouped migration plan
pqcscan scan ./infra --save base.json   # snapshot for progress tracking
pqcscan diff base.json ./infra          # what got fixed, what regressed
```

Exit codes: `0` no quantum-vulnerable crypto, `2` vulnerable findings present, `1` error — so CI can gate against new vulnerable crypto.

## Development

```bash
python -m pip install -e ".[dev]"
pytest --cov=pqcscan       # 33 tests, ~91% coverage
mypy --strict src/pqcscan  # clean
ruff check src tests       # clean
```

## License

MIT © vinzabe

"""Algorithm classification: what is quantum-vulnerable, and what replaces it.

Shor's algorithm breaks integer factorization and discrete log, so RSA, DH, and
all of elliptic-curve are broken by a large quantum computer. Grover's algorithm
halves symmetric security, so AES-128 weakens (use 256) but AES-256 is fine. Hash
functions are similarly only weakened, not broken.
"""
from __future__ import annotations

import enum


class Quantum(enum.Enum):
    BROKEN = "broken"            # fully broken by Shor (asymmetric)
    WEAKENED = "weakened"        # security halved by Grover (symmetric/hash)
    SAFE = "safe"                # post-quantum or unaffected
    UNKNOWN = "unknown"

    @property
    def severity(self) -> int:
        return {"broken": 3, "weakened": 2, "unknown": 1, "safe": 0}[self.value]


# Canonical classification. Keys are lowercased algorithm tokens.
_BROKEN = {
    "rsa", "dsa", "dh", "diffie-hellman", "ecdsa", "ecdh", "ec", "ecc",
    "ed25519", "ed448", "x25519", "x448", "secp256r1", "secp384r1",
    "prime256v1", "curve25519",
}
_WEAKENED = {
    "aes-128", "aes128", "3des", "des", "sha-1", "sha1", "md5",
    "sha-224", "hmac-sha1",
}
_SAFE = {
    # NIST PQC standards + symmetric that stays strong
    "ml-kem", "kyber", "ml-dsa", "dilithium", "slh-dsa", "sphincs+",
    "falcon", "aes-256", "aes256", "chacha20", "sha-256", "sha-384",
    "sha-512", "sha3-256", "sha3-512", "hmac-sha256",
}

# Recommended migration target per broken algorithm class.
MIGRATION = {
    "rsa": "ML-KEM (key exchange) + ML-DSA (signatures)",
    "dsa": "ML-DSA (Dilithium)",
    "ecdsa": "ML-DSA (Dilithium) or SLH-DSA (SPHINCS+) for hash-based",
    "ecdh": "ML-KEM (Kyber)",
    "dh": "ML-KEM (Kyber)",
    "ed25519": "ML-DSA (Dilithium)",
    "x25519": "ML-KEM (Kyber)",
    "aes-128": "AES-256",
    "aes128": "AES-256",
    "3des": "AES-256",
    "sha-1": "SHA-256 or SHA3-256",
    "md5": "SHA-256 or SHA3-256",
}


def classify(algorithm: str) -> Quantum:
    a = algorithm.strip().lower()
    if a in _SAFE:
        return Quantum.SAFE
    if a in _BROKEN:
        return Quantum.BROKEN
    if a in _WEAKENED:
        return Quantum.WEAKENED
    # prefix heuristics for versioned tokens
    for tok in _BROKEN:
        if a.startswith(tok):
            return Quantum.BROKEN
    for tok in _WEAKENED:
        if a.startswith(tok):
            return Quantum.WEAKENED
    for tok in _SAFE:
        if a.startswith(tok):
            return Quantum.SAFE
    return Quantum.UNKNOWN


def migration_for(algorithm: str) -> str | None:
    a = algorithm.strip().lower()
    if a in MIGRATION:
        return MIGRATION[a]
    for tok, target in MIGRATION.items():
        if a.startswith(tok):
            return target
    return None

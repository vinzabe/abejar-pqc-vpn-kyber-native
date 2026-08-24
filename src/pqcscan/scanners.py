"""Detectors across three crypto surfaces.

Each detector reads text/data (never executes anything) and yields findings with a
location, the algorithm found, and how it was found. The three surfaces map to the
'easy 30% vs hard 70%' split: certificates are the visible part; config/source and
dependencies are where crypto hides.
"""
from __future__ import annotations

import dataclasses
import re
from pathlib import Path

from .algorithms import Quantum, classify, migration_for


@dataclasses.dataclass(frozen=True, slots=True)
class Finding:
    location: str
    surface: str          # "certificate" | "config" | "source" | "dependency"
    algorithm: str
    quantum: Quantum
    context: str

    @property
    def migration(self) -> str | None:
        return migration_for(self.algorithm)


# --- certificates -----------------------------------------------------------
# Parse the human-readable fields our own `openssl x509 -text` style dumps expose,
# without a crypto dependency: signature algorithm + public-key algorithm/size.
_SIG_ALGO = re.compile(r"(?i)signature algorithm:\s*([a-z0-9\-]+)")
_PUB_ALGO = re.compile(r"(?i)public key algorithm:\s*([a-z0-9\- ]+)")
_RSA_BITS = re.compile(r"(?i)(rsa).{0,40}?\((\d+)\s*bit")


def scan_certificate_text(text: str, location: str) -> list[Finding]:
    out: list[Finding] = []
    for m in _SIG_ALGO.finditer(text):
        algo = _normalize_sig(m.group(1))
        out.append(Finding(location, "certificate", algo, classify(algo),
                           f"signature algorithm: {m.group(1)}"))
    for m in _PUB_ALGO.finditer(text):
        algo = m.group(1).strip().split()[0]
        out.append(Finding(location, "certificate", algo, classify(algo),
                           f"public key: {m.group(1).strip()}"))
    return out


def _normalize_sig(sig: str) -> str:
    s = sig.lower()
    if "rsa" in s:
        return "rsa"
    if "ecdsa" in s:
        return "ecdsa"
    if "ed25519" in s:
        return "ed25519"
    if "dsa" in s:
        return "dsa"
    return s


# --- config / source --------------------------------------------------------
_CONFIG_PATTERNS = (
    re.compile(r"(?i)\b(RSA|DSA|ECDSA|ECDH|DH|Ed25519|X25519)\b"),
    re.compile(r"(?i)\b(AES-?128|AES-?256|3DES|DES|ChaCha20)\b"),
    re.compile(r"(?i)\b(SHA-?1|SHA-?256|SHA-?512|MD5|SHA3-?256)\b"),
    re.compile(r"(?i)ssl_ciphers?\s*[:=]\s*['\"]?([A-Z0-9\-!:+@]+)"),
    re.compile(r"(?i)-----BEGIN (RSA|EC|DSA) (PRIVATE|PUBLIC) KEY-----"),
)


def scan_config_text(text: str, location: str, surface: str = "config"
                     ) -> list[Finding]:
    out: list[Finding] = []
    seen: set[tuple[str, int]] = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat in _CONFIG_PATTERNS:
            for m in pat.finditer(line):
                algo = m.group(1) if m.groups() else m.group(0)
                q = classify(algo)
                if q is Quantum.UNKNOWN:
                    continue
                key = (algo.lower(), lineno)
                if key in seen:
                    continue
                seen.add(key)
                out.append(Finding(f"{location}:{lineno}", surface, algo, q,
                                   line.strip()[:100]))
    return out


# --- dependencies -----------------------------------------------------------
# Crypto libraries that ship classical primitives; flag as "review for crypto-
# agility" rather than a hard finding, since presence != vulnerable use.
_CRYPTO_LIBS = {
    "cryptography", "pycryptodome", "pyopenssl", "rsa", "ecdsa", "paramiko",
    "openssl", "libsodium", "bouncycastle", "node-forge", "jsrsasign",
}


def scan_dependencies(names: list[str], location: str) -> list[Finding]:
    out: list[Finding] = []
    for name in names:
        base = name.strip().lower().split("==")[0].split("@")[0]
        if base in _CRYPTO_LIBS:
            out.append(Finding(location, "dependency", base, Quantum.UNKNOWN,
                               f"crypto library '{base}' — review for PQC support"))
    return out


_CERT_EXTS = (".pem", ".crt", ".cer")
_CONFIG_EXTS = (".conf", ".cfg", ".ini", ".yaml", ".yml", ".toml", ".env",
                ".py", ".js", ".ts", ".go", ".java", ".rb")


def scan_path(root: Path | str) -> list[Finding]:
    root = Path(root)
    files = [root] if root.is_file() else [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and ".git" not in p.parts]
    out: list[Finding] = []
    for f in files:
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        rel = str(f)
        if "-----BEGIN CERTIFICATE-----" in text or "Signature Algorithm:" in text:
            out += scan_certificate_text(text, rel)
        if f.suffix.lower() in _CONFIG_EXTS:
            surface = "source" if f.suffix.lower() in (
                ".py", ".js", ".ts", ".go", ".java", ".rb") else "config"
            out += scan_config_text(text, rel, surface)
    return out

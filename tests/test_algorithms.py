import pytest

from pqcscan.algorithms import Quantum, classify, migration_for


@pytest.mark.parametrize("algo,expected", [
    ("RSA", Quantum.BROKEN), ("ecdsa", Quantum.BROKEN),
    ("Ed25519", Quantum.BROKEN), ("secp384r1", Quantum.BROKEN),
    ("AES-128", Quantum.WEAKENED), ("3DES", Quantum.WEAKENED),
    ("SHA-1", Quantum.WEAKENED), ("MD5", Quantum.WEAKENED),
    ("AES-256", Quantum.SAFE), ("ML-KEM", Quantum.SAFE),
    ("Kyber", Quantum.SAFE), ("SHA-256", Quantum.SAFE),
    ("SomeRandomThing", Quantum.UNKNOWN),
])
def test_classification(algo, expected):
    assert classify(algo) is expected


def test_severity_ordering():
    assert Quantum.BROKEN.severity > Quantum.WEAKENED.severity > Quantum.SAFE.severity


def test_migration_targets():
    assert "ML-KEM" in migration_for("rsa")
    assert "ML-DSA" in migration_for("ecdsa")
    assert "AES-256" in migration_for("3des")
    assert migration_for("aes-256") is None   # already safe


def test_classify_case_insensitive():
    assert classify("rsa") is classify("RSA") is Quantum.BROKEN

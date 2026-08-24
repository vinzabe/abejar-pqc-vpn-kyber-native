from pathlib import Path

from pqcscan.algorithms import Quantum
from pqcscan.scanners import scan_certificate_text, scan_config_text, scan_dependencies, scan_path

FIX = Path(__file__).parent / "fixtures"


def test_config_finds_rsa_and_aes128():
    findings = scan_config_text((FIX / "nginx.conf").read_text(), "nginx.conf")
    algos = {f.algorithm.lower() for f in findings}
    assert any("rsa" in a for a in algos)
    assert any("aes" in a for a in algos)


def test_certificate_signature_algorithm():
    findings = scan_certificate_text((FIX / "cert.pem").read_text(), "cert.pem")
    assert any(f.quantum is Quantum.BROKEN for f in findings)   # RSA sig


def test_source_finds_md5_and_rsa():
    findings = scan_config_text((FIX / "app.py").read_text(), "app.py", "source")
    quantums = {f.quantum for f in findings}
    assert Quantum.BROKEN in quantums    # rsa
    assert Quantum.WEAKENED in quantums  # md5


def test_dependencies_flagged():
    findings = scan_dependencies(["cryptography==41.0", "requests", "pyopenssl"],
                                 "requirements.txt")
    names = {f.algorithm for f in findings}
    assert "cryptography" in names and "pyopenssl" in names
    assert "requests" not in names       # not a crypto lib


def test_scan_path_covers_all_surfaces():
    findings = scan_path(FIX)
    surfaces = {f.surface for f in findings}
    assert "config" in surfaces or "source" in surfaces
    assert "certificate" in surfaces
    assert any(f.quantum is Quantum.BROKEN for f in findings)

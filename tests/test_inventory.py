from pqcscan.algorithms import Quantum
from pqcscan.inventory import Inventory, diff_inventories, migration_plan
from pqcscan.scanners import Finding


def _inv(*findings):
    return Inventory(tuple(findings))


RSA = Finding("a.conf:1", "config", "RSA", Quantum.BROKEN, "x")
AES128 = Finding("b.conf:2", "config", "AES-128", Quantum.WEAKENED, "y")
AES256 = Finding("c.conf:3", "config", "AES-256", Quantum.SAFE, "z")


def test_vulnerable_excludes_safe():
    inv = _inv(RSA, AES128, AES256)
    assert AES256 not in inv.vulnerable()
    assert len(inv.vulnerable()) == 2


def test_by_severity_orders_broken_first():
    inv = _inv(AES128, RSA)
    assert inv.by_severity()[0].quantum is Quantum.BROKEN


def test_diff_reports_fixed_and_new():
    baseline = _inv(RSA, AES128)
    current = _inv(AES128)          # RSA fixed
    d = diff_inventories(baseline, current)
    assert any("rsa" in k for k in d.fixed)
    assert d.new == ()
    assert d.net_progress == 1


def test_diff_detects_regression():
    baseline = _inv(AES128)
    current = _inv(AES128, RSA)     # RSA newly appeared
    d = diff_inventories(baseline, current)
    assert any("rsa" in k for k in d.new)
    assert d.net_progress == -1


def test_migration_plan_groups_by_target():
    inv = _inv(RSA, AES128)
    plan = dict(migration_plan(inv))
    assert any("ML-KEM" in t or "ML-DSA" in t for t in plan)
    assert any("AES-256" in t for t in plan)


def test_json_roundtrip():
    import os
    import tempfile

    from pqcscan.inventory import load_inventory
    inv = _inv(RSA, AES128, AES256)
    f = tempfile.mktemp(suffix=".json")
    with open(f, "w") as fh:
        fh.write(inv.to_json())
    loaded = load_inventory(f)
    os.remove(f)
    assert len(loaded.findings) == 3
    assert len(loaded.vulnerable()) == 2

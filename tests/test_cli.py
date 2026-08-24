import json
from pathlib import Path

import pytest

from pqcscan.cli import EXIT_OK, EXIT_VULNERABLE, main

FIX = Path(__file__).parent / "fixtures"


def test_scan_finds_vulnerable(capsys):
    assert main(["scan", str(FIX)]) == EXIT_VULNERABLE
    assert "broken" in capsys.readouterr().out.lower()


def test_scan_json(capsys):
    main(["scan", str(FIX), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert any(f["quantum"] == "broken" for f in data["findings"])


def test_plan_output(capsys):
    main(["scan", str(FIX), "--plan"])
    assert "migration plan" in capsys.readouterr().out.lower()


def test_scan_clean_dir_exits_ok(tmp_path, capsys):
    (tmp_path / "safe.conf").write_text("cipher = AES-256\nhash = SHA-256\n")
    assert main(["scan", str(tmp_path)]) == EXIT_OK


def test_diff_progress(tmp_path, capsys):
    base = str(tmp_path / "base.json")
    main(["scan", str(FIX), "--save", base])
    capsys.readouterr()
    # diff against a clean dir -> everything "fixed"
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "ok.conf").write_text("AES-256\n")
    main(["diff", base, str(clean)])
    assert "Migration progress" in capsys.readouterr().out


def test_version():
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0

"""CLI: scan, diff against a baseline, and print a migration plan.

Exit codes: 0 no quantum-vulnerable crypto, 2 vulnerable findings present, 1 error.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .algorithms import Quantum
from .inventory import Inventory, diff_inventories, load_inventory, migration_plan
from .scanners import scan_path

EXIT_OK, EXIT_ERROR, EXIT_VULNERABLE = 0, 1, 2

_ICON = {Quantum.BROKEN: "🔴", Quantum.WEAKENED: "🟠",
         Quantum.SAFE: "🟢", Quantum.UNKNOWN: "⚪"}


def cmd_scan(a: argparse.Namespace) -> int:
    inv = Inventory(tuple(scan_path(a.path)))
    if a.save:
        Path(a.save).write_text(inv.to_json())
    if a.json:
        print(inv.to_json())
    elif a.plan:
        _print_plan(inv)
    else:
        _print_inventory(inv)
    return EXIT_VULNERABLE if inv.vulnerable() else EXIT_OK


def cmd_diff(a: argparse.Namespace) -> int:
    baseline = load_inventory(a.baseline)
    current = Inventory(tuple(scan_path(a.path)))
    d = diff_inventories(baseline, current)
    print(f"Migration progress: {d.net_progress:+d} "
          f"(fixed {len(d.fixed)}, new {len(d.new)}, remaining {len(d.remaining)})")
    if d.fixed:
        print("\nFixed:")
        for k in d.fixed:
            print(f"  ✓ {k.replace(chr(31), ' ')}")
    if d.new:
        print("\nNew (regressions):")
        for k in d.new:
            print(f"  ✗ {k.replace(chr(31), ' ')}")
    return EXIT_VULNERABLE if d.new else EXIT_OK


def _print_inventory(inv: Inventory) -> None:
    counts = inv.counts()
    print(f"Crypto inventory: {counts}\n")
    for f in inv.by_severity():
        if f.quantum is Quantum.SAFE:
            continue
        print(f"  {_ICON[f.quantum]} [{f.quantum.value:^8}] {f.surface}: "
              f"{f.algorithm}  @ {f.location}")
        if f.migration:
            print(f"        -> migrate to {f.migration}")


def _print_plan(inv: Inventory) -> None:
    plan = migration_plan(inv)
    if not plan:
        print("No quantum-vulnerable cryptography found.")
        return
    print("# Post-quantum migration plan (highest risk first)\n")
    for i, (target, locations) in enumerate(plan, 1):
        print(f"{i}. Migrate to {target}")
        print(f"   {len(locations)} location(s): "
              + ", ".join(locations[:5])
              + (" …" if len(locations) > 5 else ""))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pqcscan", description=__doc__)
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="inventory crypto in a path")
    s.add_argument("path")
    s.add_argument("--save", help="write inventory JSON (use as a diff baseline)")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true")
    g.add_argument("--plan", action="store_true", help="print a migration plan")
    s.set_defaults(func=cmd_scan)

    d = sub.add_parser("diff", help="compare against a baseline inventory")
    d.add_argument("baseline")
    d.add_argument("path")
    d.set_defaults(func=cmd_diff)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rc: int = args.func(args)
        return rc
    except (OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())

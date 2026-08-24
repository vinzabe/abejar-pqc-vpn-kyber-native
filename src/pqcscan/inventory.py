"""The crypto inventory, its diff over time, and the migration plan.

Inventory is content-addressed by (surface, location, algorithm) so re-scans are
comparable: the deliverable is migration PROGRESS ("RSA endpoints 340 -> 180"),
not a static census. A baseline snapshot lets `diff` report what was fixed, what
regressed, and what is new.
"""
from __future__ import annotations

import dataclasses
import json
from collections import Counter
from pathlib import Path

from .algorithms import Quantum
from .scanners import Finding


@dataclasses.dataclass(frozen=True, slots=True)
class Inventory:
    findings: tuple[Finding, ...]

    def vulnerable(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings
                     if f.quantum in (Quantum.BROKEN, Quantum.WEAKENED))

    def by_severity(self) -> list[Finding]:
        return sorted(self.findings, key=lambda f: f.quantum.severity, reverse=True)

    def counts(self) -> dict[str, int]:
        return dict(Counter(f.quantum.value for f in self.findings))

    def finding_keys(self) -> set[str]:
        return {f"{f.surface}\x1f{f.location}\x1f{f.algorithm.lower()}"
                for f in self.findings}

    def to_json(self) -> str:
        return json.dumps({"findings": [
            {"location": f.location, "surface": f.surface,
             "algorithm": f.algorithm, "quantum": f.quantum.value,
             "context": f.context, "migration": f.migration}
            for f in self.by_severity()]}, indent=2)


@dataclasses.dataclass(frozen=True, slots=True)
class InventoryDiff:
    fixed: tuple[str, ...]       # vulnerable keys present before, gone now
    new: tuple[str, ...]         # vulnerable keys new this scan
    remaining: tuple[str, ...]

    @property
    def net_progress(self) -> int:
        return len(self.fixed) - len(self.new)


def diff_inventories(baseline: Inventory, current: Inventory) -> InventoryDiff:
    b = {k for k in baseline.finding_keys() if _is_vuln(baseline, k)}
    c = {k for k in current.finding_keys() if _is_vuln(current, k)}
    return InventoryDiff(fixed=tuple(sorted(b - c)),
                         new=tuple(sorted(c - b)),
                         remaining=tuple(sorted(b & c)))


def _is_vuln(inv: Inventory, key: str) -> bool:
    for f in inv.vulnerable():
        if f"{f.surface}\x1f{f.location}\x1f{f.algorithm.lower()}" == key:
            return True
    return False


def migration_plan(inv: Inventory) -> list[tuple[str, list[str]]]:
    """Group vulnerable findings by recommended migration target, worst surface
    first. Returns [(migration_target, [locations])]."""
    groups: dict[str, list[str]] = {}
    for f in sorted(inv.vulnerable(),
                    key=lambda f: f.quantum.severity, reverse=True):
        target = f.migration or "review crypto usage"
        groups.setdefault(target, []).append(f"{f.location} ({f.algorithm})")
    return list(groups.items())


def load_inventory(path: Path | str) -> Inventory:
    data = json.loads(Path(path).read_text())
    findings = tuple(
        Finding(location=f["location"], surface=f["surface"],
                algorithm=f["algorithm"], quantum=Quantum(f["quantum"]),
                context=f.get("context", ""))
        for f in data.get("findings", []))
    return Inventory(findings)

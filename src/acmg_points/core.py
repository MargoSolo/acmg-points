"""Parse applied criteria, sum points, evaluate both schemes."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .schemes import CRITERIA, POINTS, STRENGTHS, rules_2015

TOKEN = re.compile(r"^(P(?:VS1|S[1-4]|M[1-6]|P[1-5])|B(?:A1|S[1-4]|P[1-7]))(?:[_\-:]?(Supporting|Moderate|Strong|VeryStrong|StandAlone|Sup|Mod|Str|VS))?$", re.I)
ALIAS = {"sup": "Supporting", "mod": "Moderate", "str": "Strong", "vs": "VeryStrong", "verystrong": "VeryStrong", "standalone": "StandAlone",
         "supporting": "Supporting", "moderate": "Moderate", "strong": "Strong"}


@dataclass
class Applied:
    code: str
    direction: str          # pathogenic | benign
    default_strength: str
    strength: str           # applied (possibly modified) strength
    points: int
    note: str = ""

    @property
    def modified(self) -> bool:
        return self.strength != self.default_strength


def parse(token: str, note: str = "") -> Applied:
    m = TOKEN.match(token.strip())
    if not m:
        raise ValueError(f"unknown criterion token: {token!r} (expected e.g. PVS1, PM2_Supporting, BP4:Strong)")
    code = m.group(1).upper()
    direction, default = CRITERIA[code]
    strength = ALIAS[m.group(2).lower()] if m.group(2) else default
    if strength == "StandAlone" and code != "BA1":
        raise ValueError("StandAlone is only valid for BA1")
    pts = POINTS[direction][strength]
    return Applied(code, direction, default, strength, pts, note)


def band(total: int) -> str:
    for name, lo, hi in POINTS["bands"]:
        if (lo is None or total >= lo) and (hi is None or total <= hi):
            return name
    return "Uncertain significance"


def counts_at_applied_strength(items: list[Applied]) -> dict[str, int]:
    """Count criteria for the 2015 rules at their applied strength (SVI practice)."""
    c = {"PVS": 0, "PS": 0, "PM": 0, "PP": 0, "BA": 0, "BS": 0, "BP": 0}
    for a in items:
        if a.direction == "pathogenic":
            c[{"VeryStrong": "PVS", "Strong": "PS", "Moderate": "PM", "Supporting": "PP"}[a.strength]] += 1
        else:
            c[{"StandAlone": "BA", "VeryStrong": "BS", "Strong": "BS", "Moderate": "BS", "Supporting": "BP"}[a.strength]] += 1
            # note: 2015 has no benign Moderate/VeryStrong; they are counted as Strong (conservative).
    return c


@dataclass
class Result:
    applied: list[Applied]
    total: int
    points_class: str
    rules_class: str
    rules_reason: str
    counts: dict[str, int] = field(default_factory=dict)
    conflict_mode: str = "any"

    @property
    def agree(self) -> bool:
        return self.points_class == self.rules_class

    def to_dict(self) -> dict:
        return {
            "applied": [a.__dict__ | {"modified": a.modified} for a in self.applied],
            "points": {"scheme": POINTS["name"], "total": self.total, "class": self.points_class},
            "rules_2015": {"class": self.rules_class, "reason": self.rules_reason, "counts": self.counts, "conflict_mode": self.conflict_mode},
            "agree": self.agree,
        }


def classify(tokens: list[str], conflict: str = "any") -> Result:
    items = [parse(t) for t in tokens]
    seen = set()
    for a in items:
        if a.code in seen:
            raise ValueError(f"criterion {a.code} applied twice")
        seen.add(a.code)
    total = sum(a.points for a in items)
    counts = counts_at_applied_strength(items)
    rcls, rreason = rules_2015(counts, conflict)
    r = Result(items, total, band(total), rcls, rreason, counts); r.conflict_mode = conflict; return r

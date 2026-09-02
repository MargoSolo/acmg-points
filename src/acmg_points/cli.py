"""CLI: acmg-points classify PVS1 PM2_Supporting ... | table | compare --file"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .core import classify
from .schemes import POINTS


def render(r) -> str:
    L = []
    for a in r.applied:
        mod = f" (modified from {a.default_strength})" if a.modified else ""
        L.append(f"  {a.code:<5} {a.strength:<11} {a.points:+d}{mod}")
    L.append(f"  {'total':<17} {r.total:+d}  → {r.points_class}   [{POINTS['name']}]")
    L.append(f"  2015 rules        → {r.rules_class}   ({r.rules_reason})")
    L.append("  " + ("✅ schemes agree" if r.agree else "⚠️ SCHEMES DISAGREE"))
    return "\n".join(L)


def cmd_classify(a):
    r = classify(a.criteria)
    print(json.dumps(r.to_dict(), indent=2) if a.json else render(r))
    sys.exit(0)


def cmd_table(a):
    print(f"scheme: {POINTS['name']} — {POINTS['citation']}")
    print("pathogenic:", ", ".join(f"{k}=+{v}" for k, v in POINTS["pathogenic"].items()))
    print("benign:    ", ", ".join(f"{k}={v}" for k, v in POINTS["benign"].items()))
    print("bands:     ", ", ".join(f"{n} [{'' if lo is None else lo}..{'' if hi is None else hi}]" for n, lo, hi in POINTS["bands"]))


def cmd_compare(a):
    rows, dis = [], 0
    for line in open(a.file, encoding="utf-8"):
        s = line.split("#", 1)[0].strip()
        if not s:
            continue
        r = classify(s.split())
        dis += 0 if r.agree else 1
        rows.append((s, r))
    print("| criteria | points | points class | 2015 class | agree |")
    print("|---|---|---|---|---|")
    for s, r in rows:
        print(f"| {s} | {r.total:+d} | {r.points_class} | {r.rules_class} | {'✅' if r.agree else '⚠️'} |")
    print(f"\n{len(rows)} cases, {dis} disagreements")


def main(argv=None):
    p = argparse.ArgumentParser(prog="acmg-points", description="Points-based ACMG/AMP classification next to the 2015 rules.")
    p.add_argument("--version", action="version", version=__version__)
    s = p.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("classify", help="classify a set of applied criteria"); c.add_argument("criteria", nargs="+"); c.add_argument("--json", action="store_true"); c.set_defaults(fn=cmd_classify)
    t = s.add_parser("table", help="print the points scheme"); t.set_defaults(fn=cmd_table)
    m = s.add_parser("compare", help="batch: one criteria set per line → table of both schemes"); m.add_argument("--file", required=True); m.set_defaults(fn=cmd_compare)
    a = p.parse_args(argv); a.fn(a)


if __name__ == "__main__":
    main()

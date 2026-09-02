"""Classification schemes.

POINTS: Tavtigian SV et al. (2020) "Fitting a naturally scaled point system to the
ACMG/AMP variant classification guidelines", Hum Mutat 41:1734 — the published
system that ClinGen SVI adopted and that SVC v4.0 (in pilot, unpublished) builds
on. When the official v4 table is published, add it as another scheme here; the
engine does not care which table it sums.

RULES_2015: Richards S et al. (2015) Genet Med 17:405, Table 5 combining rules.
"""
from __future__ import annotations

STRENGTHS = ("Supporting", "Moderate", "Strong", "VeryStrong", "StandAlone")

# Tavtigian 2020, naturally scaled: pathogenic positive, benign negative.
POINTS = {
    "name": "tavtigian2020",
    "citation": "Tavtigian et al. 2020, Hum Mutat 41:1734 (doi:10.1002/humu.24088)",
    "pathogenic": {"Supporting": 1, "Moderate": 2, "Strong": 4, "VeryStrong": 8},
    "benign": {"Supporting": -1, "Moderate": -2, "Strong": -4, "VeryStrong": -8, "StandAlone": -8},
    # inclusive bands
    "bands": [
        ("Pathogenic", 10, None),
        ("Likely pathogenic", 6, 9),
        ("Uncertain significance", 0, 5),
        ("Likely benign", -6, -1),
        ("Benign", None, -7),
    ],
}

# Default (unmodified) strength of every 2015 criterion.
CRITERIA = {
    "PVS1": ("pathogenic", "VeryStrong"),
    **{f"PS{i}": ("pathogenic", "Strong") for i in range(1, 5)},
    **{f"PM{i}": ("pathogenic", "Moderate") for i in range(1, 7)},
    **{f"PP{i}": ("pathogenic", "Supporting") for i in range(1, 6)},
    "BA1": ("benign", "StandAlone"),
    **{f"BS{i}": ("benign", "Strong") for i in range(1, 5)},
    **{f"BP{i}": ("benign", "Supporting") for i in range(1, 8)},
}


def rules_2015(counts: dict[str, int]) -> tuple[str, str]:
    """Richards 2015 Table 5. `counts` keys: PVS, PS, PM, PP, BA, BS, BP
    (criteria counted at their *applied* strength, per ClinGen SVI practice)."""
    pvs, ps, pm, pp = counts["PVS"], counts["PS"], counts["PM"], counts["PP"]
    ba, bs, bp = counts["BA"], counts["BS"], counts["BP"]

    path = (pvs >= 1 and (ps >= 1 or pm >= 2 or (pm == 1 and pp >= 1) or pp >= 2)) \
        or ps >= 2 \
        or (ps == 1 and (pm >= 3 or (pm == 2 and pp >= 2) or (pm == 1 and pp >= 4)))
    likely_path = (pvs >= 1 and pm == 1) \
        or (ps == 1 and 1 <= pm <= 2) \
        or (ps == 1 and pp >= 2) \
        or pm >= 3 \
        or (pm == 2 and pp >= 2) \
        or (pm == 1 and pp >= 4)
    benign = ba >= 1 or bs >= 2
    likely_benign = (bs == 1 and bp >= 1) or bp >= 2

    p_side = "Pathogenic" if path else ("Likely pathogenic" if likely_path else None)
    b_side = "Benign" if benign else ("Likely benign" if likely_benign else None)
    if p_side and b_side:
        return "Uncertain significance", f"conflicting: rules give {p_side} and {b_side} → VUS by the 2015 conflict rule"
    if p_side:
        return p_side, "2015 combining rule met"
    if b_side:
        return b_side, "2015 combining rule met"
    return "Uncertain significance", "no 2015 combining rule met"

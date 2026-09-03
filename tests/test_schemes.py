import pytest
from acmg_points.core import classify, band
from acmg_points.schemes import rules_2015

def cls(*t, conflict="any"): return classify(list(t), conflict)

# ---- Richards 2015 Table 5, one case per row (criteria at default strength) ----
TABLE5 = [
    (("PVS1", "PS1"), "Pathogenic"), (("PVS1", "PM1", "PM2"), "Pathogenic"), (("PVS1", "PM1", "PP1"), "Pathogenic"), (("PVS1", "PP1", "PP2"), "Pathogenic"),
    (("PS1", "PS2"), "Pathogenic"), (("PS1", "PM1", "PM2", "PM3"), "Pathogenic"), (("PS1", "PM1", "PM2", "PP1", "PP2"), "Pathogenic"), (("PS1", "PM1", "PP1", "PP2", "PP3", "PP4"), "Pathogenic"),
    (("PVS1", "PM1"), "Likely pathogenic"), (("PS1", "PM1"), "Likely pathogenic"), (("PS1", "PM1", "PM2"), "Likely pathogenic"), (("PS1", "PP1", "PP2"), "Likely pathogenic"),
    (("PM1", "PM2", "PM3"), "Likely pathogenic"), (("PM1", "PM2", "PP1", "PP2"), "Likely pathogenic"), (("PM1", "PP1", "PP2", "PP3", "PP4"), "Likely pathogenic"),
    (("BA1",), "Benign"), (("BS1", "BS2"), "Benign"), (("BS1", "BP1"), "Likely benign"), (("BP1", "BP2"), "Likely benign"),
    (("PP1",), "Uncertain significance"), (("PM1",), "Uncertain significance"), (("PVS1",), "Uncertain significance"), (("BS1",), "Uncertain significance"), (("BP1",), "Uncertain significance"),
    (("PS1", "PP1"), "Uncertain significance"), (("PM1", "PM2"), "Uncertain significance"),
]

@pytest.mark.parametrize("criteria,expected", TABLE5, ids=[" ".join(c) for c, _ in TABLE5])
def test_table5_rows(criteria, expected):
    assert cls(*criteria).rules_class == expected

# ---- conflict rule, both readings ----
@pytest.mark.parametrize("criteria,any_mode,both_met_mode", [
    (("PS1", "PM1", "BS1"), "Uncertain significance", "Likely pathogenic"),   # P rule met, lone BS1: readings differ
    (("PVS1", "PS1", "BP4"), "Uncertain significance", "Pathogenic"),
    (("BS1", "BS2", "PP3"), "Uncertain significance", "Benign"),
    (("BA1", "PP3"), "Benign", "Benign"),                                                     # BA1 is stand-alone: not overridden by Supporting
    (("PVS1", "PS1", "BS1", "BS2"), "Uncertain significance", "Uncertain significance"),   # both rules met: VUS either way
    (("PVS1", "PS1"), "Pathogenic", "Pathogenic"),                                          # no benign evidence: no conflict
])
def test_conflict_readings(criteria, any_mode, both_met_mode):
    assert cls(*criteria).rules_class == any_mode and cls(*criteria, conflict="both-met").rules_class == both_met_mode
    assert cls(*criteria).to_dict()["rules_2015"]["conflict_mode"] == "any"

def test_conflict_mode_validated():
    with pytest.raises(ValueError): rules_2015({"PVS": 0, "PS": 0, "PM": 0, "PP": 0, "BA": 0, "BS": 0, "BP": 0}, "nope")

# ---- Tavtigian 2020 bands at every boundary ----
@pytest.mark.parametrize("total,expected", [(-8, "Benign"), (-7, "Benign"), (-6, "Likely benign"), (-1, "Likely benign"), (0, "Uncertain significance"), (5, "Uncertain significance"), (6, "Likely pathogenic"), (9, "Likely pathogenic"), (10, "Pathogenic"), (12, "Pathogenic")])
def test_tavtigian_boundaries(total, expected):
    assert band(total) == expected

def test_points_values_and_modifiers():
    r = cls("PVS1", "PS1"); assert r.total == 12 and r.points_class == "Pathogenic"
    r = cls("PM2_Supporting", "PS1", "PM5"); assert [a.points for a in r.applied] == [1, 4, 2] and r.total == 7 and r.points_class == "Likely pathogenic"
    r = cls("PVS1", "PM2_Supporting"); assert r.total == 9 and r.points_class == "Likely pathogenic" and r.rules_class == "Uncertain significance"   # SVI 2020: PM2 Supporting; 2015 needs ≥2 Supporting
    assert cls("BA1").total == -8 and cls("BA1").points_class == "Benign"
    with pytest.raises(ValueError): cls("PVS1", "PVS1")

# ---- the divergences shown in the README ----
def test_readme_divergences():
    r = cls("PVS1", "PM1"); assert (r.total, r.points_class, r.rules_class) == (10, "Pathogenic", "Likely pathogenic") and not r.agree
    r = cls("PVS1", "PP3"); assert (r.total, r.points_class, r.rules_class) == (9, "Likely pathogenic", "Uncertain significance") and not r.agree
    r = cls("PS1", "PM1", "BS1"); assert (r.total, r.points_class, r.rules_class) == (2, "Uncertain significance", "Uncertain significance") and r.agree

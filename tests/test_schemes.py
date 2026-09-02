from acmg_points.core import classify

def cls(*t): return classify(list(t))

def test_points_table_and_bands():
    assert cls("PVS1", "PS1").total == 12 and cls("PVS1", "PS1").points_class == "Pathogenic"
    assert cls("PM1", "PM2", "PP3").total == 5 and cls("PM1", "PM2", "PP3").points_class == "Uncertain significance"
    assert cls("BS1", "BP4").total == -5 and cls("BS1", "BP4").points_class == "Likely benign"
    assert cls("BA1").points_class == "Benign"

def test_2015_rules_agree_on_classic_cases():
    assert cls("PVS1", "PS1").rules_class == "Pathogenic"
    assert cls("PS1", "PM1").rules_class == "Likely pathogenic"
    assert cls("BS1", "BS2").rules_class == "Benign"

def test_known_divergence_pvs1_plus_one_pp():
    r = cls("PVS1", "PP3")            # 2015: needs ≥2 PP → VUS; points: 8+1=9 → LP
    assert r.points_class == "Likely pathogenic" and r.rules_class == "Uncertain significance" and not r.agree

def test_modified_strength():
    r = cls("PM2_Supporting", "PS1", "PM5")
    assert [a.points for a in r.applied] == [1, 4, 2] and r.total == 7 and r.points_class == "Likely pathogenic"

def test_conflict_handling_differs():
    r = cls("PS1", "PM1", "BS1")     # 2015: LP vs (BS1 alone = nothing) → LP ; points: 4+2-4=2 → VUS
    assert r.points_class == "Uncertain significance" and r.rules_class == "Likely pathogenic" and not r.agree

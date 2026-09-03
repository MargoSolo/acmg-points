import json, pytest
from acmg_points import cli


def run(args):
    try:
        cli.main(args)
    except SystemExit as e:
        assert e.code in (0, None)


def test_classify_text_and_json(capsys):
    run(["classify", "PVS1", "PP3"])
    out = capsys.readouterr().out
    assert "SCHEMES DISAGREE" in out and "Likely pathogenic" in out and "Uncertain significance" in out
    run(["classify", "PVS1", "PM2_Supporting", "PP3", "--json"])
    j = json.loads(capsys.readouterr().out)
    assert j["points"]["total"] == 10 and any(a["modified"] for a in j["applied"])


def test_compare_and_table(capsys, tmp_path):
    f = tmp_path / "c.txt"; f.write_text("# comment\nPVS1 PS1\n\nPVS1 PP3  # conflict\n")
    try:
        cli.main(["compare", "--file", str(f)])
    except SystemExit as e:
        assert e.code in (0, None)
    out = capsys.readouterr().out
    assert out.count("|") > 10 and "⚠️" in out and "✅" in out
    try:
        cli.main(["table"])
    except SystemExit as e:
        assert e.code in (0, None)
    assert "Tavtigian" in capsys.readouterr().out


def test_errors():
    with pytest.raises(SystemExit) as e:
        cli.main(["classify", "PVS1", "PVS1"])       # applied twice
    assert e.value.code == 2
    with pytest.raises(SystemExit) as e:
        cli.main(["classify", "NOPE"])
    assert e.value.code == 2

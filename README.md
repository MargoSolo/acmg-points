# acmg-points

**Points-based ACMG/AMP variant classification, side by side with the 2015 combining rules — so you can see exactly where the two systems disagree on your evidence.**

```bash
acmg-points classify PVS1 PP3
```
```
  PVS1  VeryStrong  +8
  PP3   Supporting  +1
  total             +9  → Likely pathogenic   [tavtigian2020]
  2015 rules        → Uncertain significance   (no 2015 combining rule met)
  ⚠️ SCHEMES DISAGREE
```

## What is implemented — and what is deliberately not

- **Points scheme:** Tavtigian et al. 2020, *"Fitting a naturally scaled point system to the ACMG/AMP variant classification guidelines"* (Hum Mutat 41:1734). Supporting +1 · Moderate +2 · Strong +4 · Very Strong +8; benign evidence is the same magnitudes negative; BA1 = −8. Bands: **Pathogenic ≥ 10 · Likely pathogenic 6–9 · VUS 0–5 · Likely benign −6…−1 · Benign ≤ −7.** This is the published system ClinGen SVI adopted and the basis of the forthcoming SVC v4.0.
- **2015 rules:** Richards et al. 2015 (Genet Med 17:405), Table 5 combining rules, including the conflict rule (pathogenic *and* benign rules both met → VUS). Criteria are counted at their **applied** strength (`PM2_Supporting` counts as a Supporting criterion), which is how ClinGen SVI modifiers are meant to be used.
- **Not implemented on purpose:** any "SVC v4.0 points table". v4 is in pilot and unpublished (publication expected 2027). Schemes live in one file (`schemes.py`); the day the official table appears it is a second scheme, not a rewrite.

This is a **combiner**, not a classifier: it assumes you have already decided which criteria apply at which strength. It does not assess evidence, look up gnomAD, or know gene-specific VCEP specifications.

## Where the systems disagree (real cases)

`acmg-points compare --file examples/cases.txt` →

| criteria | points | points class | 2015 class | agree |
|---|---|---|---|---|
| PVS1 PM2 | +10 | Pathogenic | Likely pathogenic | ⚠️ |
| PVS1 PP3 | +9 | Likely pathogenic | Uncertain significance | ⚠️ |
| PS1 PM1 BS1 | +2 | Uncertain significance | Likely pathogenic | ⚠️ |
| PVS1 PS1 | +12 | Pathogenic | Pathogenic | ✅ |
| PM2_Supporting PS1 PM5 | +7 | Likely pathogenic | Likely pathogenic | ✅ |
| PVS1 PS1 BS1 BS2 | +4 | Uncertain significance | Uncertain significance | ✅ |

Three patterns to know:
1. **PVS1 + one Moderate** is *Pathogenic* on points (+10) but only *Likely pathogenic* under 2015 (which needs ≥ 2 Moderate).
2. **PVS1 + one Supporting** reaches *Likely pathogenic* on points (+9); 2015 needs ≥ 2 Supporting and leaves it at VUS.
3. **A lone benign Strong** is invisible to the 2015 pathogenic rules (LP stands), but on points it subtracts 4 and pulls the call down to VUS. Points handle conflicting evidence by arithmetic; 2015 handles it by a blunt "→ VUS" only when *both* sides meet a rule.

Full table: [`examples/compare.md`](examples/compare.md).

## Install

```bash
pip install git+https://github.com/MargoSolo/acmg-points
```
No dependencies.

## Use

```bash
acmg-points classify PVS1 PM2_Supporting PP3        # modified strengths: CODE_Strength (also CODE:Strength, CODE-Sup)
acmg-points classify PS1 PM1 --json                 # machine-readable, per-criterion points and both verdicts
acmg-points compare --file cases.txt                # one criteria set per line, '#' comments → markdown table
acmg-points table                                   # the scheme in force, with citation
```
Accepted strengths: `Supporting` `Moderate` `Strong` `VeryStrong` (`Sup`/`Mod`/`Str`/`VS`), `StandAlone` for BA1 only. A criterion applied twice is an error.

## Limitations

- No gene-specific rules (ClinGen VCEP specifications) — scheme files are the place to add them.
- 2015 has no *benign Moderate / Very Strong*; when you apply such a modifier, the 2015 counter treats it as Strong (conservative). Points use the exact value.
- It will happily sum evidence you should not have applied together (e.g. PVS1 with PM4). Mutual-exclusion checks from the SVI recommendations are on the roadmap.

## Roadmap

- official SVC v4.0 table as a drop-in scheme when published
- SVI modifier library (PVS1 decision-tree levels, PM2_Supporting default, PP3/BP4 calibrated strengths)
- mutual-exclusion / co-application checks
- VCEP-specific schemes (e.g. gene-specific BA1/BS1 cut-offs)
- batch from CSV / VCF INFO, and a tiny web UI
- JOSS paper

## Cite

Solosenko M. *acmg-points: points-based ACMG/AMP classification alongside the 2015 rules.* 2026. (software, v0.1.0)
Please also cite Tavtigian et al. 2020 and Richards et al. 2015 — the science is theirs.

MIT License.

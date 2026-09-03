# Changelog

## 0.1.2 (2026-09-03)

2015 conflict rule made explicit: `--conflict any` (default; any pathogenic + any benign evidence → VUS, per Richards 2015 'criteria for benign and pathogenic are contradictory') or `--conflict both-met` (VUS only when a pathogenic and a benign rule are both met); BA1 remains stand-alone under both. Consequence: PS1 + PM1 + BS1 is now VUS under 2015 by default (was Likely pathogenic). Parameterised tests for every Richards Table 5 row, both conflict readings and all Tavtigian band boundaries (48 tests). Examples lead with PVS1 + PM1; PM2 shown at SVI-2020 Supporting strength. `.coverage` removed from the repository.

## 0.1.1 (2026-09-03)

Public release: PyPI package, Zenodo archiving, PyPI metadata, trusted-publishing workflow, author ORCID. No functional changes.

## Unreleased

- CLI: invalid input (unknown criterion, criterion applied twice) now prints `error: …` and exits 2 instead of a traceback.

## 0.1.0 — 2026-09-03

First release. Tavtigian 2020 points + Richards 2015 rules on the same evidence; classify / compare / table; 14-case comparison.

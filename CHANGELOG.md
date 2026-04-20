# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Plain-language preface and glossary on the dashboard Overview tab
- `CITATION.cff` for academic citation
- `CHANGELOG.md` (this file)
- `RELEASE_NOTES.md` for the v1.0 GitHub release
- `archive/` directory for deprecated source files (retains `voynich_dashboard.jsx`
  as a historical artifact — no longer in the load path)
- `run_all.py` — single-command reproduction of the entire analysis pipeline
- `tests/test_canonical_values.py` — regression tests that verify key findings
  match published values within tolerance, catching silent drift
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running manifest
  validation and canonical value tests on every push

### Changed
- Dashboard Overview tab: each Core Finding and Eliminated Hypothesis now includes
  a plain-language "→" translation line for non-specialist readers
- README Reproduction section updated to document the one-command `run_all.py`
  workflow alongside the per-script commands

## [1.0.0] — 2026-04-19

First public release. Full write-up, frozen datasets, reproducible analysis
pipeline, and interactive dashboard.

### Core Findings
- Non-random sequential structure (Chi² = 1407.8, p ≈ 0)
- Two robust transition rules: CHEDY→QOK attraction (2.625x) and AIIN→QOK
  repulsion (0.504x), both distributed across 77% of CHEDY tokens and 369
  unique token pairs
- AIIN density invariant at 15.0% across Currier A and B (KS p = 0.742)
- Bidirectional self-clustering symmetry: prefix 1.524x, suffix 1.544x,
  ratio 0.99 — unique among 11 tested natural-language comparators

### Included
- 5 analysis scripts (`scripts/`): fetch, validate, core, cross-linguistic,
  stress tests
- 6 canonical result JSONs (`results/`)
- Frozen comparison datasets (~228 MB) with SHA-256 checksums and manifest
- Research paper draft (`docs/voynich_paper_v2_revised.docx`)
- Durable findings document (`docs/durable_findings.md`) with 10 numbered
  findings, caveats, retired claims, and a "minimum viable explanation"
  checklist
- Release documentation with claim ledger (`docs/release_documentation.md`)
- Interactive HTML dashboard (`dashboard/voynich_dashboard.html`)

### Retired claims
Documented in `docs/durable_findings.md` § 3 and `docs/release_documentation.md`:
- "Arabic is the closest structural match" — Arabic is suffix-dominant
  (ratio 0.72); Voynich is symmetric (0.99). Different structural categories.
- "Uralic languages (Estonian, Finnish) match Voynich" — false positives
  from 10K-sentence corpora. Both are suffix-dominant at 100K.
- "15 languages compared" — corrected to 11 verified + 3 pending + 1 control.
- "Self-clustering = 1.44x fixed" — value is method-sensitive, range 0.93x
  to 1.45x.

### Not Claimed
- No language identification
- No decipherment or semantic content

[Unreleased]: https://github.com/amy2213/Voynich-Transition-Grammar/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v1.0.0

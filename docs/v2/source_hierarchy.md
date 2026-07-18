# Version 2 canonical source hierarchy

Status: Phase 1 consolidation. The paper has not been revised.

Authority is strictly ordered:

1. `scripts/_canonical.py`: token parsing, normalization, family predicates,
   ambiguity policies, natural sequence units, transition counting,
   self-clustering utilities, block sampling, and exact diagnostic reports.
2. Frozen raw inputs and `data/manifests/`.
3. Scripts explicitly listed in `run_all.py::CANONICAL_PIPELINE`.
4. Fresh generated outputs named by that pipeline and recorded in
   `results/run_manifest.json`.
5. The complete test suite and `results/test_report.json`.
6. Current Version 2 documents under `docs/v2/` and the root `README.md`.
7. `docs/main.tex`, which is frozen as an audited but unrevised manuscript
   until Phase 1 approval.
8. Historical material under `docs/archive/` and `results/archive/`.

Generated output overrides prose. Prose never overrides generated output.
Bucket names are descriptive labels, not primary scientific estimands.

## Current canonical scope

The Phase 1 canonical pipeline contains dataset validation, the repaired
within-line core analysis, the generated classifier-overlap audit, and both
test entry points. The prefix/suffix comparison is explicitly provisional and
excluded pending Phase 2 boundary-preserving, matched-size reconstruction.


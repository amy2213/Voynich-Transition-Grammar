# Version 2 canonical source hierarchy

Status: Phase 2 central-estimator rebuild. The paper has not been revised.

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
7. `docs/main.tex`, which remains frozen as an audited but unrevised manuscript.
8. Historical material under `docs/archive/` and `results/archive/`.

Generated output overrides prose. Prose never overrides generated output.
Bucket names are descriptive labels, not primary scientific estimands.

## Current canonical scope

The canonical pipeline contains dataset validation, the repaired within-line
core analysis, the generated classifier-overlap audit, the Version 2
boundary-preserving matched prefix/suffix estimator, and both test entry
points. Other July exploratory analyses remain outside the canonical pipeline
unless the claim ledger explicitly says otherwise.

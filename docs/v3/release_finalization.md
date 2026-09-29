# Version 3.0.0 release finalization

Status: corrected release candidate; final exact-head gates pending  
Release tag: `v3.0.0`

## Completed before final freeze

- boundary-safe comparator tokenization implemented and regression-tested;
- Voynich page-block robustness implemented;
- 90% line interval demoted to deletion stability;
- corrected 200-replicate run `36624694412` passed;
- corrected mechanical audit passed;
- complete frozen Version 2 compatibility run `36624694574` passed;
- exact JSON and audit committed with SHA-256 records;
- exact-repeat robustness reported with reproduced values.

## Exact release-commit gates

The final merge commit must again pass:

1. Python compilation;
2. Version 3 regression controls;
3. complete 200-replicate corrected Version 3 validation;
4. Version 3 mechanical audit;
5. corrected numerical fingerprint;
6. complete frozen Version 2 canonical pipeline and suite;
7. verification that `v2.0.0` still resolves to
   `039acf4873104d7c8b60a3a5ff946667a8e0193c`.

## Release assets

The guarded publisher packages the final-run JSON and audit together with the
corrected addendum, interpretation, provenance manifest, Version 2 defect
record, citation metadata, release notes, validation record, manifest, and
SHA-256 sums.

The `.release/v3.0.0-ready` marker is armed on this branch but remains inert
until the reviewed PR is merged to `main`.

Zenodo publication follows the frozen GitHub release. The version-specific DOI
is recorded only after archival ingestion.

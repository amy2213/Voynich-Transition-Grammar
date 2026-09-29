# Changelog

All notable changes to this project are documented here. The project uses
semantic versioning for public releases.

## [3.0.0] - 2026-09-29

### Corrected
- Replaced the Version 2 pooled-marginal prefix/suffix expectation with an
  exact within-unit composition-conditioned ordering expectation.
- Corrected suffix-family nesting to use suffix-aware `endswith` logic.
- Retained alphabetic one-character comparator words for tokenizer symmetry.
- Removed index-paired cross-system sign-test inference from independently
  generated replicate schedules.

### Added
- Two declared Version 3 matched-size validation profiles:
  - 28,447-token main analysis across Voynich plus 14 sufficiently large
    comparators;
  - 14,380-token all-system sensitivity including Ottoman Turkish.
- 200-replicate Version 3 validation workflow and machine audit.
- Release-candidate provenance manifest with frozen input SHA-256 values.
- Explicit post-release Version 2 defect record and Version 3 addendum.

### Result
- Main matched Voynich prefix: 1.013 [1.005, 1.025].
- Main matched Voynich suffix: 1.108 [1.099, 1.116].
- Main matched minimum: 1.013 [1.005, 1.025].
- All 14 large comparators have their entire minimum-side 95% replicate
  interval below 1.0.
- At the smaller all-system target, Voynich minimum is
  1.019 [0.985, 1.060], crossing neutral.

This finite-corpus result does not establish natural-language uniqueness,
language identity, decipherment, syntax, semantics, or a generating mechanism.

## [2.0.0] - 2026-09-11

Version 2 introduced boundary-preserving resampling, symmetric affix discovery,
a frozen scientific tag, machine-readable release evidence, and a Zenodo
software record. Its prefix/suffix cross-corpus claim was reopened on
2026-09-29 after the estimator defects documented in
`docs/v2/post_release_defect_2026-09-29.md`. The frozen Version 2 artifacts
remain unchanged and reproducible.

## [1.0.0] - 2026-04-19

First public release. Historical Version 1 findings and later retractions remain
preserved in repository history and archive directories.

[3.0.0]: https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v3.0.0
[2.0.0]: https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v2.0.0
[1.0.0]: https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v1.0.0

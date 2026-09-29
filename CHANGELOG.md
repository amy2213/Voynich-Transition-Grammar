# Changelog

All notable changes to this project are documented here. The project uses
semantic versioning for public releases.

## [3.0.0] - 2026-09-29

### Corrected
- Replaced the Version 2 pooled-marginal affix expectation with the exact
  within-unit composition-conditioned expectation.
- Corrected suffix nesting.
- Retained valid alphabetic one-character comparator words.
- Broke comparator sequences at excluded or split lexical items so filtering
  cannot manufacture adjacency.
- Removed cross-system replicate-index sign-test inference.
- Demoted 90% Voynich line subsampling to deletion stability.
- Added Voynich page-block robustness for the cluster-aware neutrality claim.

### Added
- Regression tests for numeric gaps, foreign-script gaps, split orthographic
  forms, punctuation-wrapped words, and one-character words.
- Exact adjacent-repeat robustness.
- Committed 200-replicate Version 3 JSON and audit evidence.

### Result
- Voynich page-block prefix/minimum:
  1.020 [0.978, 1.064].
- Voynich page-block suffix:
  1.110 [1.074, 1.145].
- Large comparator minimum-side deletion-stability intervals below 1.0:
  14/14.
- Smaller all-system sensitivity weakens interval separation: Arabic and
  Georgian minimum-side intervals cross 1.0.
- Breaking every exact Voynich repeated-token pair leaves suffix ratio 1.064.

The result is a finite-corpus structural contrast, not evidence of
natural-language uniqueness, language identity, decipherment, semantics,
syntax, or a generating mechanism.

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

# Voynich Transition Grammar v3.0.0

> **POST-RELEASE SCIENTIFIC NOTICE, 2026-09-29:** The Version 3.0.0
> prefix-near-neutral and universal-comparator headlines are **REOPENED**.
> The frozen tag, code, data, and release assets remain unchanged for
> reproducibility. See the post-release defect record:
> https://github.com/amy2213/Voynich-Transition-Grammar/blob/main/docs/v3/post_release_defect_2026-09-29.md

## Why the headline was reopened

Version 3.0.0 correctly fixed the earlier pooled-composition, suffix-nesting,
comparator-seam, and overlapping-line-interval problems.

A later audit found that its complete-line permutation null still treats
line-initial and line-final positions as exchangeable. Voynich line edges have
strong positional structure.

Independent diagnostics from the frozen v3.0.0 baseline show:

- interior-only Voynich page bootstrap:
  - prefix **0.934 [0.893, 0.978]**
  - suffix **1.052 [1.022, 1.088]**
- fixed-endpoint position-aware page bootstrap:
  - prefix **0.919 [0.884, 0.954]**
  - suffix **1.048 [1.017, 1.086]**

The released statement that Voynich prefix ordering is near neutral therefore
does not survive position control. The suffix signal does survive.

The comparator contrast is also sensitive to automatic affix-discovery
thresholds. Arabic's weaker edge changes from 0.864 under the released
thresholds to **1.010** when candidate coverage is widened from 2%–20% to
1%–30%. The "every comparator below neutral" wording is therefore conditional
on the released discovery setting.

## Repeat clarification

The v3.0.0 value 1.064 came from a deliberately harsh stress test that breaks
lines at every exact adjacent repeated-token pair.

A symmetric adjustment subtracting matched exact-repeat contributions from
both observed and expected suffix counts leaves the suffix ratio at
approximately **1.110**.

## Current scientific status

The strongest surviving observation is modest Voynich suffix
self-clustering. Version 3.1 is being developed with:

- an exact fixed-endpoint position-aware null;
- page-level resampling under that null;
- explicit affix-discovery sensitivity;
- symmetric exact-repeat adjustment;
- matched manuscript-line comparators and generating-mechanism controls as
  higher-priority external-validation work.

No Version 3.1 result is frozen by this notice.

## Frozen release provenance

- tag: `v3.0.0`
- commit: `b93e87468347c154cbe9c84cb12ebbbdc9823821`
- publication date: 2026-09-29
- Version-family concept DOI: `10.5281/zenodo.19996904`

The v3.0.0 tag and release assets are not rewritten.

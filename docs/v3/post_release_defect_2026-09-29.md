# Version 3.0.0 post-release defect record

Status: **Version 3.0.0 cross-corpus headline REOPENED**  
Recorded: 2026-09-29  
Frozen release tag: `v3.0.0`  
Frozen release commit: `b93e87468347c154cbe9c84cb12ebbbdc9823821`

## Summary

Version 3.0.0 correctly fixed the Version 2 pooled-composition confound,
suffix-nesting bug, comparator seam creation, and over-narrow Voynich
line-deletion uncertainty framing.

A post-release audit nevertheless identified a new construct-validity problem
and a comparator-sensitivity problem that materially narrow the Version 3.0.0
headline.

The frozen tag, release assets, and evidence remain unchanged for historical
reproducibility. Version 3.1 will replace the affected interpretation rather
than rewriting Version 3.0.0.

## Defect 1: the Version 3.0.0 null treats within-line positions as exchangeable

The Version 3.0.0 primary expectation for class `c` in a natural unit of
length `n`, with `k` occurrences of `c`, is:

```
k(k - 1) / n
```

That is the exact expected adjacent self-transition count under a uniform
permutation of the complete line or sentence while holding its class
composition fixed.

The mathematics is correct for that null.

The construct problem is that the null allows the first and last token of a
Voynich line to move into arbitrary positions. Voynich line beginnings and
endings are known to have strong positional structure. Therefore the Version
3.0.0 ratio can combine:

- genuine local ordering structure; and
- line-position structure, especially line-initial and line-final effects.

The released result was interpreted too broadly as an ordering property.

### Independent diagnostic reproduction

Diagnostics were run from the frozen Version 3.0.0 code/data baseline.

Full-corpus scores:

| Voynich | Prefix | Suffix |
|---|---:|---:|
| all tokens | 1.013 | 1.108 |
| first/last token removed from each line | **0.933** | **1.053** |

Comparator interior-only diagnostics moved in the same general direction:

| System | Interior prefix | Interior suffix |
|---|---:|---:|
| Arabic | 0.836 | 0.945 |
| Georgian | 0.869 | 0.933 |
| Swahili | 0.904 | 0.759 |

The Voynich prefix therefore changes from approximately neutral to clearly
anti-clustered when line-edge tokens are removed. The Version 3.0.0 phrase
"prefix ordering is near neutral" is not stable to line-position control.

A direct analytic fixed-endpoint diagnostic also changes the frozen full-corpus
Voynich scores to approximately:

- prefix: **0.912**;
- suffix: **1.048**.

Independent 200-replicate page-bootstrap diagnostics then confirm the effect.

Interior-only lines:

- prefix median **0.934**, 95% replicate interval **[0.893, 0.978]**;
- suffix median **1.052**, interval **[1.022, 1.088]**.

Exact fixed-endpoint position-aware null:

- prefix median **0.919**, interval **[0.884, 0.954]**;
- suffix median **1.048**, interval **[1.017, 1.086]**;
- prefix below 1.0 in **200/200** replicates;
- suffix at or above 1.0 in **200/200** replicates.

The released Version 3.0.0 prefix-near-neutral interpretation therefore does
not survive direct position control. The suffix effect does survive this
diagnostic. These values are correction diagnostics, not yet a frozen Version
3.1 release claim.

### Historical relevance

Prescott Currier explicitly reported that line beginnings and endings in the
Voynich Manuscript have markedly different distributions from line interiors.
That makes line position a known structural variable rather than an ad hoc
post-release covariate.

Reference:
https://www.voynich.com/currier1.htm

## Defect 2: the "all comparators below neutral" contrast depends on affix-discovery thresholds

Version 3.0.0 used a declared automatic discovery rule:

- 5 families;
- affix lengths 2–3;
- coverage 2%–20%.

The released finite-set result is reproducible under those thresholds.

However, a reasonable discovery sensitivity shows that the cross-corpus
separation is not threshold-invariant.

### Independently reproduced Arabic sensitivity

Arabic full-corpus prefix ratio:

- 3 families: **0.598**;
- released setting: **0.864**;
- widened 1%–30% coverage: **1.075**.

Under the widened 1%–30% coverage rule:

- Arabic prefix: **1.075**;
- Arabic suffix: **1.010**;
- Arabic weaker edge: **1.010**.

That is effectively tied with the released Voynich weaker edge of about
1.013.

Accordingly, the Version 3.0.0 wording that every comparator is below neutral
must be treated as conditional on the release discovery thresholds rather than
as a threshold-robust corpus property.

### Voynich discovery robustness is a strength

Across the released setting plus six reasonable discovery perturbations
covering:

- 3 versus 8 families;
- maximum affix length 3 versus 4;
- released 2%–20% versus widened 1%–30% coverage;

Voynich full-corpus prefix ratios remain in the narrow range:

**1.013–1.025**

and suffix ratios remain approximately:

**1.090–1.108**.

This robustness should be reported in Version 3.1.

## Exact-repeat clarification

Version 3.0.0 reported a deliberately harsh stress test that breaks a line at
every exact adjacent repeated-token pair. That changes sequence structure and
reduces the suffix ratio to about **1.064**.

That number is valid as a worst-case structural stress test, but it is not a
symmetric "remove repeated pairs from the effect" calculation.

A matched subtraction removes exact-repeat contributions from both the
observed and null expected counts for each included affix class.

For the released suffix classes:

- base suffix ratio: **1.1077**;
- exact-repeat observed contribution: **205**;
- exact-repeat expected contribution: **191.241**;
- symmetrically adjusted suffix ratio: **1.1100**.

Across all token identities, not only the included suffix classes, the corpus
contains 249 exact adjacent repeats against an exact within-line expectation of
244.274.

Therefore exact word repetition does not explain the suffix self-clustering.
Version 3.1 should report the symmetric adjustment as the direct repeat
sensitivity and retain 1.064 only if explicitly labeled as the deliberately
lopsided break-at-repeat stress test.

## What remains supported

The strongest surviving Version 3 result is the suffix effect.

It remains above neutral under:

- the released full-corpus estimator;
- removal of the first and last token of every Voynich line;
- the initial analytic fixed-endpoint diagnostic; and
- symmetric exact-repeat subtraction.

The final Version 3.1 page-bootstrap estimate under the position-aware null is
still required before a replacement frozen claim is made.

The Version 3.0.0 prefix-near-neutral headline is reopened.

The Version 3.0.0 all-comparators-below-neutral contrast is also reopened as a
general statement because it depends materially on the affix-discovery
thresholds.

## Release-hygiene defects frozen into Version 3.0.0

The frozen tag also contains stale release-state text:

- `PROJECT_STATE.md` says final exact-head validation is pending;
- `PROJECT_STATE.md` leaves `LAST VERIFIED SCIENTIFIC_COMMIT` pointing to
  the Version 2 scientific commit;
- `docs/v3/release_finalization.md` says the final exact-head gates are still
  pending even though the guarded release workflow later passed and created
  `v3.0.0`.

These are documentation/provenance defects, not numerical defects. They will be
corrected prospectively in repository authority and Version 3.1 rather than by
moving the frozen Version 3.0.0 tag.

## Version 2 Zenodo archival disclosure

The live public Version 2 Zenodo record
(`10.5281/zenodo.22715079`) currently has a generic bounded description and
does **not** literally repeat the retired 14-comparator/self-clustering
headline.

However, the public record contains no "correction", "reopened",
"superseded", "defect", or Version 3 notice.

A correction notice linking to the Version 2 defect record and the current
replacement release remains required archival hygiene.

## Version 3.1 correction plan

Version 3.1 must, before any freeze:

1. define and test an exact position-aware null that holds line-edge positions
   fixed while permuting the interior;
2. retain interior-only analysis as an independent sensitivity;
3. run page-level Voynich resampling under the position-aware null;
4. report affix-discovery sensitivity as part of the cross-corpus result;
5. demote comparator-neutrality language to threshold-conditional unless it
   survives the pre-registered sensitivity grid;
6. replace the repeat interpretation with the symmetric observed/expected
   subtraction, retaining the 1.064 break test only as a worst-case stress
   test;
7. add regression tests that distinguish exchangeable-position and
   fixed-endpoint nulls;
8. update release-state provenance;
9. add correction notices to public archival/release surfaces without changing
   historical tags or files;
10. undergo outside design review before the Version 3.1 result is frozen.

## Claim gate

No Version 3.1 conclusion is promoted by this defect record.

The currently supported interpretation is deliberately narrow:

> The Version 3.0.0 suffix self-clustering signal survives the initial
> line-position, discovery, and repeat diagnostics, but the released prefix
> neutrality and universal comparator-separation headlines are reopened.
> Version 3.1 must use a position-aware null and report discovery-threshold
> sensitivity before a replacement cross-corpus claim is frozen.

# SUPERSEDED: Version 3 pre-correction validation interpretation

Status: **superseded by pre-freeze external-review corrections; replacement analysis pending**  
Validation date: 2026-09-29  
Superseded: 2026-09-29 before release freeze  
Estimator: `3.0.0-dev`  
Matched replicates per profile: 200

> This interpretation used seam-creating comparator tokenization and treated 90% Voynich line subsamples too prominently. It is retained for audit history only. Do not use its 199/200 statement or narrow line-subsample interval as current evidence.

## Executive result

Version 3 changes the interpretation of the prefix/suffix analysis.

Version 2 reported elevated raw self-clustering against pooled corpus marginals.
That result was reopened because the pooled expectation could mix true ordering
with between-line or between-sentence composition.

Version 3 instead conditions the expectation on each natural unit's own class
composition. Under that estimator, the large Version 2 elevation mostly
disappears. The remaining pattern is about **order relative to fixed local
composition**, not raw clustering.

In the main matched analysis at 28,447 tokens, Voynich has:

- prefix order ratio: **1.013**, 95% replicate interval **[1.005, 1.025]**;
- suffix order ratio: **1.108**, 95% replicate interval **[1.099, 1.116]**;
- minimum-side order ratio: **1.013**, 95% replicate interval
  **[1.005, 1.025]**;
- minimum-side ratio at or above the neutral value 1.0 in **199/200**
  replicates.

All 14 eligible large comparators have a minimum-side median below 1.0, and
all 14 have their entire 95% minimum-side replicate interval below 1.0.

This is a finite-set descriptive separation under the declared Version 3
estimator. It is not a p-value and is not a population-level claim about all
languages.

## What the order ratio means

The Version 3 null fixes the class composition of every line or sentence and
asks what self-transition count is expected if order inside that unit were
random.

- ratio > 1: ordering adds self-clustering;
- ratio = 1: ordering contributes no net self-clustering;
- ratio < 1: ordering produces anti-clustering.

The main result therefore does **not** say that Voynich has dramatically high
affix clustering. Its prefix ratio is close to neutral. The notable contrast is
that the tested comparators show order-driven anti-clustering on at least one
token edge, while Voynich does not in the main matched analysis.

## Main matched sensitivity

Target: 28,447 tokens, equal to 90% of the canonical Voynich corpus.  
Systems: Voynich plus 14 comparators.  
Excluded: Ottoman Turkish only, because its preserved corpus is too small for
this target.

| System | Prefix median [95%] | Suffix median [95%] | Minimum median [95%] |
|---|---:|---:|---:|
| Voynich | **1.013 [1.005, 1.025]** | **1.108 [1.099, 1.116]** | **1.013 [1.005, 1.025]** |
| Arabic | 0.804 [0.630, 0.931] | 0.963 [0.824, 1.075] | 0.803 [0.630, 0.927] |
| Estonian | 0.687 [0.552, 0.816] | 1.390 [1.213, 1.513] | 0.687 [0.552, 0.816] |
| Finnish | 0.641 [0.511, 0.790] | 1.286 [1.228, 1.354] | 0.641 [0.511, 0.790] |
| Georgian | 0.911 [0.815, 0.995] | 0.958 [0.905, 1.000] | 0.907 [0.815, 0.973] |
| Hebrew | 0.574 [0.394, 0.775] | 1.651 [1.564, 1.750] | 0.574 [0.394, 0.775] |
| Hungarian | 0.572 [0.470, 0.708] | 0.635 [0.507, 0.765] | 0.564 [0.470, 0.676] |
| Italian | 0.649 [0.552, 0.749] | 0.679 [0.568, 0.796] | 0.633 [0.541, 0.722] |
| KJV English | 0.316 [0.281, 0.355] | 0.093 [0.061, 0.126] | 0.093 [0.061, 0.126] |
| Latin | 0.619 [0.505, 0.732] | 1.592 [1.516, 1.668] | 0.619 [0.505, 0.732] |
| Middle English | 0.483 [0.435, 0.531] | 0.333 [0.263, 0.413] | 0.333 [0.263, 0.413] |
| North Azerbaijani | 0.639 [0.481, 0.803] | 0.794 [0.673, 0.925] | 0.639 [0.481, 0.786] |
| Swahili | 0.937 [0.886, 0.984] | 0.867 [0.816, 0.915] | 0.867 [0.816, 0.915] |
| Tagalog | 0.536 [0.481, 0.594] | 0.889 [0.838, 0.941] | 0.536 [0.481, 0.594] |
| Turkish | 0.613 [0.481, 0.736] | 0.776 [0.640, 0.932] | 0.613 [0.481, 0.732] |

The intervals above are replicate intervals from the declared frozen-corpus
subsampling procedures. They are not confidence intervals for a population of
all languages.

## All-system small-target sensitivity

Target: 14,380 tokens, equal to 90% of the smallest available corpus.  
Systems: all 16 systems, including Ottoman Turkish.

Voynich minimum-side order ratio is **1.019 [0.985, 1.060]**, with 170/200
replicates at or above 1.0. Its suffix result remains above neutral at
**1.108 [1.081, 1.132]**, but its prefix/minimum interval crosses 1.0.

All 15 comparators still have their entire minimum-side 95% replicate interval
below 1.0 in this smaller-target analysis.

This sensitivity matters. At the smaller sample size, the evidence that
Voynich itself is strictly above neutral on both sides is weaker. The
cross-corpus descriptive pattern remains: the tested comparator minimum-side
distributions are below neutral, while Voynich is centered near or above
neutral.

## Full-corpus descriptive values

The complete available corpora give:

- Voynich prefix: **1.013**;
- Voynich suffix: **1.108**;
- Voynich minimum: **1.013**.

Every tested comparator has a full-corpus minimum-side ratio below 1.0.

Full-corpus values are descriptive because corpus sizes differ substantially.

## Relationship to the Version 2 correction

The Version 3 result confirms the central criticism of Version 2: much of the
old apparent elevation was caused by the pooled expectation rather than word
order alone.

That correction does not erase the project. It changes the scientific claim.

The defensible Version 3 observation is that, under a local
composition-conditioned ordering baseline, Voynich is near-neutral to modestly
self-clustering at both token edges, whereas each tested comparator shows
anti-clustering on at least one edge in the declared frozen corpus set.

## Retained independent transition findings

The CHEDY->QOK and AIIN->QOK findings come from a separate within-line
permutation design that already preserves line composition while destroying
order. They are not invalidated by the Version 2 prefix/suffix defect.

Their pooled observed/expected ratios remain descriptive effect-size summaries;
their within-line shuffle evidence is the stronger order-sensitive component.

## What Version 3 does not establish

Version 3 does not establish:

- decipherment or translation;
- language identity;
- that Voynich is or is not a natural language;
- uniqueness among natural languages;
- syntax or semantics;
- a cipher, constructed-language, stenographic, hybrid, or other generating
  mechanism;
- generalization beyond the frozen tested corpora, transcription, discovery
  rules, and sequence-unit definitions.

No cross-system p-value is reported. Replicate indices are not paired across
systems.

## Validation record

The 200-replicate validation workflow completed successfully. The mechanical
audit passed all declared structural checks, including output completeness,
supported class counts, side-aware suffix nesting, sampling profiles, and the
prohibition on cross-system replicate pairing.

Machine-generated evidence is retained as the GitHub Actions artifact
`v3-validation-200-replicates` for the validation run.

## Recommended claim wording

> Under a composition-conditioned within-unit ordering baseline, the Voynich
> EVA transcription is near-neutral for prefix self-transition ordering and
> modestly self-clustering for suffix ordering. In the 28,447-token matched
> analysis, its minimum-side order ratio is 1.013 [1.005, 1.025], while all 14
> tested large comparators have minimum-side 95% replicate intervals below
> 1.0. At the smaller 14,380-token all-system target, the Voynich minimum
> interval crosses 1.0, so the result is reported as a finite-corpus structural
> contrast rather than evidence of language identity or natural-language
> uniqueness.

## Release recommendation

The Version 3 estimator and validation result are suitable to advance to a
release-candidate/addendum stage. The frozen Version 2 artifact should remain
unchanged and linked to its post-release defect record.

# SUPERSEDED: Version 3 20-replicate smoke validation record

Date: 2026-09-29  
Superseded: 2026-09-29 by the corrected 200-replicate pre-freeze analysis  
Status: **superseded smoke evidence; not current scientific authority**  
GitHub Actions run: `59` / `36607933106`  
Candidate artifact: `v3-candidate-evidence`  
Artifact SHA-256: `38e17487d61cf5f791f2bab863425371b7ddd9debf8112f769710d754bb5f527`

> This file is retained only as an audit trail of an early 20-replicate smoke run. It must not be cited for current Version 3 numerical claims. The final pre-freeze analysis adds boundary-safe comparator tokenization and Voynich page-block robustness.

## Gates completed

- all Python sources compiled successfully;
- targeted Version 3 regression controls passed;
- the Version 3 estimator executed successfully against the frozen corpus set;
- the generated JSON artifact uploaded successfully;
- suffix nesting uses side-aware logic in Version 3;
- one-character comparator words are retained;
- the ordering baseline is the exact within-unit permutation expectation;
- no cross-system replicate-index p-values are generated.

The full legacy Version 2 reproduction pipeline is a separate compatibility
gate and is not replaced by this candidate run.

## Primary full-corpus order ratios

A ratio of 1 means observed self-transitions equal the exact expectation after
conditioning on every natural unit's class composition. Values below 1 indicate
order-driven anti-clustering; values above 1 indicate order-driven
self-clustering.

| System | Prefix | Suffix | Weaker side |
|---|---:|---:|---:|
| **Voynich** | **1.013** | **1.108** | **1.013** |
| Georgian | 0.906 | 0.959 | 0.906 |
| Swahili | 0.937 | 0.867 | 0.867 |
| Arabic | 0.806 | 0.959 | 0.806 |
| Estonian | 0.681 | 1.390 | 0.681 |
| Italian | 0.651 | 0.700 | 0.651 |
| Finnish | 0.640 | 1.283 | 0.640 |
| North Azerbaijani | 0.631 | 0.811 | 0.631 |
| Turkish | 0.617 | 0.833 | 0.617 |
| Latin | 0.599 | 1.591 | 0.599 |
| Hebrew | 0.593 | 1.657 | 0.593 |
| Hungarian | 0.595 | 0.637 | 0.595 |
| Tagalog | 0.536 | 0.888 | 0.536 |
| Middle English | 0.484 | 0.353 | 0.353 |
| Ottoman Turkish | 0.311 | 0.342 | 0.311 |
| KJV English | 0.315 | 0.089 | 0.089 |

The corrected estimator therefore does **not** reproduce the Version 2 story
that Voynich is strongly self-clustered on both sides. Its prefix side is near
the composition-conditioned null, while its suffix side is modestly above the
null. Every tested comparator has at least one side below 1 in this candidate
run.

Some natural-language comparators have strong suffix self-clustering while
showing prefix anti-clustering. The relevant structural contrast is therefore
not "natural languages always anti-cluster on both sides." The candidate
pattern is that each tested comparator has a weaker affix side below its own
composition-conditioned null, whereas Voynich's weaker side is approximately
neutral.

## Matched-size sensitivity

The common target was 14,380 tokens, defined as 90% of the smallest available
system. Twenty without-replacement natural-unit subsamples were generated per
system.

Selected weaker-side medians and 95% replicate intervals:

| System | Median weaker side | 95% replicate interval |
|---|---:|---:|
| **Voynich** | **1.017** | **[0.991, 1.047]** |
| Georgian | 0.908 | [0.850, 1.001] |
| Swahili | 0.853 | [0.814, 0.904] |
| Arabic | 0.791 | [0.601, 0.920] |
| Italian | 0.633 | [0.529, 0.713] |
| Latin | 0.618 | [0.516, 0.772] |
| Ottoman Turkish | 0.311 | [0.275, 0.346] |
| KJV English | 0.096 | [0.067, 0.125] |

These intervals are robustness summaries of independent subsampling
distributions. They are **not** paired confidence intervals and are not used to
manufacture a cross-system p-value.

## Differences from the external review's preliminary control

The candidate result supports the review's central diagnosis that much of the
Version 2 Voynich elevation came from composition rather than word order.
However, the exact numeric values differ because Version 3 also:

- fixes suffix nesting;
- retains one-character comparator words;
- uses an exact composition-conditioned expectation rather than dividing two
  noisy pooled scores;
- uses an exposure-weighted aggregate across supported classes rather than an
  unweighted mean;
- includes Ottoman Turkish in the common-size sensitivity analysis.

## Remaining cautions before claim promotion

1. The current validation uses 20 matched-size replicates as a smoke/robustness
   run, not the final release replicate count.
2. Hebrew discovers only two supported full-corpus prefix families under the
   declared thresholds; the aggregate estimator reduces the leverage problem,
   but family-count sensitivity should still be reviewed.
3. Leipzig records preserve sentence units but not source-document nesting.
   The composition-conditioned null removes document-mix inflation from the
   order statistic, but genre and corpus-source mismatch remain limitations.
4. EVA/transcription dependence remains.
5. No mechanism, language identity, or decipherment follows from this pattern.
6. A formal cross-system hypothesis test has not been specified or approved.

## Current interpretation

The defensible candidate statement is:

> Under automatic affix discovery and an exact within-unit
> composition-conditioned ordering null, Voynich is near neutral on prefix
> self-transition ordering and modestly self-clustered on suffix ordering,
> while every tested comparator has at least one affix side showing
> anti-clustering in the full-corpus candidate analysis.

This remains a Version 3 candidate statement until the claim gate is explicitly
closed after final replication and review.

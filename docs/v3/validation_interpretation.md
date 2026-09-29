# Version 3 validation interpretation

Status: corrected 200-replicate pre-freeze result  
Validation date: 2026-09-29  
Estimator: `3.0.0`  
Matched replicates per profile: 200

## Executive result

Version 3 measures affix-class ordering against the exact expectation obtained
after conditioning on each natural line or sentence fragment's own class
composition. A pre-freeze external review identified two additional issues
before Version 3 was tagged:

1. comparator regex filtering could join surviving words across excluded or
   split lexical material;
2. 90% Voynich line-deletion replicates overlap too heavily to serve as the
   cluster-aware uncertainty summary for Voynich.

Both issues are corrected in the current result. Comparator tokenization now
breaks the sequence at excluded or split whitespace items, and Voynich receives
a separate page-block bootstrap while retaining line boundaries inside pages.

The corrected result is narrower than the earlier candidate claim:

- **Voynich prefix ordering is near neutral under page-level resampling.**
- **Voynich suffix ordering remains modestly self-clustering.**
- Every tested comparator has a full-corpus minimum-side point estimate below
  1.0.
- In the 28,447-token sequence-unit deletion-stability analysis, all 14 large
  comparators have their entire minimum-side 95% replicate interval below 1.0.
- At the smaller 14,380-token all-system target, Arabic and Georgian
  minimum-side intervals cross 1.0, so that smaller sensitivity does not show
  complete interval separation.

These are finite-corpus robustness summaries. They are not population
confidence intervals and are not a natural-language classifier.

## Voynich page-block robustness

Target: 28,447 tokens. Pages are sampled with replacement while the lines
nested inside each sampled page remain separate sequence units.

| Metric | Median | 95% replicate interval | Fraction >= 1 |
|---|---:|---:|---:|
| Prefix order ratio | **1.020** | **[0.978, 1.064]** | 0.770 |
| Suffix order ratio | **1.110** | **[1.074, 1.145]** | 1.000 |
| Minimum-side ratio | **1.020** | **[0.978, 1.064]** | 0.770 |

The prefix/minimum interval crosses the neutral value 1.0. The suffix interval
does not. The earlier 199/200 line-deletion statement is therefore not used as
headline evidence about Voynich neutrality.

## Line-deletion stability

The 90% without-replacement Voynich line analysis is retained as a deletion
stability diagnostic:

- prefix: 1.013 [1.005, 1.025];
- suffix: 1.108 [1.099, 1.116];
- minimum: 1.013 [1.005, 1.025].

Those narrow intervals mostly reflect highly overlapping 90% samples and are
not the cluster-aware uncertainty summary.

For the 14 sufficiently large comparators, the same 28,447-token
sequence-unit deletion analysis gives minimum-side intervals entirely below
1.0 for **14/14** systems after boundary-safe tokenization.

Notably, individual edges can cross neutral. Arabic suffix is centered near
1.0 and Georgian suffix overlaps 1.0. The claim concerns the weaker/minimum
edge in this declared stability analysis, not universal anti-clustering on both
edges.

## Full-corpus descriptive values

Boundary-safe comparator tokenization gives:

| System | Prefix | Suffix | Minimum |
|---|---:|---:|---:|
| Voynich | **1.013** | **1.108** | **1.013** |
| Arabic | 0.864 | 1.010 | 0.864 |
| Estonian | 0.724 | 1.380 | 0.724 |
| Finnish | 0.676 | 1.279 | 0.676 |
| Georgian | 0.910 | 0.979 | 0.910 |
| Hebrew | 0.539 | 1.614 | 0.539 |
| Hungarian | 0.603 | 0.566 | 0.566 |
| Italian | 0.688 | 0.711 | 0.688 |
| KJV English | 0.316 | 0.090 | 0.090 |
| Latin | 0.610 | 1.543 | 0.610 |
| Middle English | 0.512 | 0.325 | 0.325 |
| North Azerbaijani | 0.496 | 0.756 | 0.496 |
| Ottoman Turkish | 0.306 | 0.345 | 0.306 |
| Swahili | 0.960 | 0.886 | 0.886 |
| Tagalog | 0.536 | 0.903 | 0.536 |
| Turkish | 0.637 | 0.747 | 0.637 |

All 15 comparator minimum-side point estimates are below 1.0.

## All-system small-target sensitivity

Target: 14,380 tokens across all 16 systems.

Voynich gives:

- prefix: 1.019 [0.985, 1.060];
- suffix: 1.108 [1.081, 1.132];
- minimum: 1.019 [0.985, 1.060].

Voynich prefix/minimum again crosses neutral. Among the 15 comparators, 13 have
their entire minimum-side interval below 1.0. Arabic
[0.622, 1.003] and Georgian [0.807, 1.006] cross neutral at this smaller target.
Their minimum-side medians remain below 1.0.

This sensitivity is retained precisely because it weakens interval separation.

## Boundary-safe comparator correction

Comparator alphabetic words of length 1 remain valid. In addition, any
whitespace item that is excluded or would split into multiple accepted word
runs now terminates the current sequence. Examples covered by regression tests
include:

- `word 123 word`;
- a foreign-script gap between target-script words;
- split orthographic forms such as `l'arte`;
- punctuation-wrapped valid words, which remain intact.

Surviving words are never made adjacent across dropped material.

The correction changes some edge scores materially, for example Arabic suffix
0.959 -> 1.010, while the comparator minimum-side pattern remains.

## Exact adjacent-repeat robustness

In canonical Voynich lines:

- observed exact adjacent repeated-token pairs: **249**;
- exact expectation under within-line shuffle: **244.274**.

As a deliberately harsh sensitivity, every exact adjacent repeat pair was
turned into a sequence break while retaining all tokens. The suffix score falls
from 1.108 to **1.064** but remains above 1.0.

Exact repetition therefore contributes to the suffix effect but does not fully
account for it. This is a robustness diagnostic, not an independent hypothesis
test.

## Relationship to the Version 2 correction

Version 3 continues to confirm the central Version 2 correction: the old pooled
marginal expectation substantially inflated the appearance of affix
self-clustering by mixing order with between-unit composition.

The pre-freeze corrections do not restore the Version 2 claim. They narrow
Version 3 further by removing manufactured comparator seams and by using page
blocks for the Voynich cluster-aware robustness statement.

## Retained independent transition findings

CHEDY->QOK and AIIN->QOK use a separate within-line permutation design that
already preserves line composition while destroying order. They remain separate
from the affix-order estimator and retain their existing limitations.

## Scope

Version 3 does not establish:

- decipherment or translation;
- language identity;
- that Voynich is or is not a natural language;
- uniqueness among natural languages;
- syntax or semantics;
- a cipher, constructed-language, stenographic, hybrid, or other generating
  mechanism;
- generalization beyond the frozen tested corpora, transcription, discovery
  rules, tokenization policy, and sequence-unit definitions.

No cross-system p-value is reported. Replicate indices are not paired across
systems.

## Current claim wording

> Under boundary-safe comparator tokenization and an exact within-unit
> composition-conditioned ordering baseline, Voynich suffix ordering is
> modestly self-clustering (full corpus 1.108; page-block bootstrap median
> 1.110, 95% replicate interval 1.074-1.145), while prefix ordering is near
> neutral under page-level resampling (1.020 [0.978, 1.064]). In the
> 28,447-token sequence-unit deletion-stability analysis, all 14 large
> comparators have minimum-side replicate intervals below 1.0. At the smaller
> 14,380-token all-system target, Arabic and Georgian minimum-side intervals
> cross neutral. The result is a finite-corpus structural contrast, not a
> language classifier or evidence of decipherment.

## Evidence

Committed machine-readable evidence:

- `results/prefix_suffix_v3_validation.json`
- `results/prefix_suffix_v3_validation_audit.md`
- `results/prefix_suffix_v3_validation.sha256`

Corrected validation workflow run: `36624694412`  
Corrected canonical compatibility run: `36624694574`

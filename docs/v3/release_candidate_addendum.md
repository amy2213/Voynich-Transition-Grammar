# Version 3 release-candidate addendum

Status: reviewed release-candidate addendum  
Date: 2026-09-29  
Project: Voynich Transition Grammar

## Purpose

This addendum documents the post-release correction to the Version 2
prefix/suffix cross-corpus analysis and the validated Version 3 replacement
estimator.

The frozen Version 2 release remains unchanged for reproducibility. Its
prefix/suffix claim was reopened because the self-clustering expectation used
source and destination marginals pooled across natural sequence units. That
baseline can confound within-unit order with between-unit compositional
heterogeneity.

Version 3 asks a narrower question: after fixing the affix-class composition of
each line or sentence, does the observed order produce more or fewer
self-transitions than random ordering inside that same unit?

## Corrections relative to Version 2

Version 3 makes four material repairs.

1. **Composition-conditioned null.** Expected self-transitions are computed
   exactly within each natural unit rather than from pooled corpus marginals.
2. **Suffix nesting.** Prefix nesting uses prefix logic and suffix nesting uses
   suffix logic. Nested suffix candidates such as `dy/edy` and `in/iin` are
   not simultaneously selected.
3. **Comparator tokenization.** Alphabetic one-character comparator words are
   retained rather than deleted.
4. **Inference framing.** Independently generated replicate distributions are
   not paired by index and no cross-system sign-test p-value is reported.

For a class appearing `k` times in a natural unit containing `n` tokens,
the exact expected adjacent self-transition count under a uniformly random
within-unit permutation is:

```
k(k - 1) / n
```

The primary side score aggregates observed self-transitions across supported
classes and divides by the corresponding aggregate composition-conditioned
expectation.

## Validation design

Three views are reported.

### Full-corpus descriptive analysis

Each system is scored on its complete available corpus. These estimates are
descriptive because corpus sizes differ.

### Main matched sensitivity

- target: 28,447 tokens;
- target rule: 90% of the canonical Voynich token count;
- systems: Voynich plus 14 sufficiently large comparators;
- Ottoman Turkish excluded because its preserved corpus is smaller than the
  target;
- 200 independent within-system matched subsamples per system.

### All-system small-target sensitivity

- target: 14,380 tokens;
- target rule: 90% of the smallest available corpus;
- systems: all 16 systems, including Ottoman Turkish;
- 200 independent within-system matched subsamples per system.

Natural lines or sentences remain separate. If the final sampled unit must be
truncated to reach the exact target, the retained contiguous fragment remains a
separate unit and creates no seam adjacency.

## Validated results

### Full corpus

Voynich:

- prefix order ratio: 1.013;
- suffix order ratio: 1.108;
- minimum-side ratio: 1.013.

Every tested comparator has a full-corpus minimum-side ratio below 1.0.

### Main matched analysis

Voynich:

- prefix: **1.013 [1.005, 1.025]**;
- suffix: **1.108 [1.099, 1.116]**;
- minimum: **1.013 [1.005, 1.025]**;
- minimum at or above 1.0 in **199/200** replicates.

Across the 14 large comparators:

- 14/14 have minimum-side median below 1.0;
- 14/14 have their entire 95% minimum-side replicate interval below 1.0.

### All-system small-target analysis

Voynich:

- prefix: **1.019 [0.985, 1.060]**;
- suffix: **1.108 [1.081, 1.132]**;
- minimum: **1.019 [0.985, 1.060]**;
- minimum at or above 1.0 in **170/200** replicates.

All 15 comparators have their entire minimum-side 95% replicate interval below
1.0.

The smaller Voynich prefix/minimum interval crosses 1.0. This sample-size
sensitivity limits any claim that Voynich is strictly above neutral on both
sides under every matched target.

## Interpretation

The Version 3 result is not that Voynich has extremely high affix
self-clustering. The corrected prefix effect is close to neutral.

The validated finite-set pattern is instead:

- Voynich is near-neutral for prefix ordering and modestly self-clustering for
  suffix ordering;
- each tested comparator shows order-driven anti-clustering on at least one
  token edge under the declared estimator;
- the separation is strongest in the 28,447-token matched analysis;
- the smaller all-system analysis weakens the claim that Voynich itself is
  strictly above neutral on both edges, although comparator minimum-side
  distributions remain below neutral.

This is a structural corpus contrast. It is not a language classifier.

## Relationship to retained transition findings

The CHEDY->QOK and AIIN->QOK transition findings use a separate within-line
shuffle null. That null already fixes each line's class composition and destroys
only order. The Version 2 affix-estimator defect therefore does not invalidate
their within-line permutation evidence.

The published pooled independence ratios for those cells remain descriptive
effect-size summaries rather than composition-conditioned magnitudes.

## Limits

The validated Version 3 result does not establish:

- decipherment or translation;
- language identity;
- natural-language uniqueness;
- syntax or semantics;
- a specific historical, cipher, constructed, stenographic, or hybrid
  mechanism;
- generalization beyond the frozen comparator set;
- robustness to every transcription alphabet, genre, affix-discovery rule, or
  tokenization scheme.

Most Leipzig comparators are modern Wikipedia proxies rather than
genre-matched historical manuscripts. The finite comparator set is not a
random sample of human languages.

The 95% intervals are replicate intervals under the declared resampling
procedures. They are not population confidence intervals over all possible
languages or manuscripts.

## Reproducibility

Canonical Version 3 code:

- `scripts/24_prefix_suffix_v3.py`
- `scripts/25_v3_validation_audit.py`
- `scripts/_canonical.py`

Specification:

- `docs/v3/prefix_suffix_order_estimator_spec.md`

Interpretation record:

- `docs/v3/validation_interpretation.md`

The exact-final-head 200-replicate validation workflow and mechanical audit completed successfully on run #7 (run ID `36614286293`, head `b8833f6b8714232bae2ceeebffbd6ee070432863`). The uploaded validation artifact contains the JSON result and generated audit report. Artifact ZIP SHA-256:

`1b71a5a24d29452b588eb9de4fd48e05396f091d0968da13f523b775906d6720`

The verified release-candidate evidence ZIP has SHA-256 `b6d496e05a8203bbddd1490f56de8ccacdd2e63d94e2d9763db6d8362a0b9875` and is durably preserved in the ChatGPT Library at `/Voynich Transition Grammar/Voynich-v3-release-candidate-evidence.zip`.

Full final-head provenance is recorded in `docs/v3/release_candidate_manifest.md`.

## Release-candidate conclusion

Version 3 resolves the verified Version 2 estimator defects and produces a
bounded, reproducible structural result. The appropriate claim is the
finite-set ordering contrast described above, not the earlier raw
self-clustering elevation and not a claim of natural-language uniqueness.

The Version 2 tag, paper, DOI record, hashes, and release assets remain frozen.
A future Version 3 release should link directly to the Version 2 post-release
defect record and identify this addendum as the replacement interpretation for
the prefix/suffix cross-corpus analysis.

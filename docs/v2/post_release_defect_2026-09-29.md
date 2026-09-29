# Post-release defect record: Version 2 prefix/suffix estimator

Date opened: 2026-09-29  
Affected frozen release: `v2.0.0`  
Frozen scientific commit: `039acf4873104d7c8b60a3a5ff946667a8e0193c`  
Status: verified defect; Version 2 artifact preserved; replacement analysis in Version 3 development

## Summary

The Version 2 cross-corpus prefix/suffix comparison is reproducible but its
headline self-clustering statistic does not isolate ordering from sequence-unit
composition. Transition counts are correctly restricted to natural units, but
the expected self-transition counts are calculated from source and destination
marginals pooled across all units. If lines or sentences differ in affix
composition, the pooled expectation can make compositionally homogeneous units
look self-clustered even when within-unit order is random.

This triggers the repository's reopen rule because the estimator can measure a
different property from the one attributed to the headline comparison.

## Verified defects

### 1. Pooled marginal expectation confounds composition and order

Version 2 computes, for each discovered class, observed self-transitions divided
by an independence expectation based on pooled source and destination
marginals. Natural boundaries are preserved for observed transition counting,
but the expectation is not conditioned on each unit's class composition.

Consequence: between-line or between-sentence vocabulary heterogeneity can
raise the reported self-clustering score without an order-driven effect.

### 2. Suffix nesting guard uses prefix logic

The Version 2 discovery code uses `startswith` for both prefix and suffix
nesting checks. The suffix side should use `endswith`. In the frozen Voynich
output this permits nested modal candidates including `dy/edy` and
`in/iin`. First-match assignment can then leave the longer nested families
empty.

### 3. Cross-system replicate sign-test framing is not retained

Voynich page-bootstrap replicates and comparator without-replacement subsamples
were generated independently and paired only by replicate index. The resulting
sign calculation is not retained as inferential evidence about the underlying
systems. Version 3 reports no cross-system p-value from arbitrary replicate
pairing.

### 4. Comparator one-character words were discarded

The Version 2 comparator tokenizer required token length >= 2 while canonical
Voynich tokenization retained one-character tokens. Version 3 comparator
tokenization retains alphabetic words of length 1.

## What is not retracted by this defect record

The within-line CHEDY->QOK and AIIN->QOK transition findings use a separate
within-line label-shuffle null that preserves each line's class composition
while destroying order. Their order-dependent permutation evidence is not
invalidated by this prefix/suffix-estimator defect.

Their pooled independence ratios remain descriptive effect-size summaries and
should not be confused with composition-conditioned effect sizes.

## Frozen release policy

The `v2.0.0` tag, GitHub release, paper, hashes, and Zenodo artifact remain
unchanged. Corrections are recorded prospectively on `main` and in later
versions. Historical reproducibility is preserved.

## Replacement design

Version 3 uses the exact expected self-transition count under independent
within-unit permutation. For class c with k occurrences in a natural sequence
unit of length n:

```
E[c -> c | unit composition] = k(k - 1) / n
```

The expectation is summed over units. This conditions the baseline on each
unit's length and composition, directly removing the confound above. Version 3
also fixes side-aware suffix nesting, retains one-character comparator words,
and applies the same without-replacement natural-unit subsampling algorithm to
all systems for matched-size sensitivity analyses.

See `docs/v3/prefix_suffix_order_estimator_spec.md`.

# Voynich Transition Grammar v3.0.0

Version 3.0.0 is the corrected affix-ordering release.

## Corrected result

Voynich page-block robustness, 200 replicates:

- prefix **1.020 [0.978, 1.064]**
- suffix **1.110 [1.074, 1.145]**
- minimum **1.020 [0.978, 1.064]**

Prefix/minimum crosses neutral. Suffix remains above neutral.

In the 28,447-token sequence-unit deletion-stability analysis, all 14 large
comparators have minimum-side 95% replicate intervals below 1.0 after
boundary-safe tokenization. At the smaller 14,380-token all-system target,
Arabic and Georgian minimum-side intervals cross neutral.

Exact adjacent repeats do not fully explain the suffix result: 249 are observed
versus 244.274 expected, and breaking every exact repeat pair leaves suffix
ratio 1.064.

## What changed before freeze

A hostile pre-freeze review correctly identified that regex filtering could
manufacture comparator adjacency and that 90% Voynich line samples overlap too
heavily to support the headline neutrality interval. Both were fixed before the
tag was created.

## Scope

This is a finite-corpus structural result. It does **not** establish
natural-language uniqueness, identify a language, decipher the manuscript,
infer syntax or semantics, or identify a generating mechanism.

## Version 2

The frozen `v2.0.0` tag, paper, DOI record, hashes, and release assets remain
unchanged. Its prefix/suffix claim is superseded by Version 3.

## Archival identifiers

- Zenodo concept DOI: `10.5281/zenodo.19996904`
- Version-specific Version 3 DOI: assigned after archival ingestion

# Voynich Transition Grammar v3.0.0

Version 3.0.0 is the corrected prefix/suffix ordering release.

## What changed

Version 2's prefix/suffix comparison was reopened after a post-release audit
identified a pooled-marginal composition confound, incorrect suffix-nesting
logic, comparator one-character-token asymmetry, and invalid cross-system
replicate-index sign-test framing.

Version 3 replaces that analysis with an exact within-unit
composition-conditioned ordering baseline. For a class occurring `k` times in
a natural unit of length `n`, expected adjacent self-transitions under random
within-unit order are `k(k-1)/n`.

## Validated result

Main matched analysis, 28,447 tokens, 200 replicates:

- Voynich prefix: **1.013 [1.005, 1.025]**
- Voynich suffix: **1.108 [1.099, 1.116]**
- Voynich minimum side: **1.013 [1.005, 1.025]**
- all 14 tested large comparators have their entire minimum-side 95% replicate
  interval below 1.0

All-system sensitivity, 14,380 tokens:

- Voynich minimum side: **1.019 [0.985, 1.060]**
- the interval crosses neutral, and that sample-size sensitivity is part of the
  released interpretation

## Scope

This is a finite-corpus structural result under the declared transcription,
corpora, affix-discovery rules, natural-unit definitions, and estimator.

It does **not** establish natural-language uniqueness, identify a language,
decipher the manuscript, infer syntax or semantics, or identify a cipher,
constructed-language, stenographic, hybrid, or other generating mechanism.

## Version 2

The frozen `v2.0.0` tag, paper, DOI record, hashes, and release assets remain
unchanged as historical evidence. The Version 2 prefix/suffix claim is
superseded by Version 3. The separate within-line CHEDY→QOK and AIIN→QOK
shuffle findings remain retained with their existing limitations.

## Archival identifiers

- Zenodo concept DOI: `10.5281/zenodo.19996904`
- Version-specific Version 3 DOI: assigned after archival ingestion

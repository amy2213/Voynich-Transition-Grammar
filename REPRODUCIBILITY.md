# Reproducibility Guide

This guide covers the current Version 3.0.0 result and the preserved Version 2
canonical pipeline.

## Environment

CI uses Python 3.11 on Ubuntu. Install:

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Version 3.0.0 prefix/suffix ordering analysis

Run the frozen Version 3 estimator with the declared 200-replicate design:

```bash
python scripts/24_prefix_suffix_v3.py \
  --replicates 200 \
  --seed 20260929 \
  --out results/prefix_suffix_v3_validation.json
```

Audit the generated result:

```bash
python scripts/25_v3_validation_audit.py \
  --input results/prefix_suffix_v3_validation.json \
  --out results/prefix_suffix_v3_validation_audit.md
```

The estimator preserves natural line/sentence boundaries, samples natural units
without replacement for matched analyses, uses side-aware affix nesting, keeps
alphabetic one-character comparator words, and scores self-transitions against
the exact within-unit random-order expectation `k(k-1)/n`.

The two declared matched profiles are:

- main: 28,447 tokens, Voynich plus 14 sufficiently large comparators;
- all-system sensitivity: 14,380 tokens, all 16 systems including Ottoman
  Turkish.

Replicate indices are independent across systems and are never treated as
linguistically paired observations.

## Expected Version 3 fingerprint

With the frozen inputs and seed schedule:

- Voynich main prefix median: 1.013 [1.005, 1.025]
- Voynich main suffix median: 1.108 [1.099, 1.116]
- Voynich main minimum median: 1.013 [1.005, 1.025]
- main comparators with entire minimum-side 95% interval below 1.0: 14/14
- Voynich all-system small-target minimum:
  1.019 [0.985, 1.060]

The smaller-target Voynich interval crosses 1.0 and must not be omitted from the
interpretation.

## Frozen Version 2 canonical pipeline

Version 2 remains reproducible historical evidence. Run:

```bash
python run_all.py
```

That command validates frozen inputs, regenerates the Version 2 core and
prefix/suffix outputs, runs pytest and direct Python tests, verifies output
freshness, and writes machine-readable run evidence. The frozen `v2.0.0` tag,
paper, hashes, and DOI record are not modified by Version 3.

## Tests

Run the complete regression suite:

```bash
python -m pytest -q tests/test_canonical_values.py
```

The suite separately checks current Version 3 metadata and the integrity of the
historical frozen Version 2 release bundle.

## Data provenance

Frozen input hashes used by Version 3 are recorded in
`docs/v3/release_candidate_manifest.md` and in each generated Version 3 JSON
result. Comparator sources include Leipzig Wikipedia corpora, Project Gutenberg
Middle/KJV English texts, and the Ottoman Turkish DUDU CoNLL-U treebank.

## Scope

Reproducibility demonstrates that the declared code and frozen data regenerate
the stated finite-corpus results. It does not establish decipherment,
translation, language identity, natural-language uniqueness, semantic content,
or the manuscript's generating mechanism.

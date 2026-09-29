# Reproducibility Guide

This guide covers the corrected Version 3.0.0 result and the preserved Version
2 canonical pipeline.

## Environment

CI uses Python 3.11 on Ubuntu.

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Version 3.0.0 analysis

```bash
python scripts/24_prefix_suffix_v3.py \
  --replicates 200 \
  --seed 20260929 \
  --out results/prefix_suffix_v3_validation.json

python scripts/25_v3_validation_audit.py \
  --input results/prefix_suffix_v3_validation.json \
  --out results/prefix_suffix_v3_validation_audit.md
```

Comparator tokenization is boundary-safe: excluded or split whitespace items
terminate the current sequence. Valid one-character alphabetic words are
retained. Voynich continues to use the cleaned canonical parquet tokenizer.

## Robustness hierarchy

1. Full-corpus ratios are descriptive effect-size estimates.
2. The 90% sequence-unit deletion analysis is a stability diagnostic.
3. The Voynich page-block bootstrap is the cluster-aware robustness statement
   for prefix/minimum neutrality.
4. The 14,380-token all-system analysis is a smaller-sample sensitivity.

Replicate indices are independent across systems and have no cross-system
pairing interpretation.

## Corrected numerical fingerprint

Full-corpus Voynich:

- prefix 1.013
- suffix 1.108

Page-block Voynich, 200 replicates:

- prefix 1.020 [0.978, 1.064]
- suffix 1.110 [1.074, 1.145]
- minimum 1.020 [0.978, 1.064]
- prefix/minimum fraction >=1: 0.770
- suffix fraction >=1: 1.000

Sequence-unit deletion stability, 28,447 tokens:

- comparator minimum-side intervals below 1.0: 14/14
- Voynich line-deletion prefix/minimum: 1.013 [1.005, 1.025], stability only

All-system sensitivity, 14,380 tokens:

- Voynich minimum 1.019 [0.985, 1.060]
- comparator minimum-side medians below 1.0: 15/15
- comparator minimum-side intervals entirely below 1.0: 13/15
- Arabic and Georgian cross neutral

Exact repeats:

- observed 249
- expected 244.274
- suffix after breaking every exact repeat pair: 1.064

## Committed evidence

- `results/prefix_suffix_v3_validation.json`
- `results/prefix_suffix_v3_validation_audit.md`
- `results/prefix_suffix_v3_validation.sha256`

## Frozen Version 2 pipeline

```bash
python run_all.py
```

The frozen `v2.0.0` tag, paper, hashes, and DOI record remain unchanged.

## Scope

Reproduction of the declared code and data does not establish decipherment,
translation, language identity, natural-language uniqueness, semantic content,
syntax, or a generating mechanism.

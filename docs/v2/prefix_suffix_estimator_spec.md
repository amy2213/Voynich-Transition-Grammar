# Version 2 prefix/suffix estimator specification

Status: confirmatory estimator specification, approved for implementation after Phase 1.

Estimator version: `2.0.0`

## Scope

This estimator compares continuous prefix-family and suffix-family self-clustering in Voynich EVA and a declared set of comparator corpora. It does not test decipherment, semantic content, language identity, or natural-language uniqueness.

## Sequence units

- Voynich: Zandbergen-Landini lines from the frozen parquet snapshot. Lines are nested within pages for page-block resampling. Lines are never joined.
- Leipzig corpora: one Leipzig sentence record per sequence unit.
- Gutenberg corpora: one sentence-like segment from one frozen document per sequence unit. Project Gutenberg headers and footers are removed first.
- CoNLL-U corpora: one blank-line-delimited sentence per sequence unit. Surface forms are read from column 2; comments, ranges, and empty nodes are excluded.

All transition counts are computed only inside a sequence unit. Corpus, document, sentence, page, line, resample, and truncated-unit boundaries cannot create adjacency.

## Matched samples and uncertainty

The target size is the exact number of canonical Voynich tokens. Each eligible comparator must contain at least that many tokens. A comparator replicate samples whole natural units without replacement in randomized order until the target is reached. If the final unit would exceed the target, one contiguous fragment supplies the remaining tokens and remains a separate unit.

Voynich uncertainty uses page-block bootstrap replicates. Sampled pages contribute their original separate lines. Sampling continues to the target token count; any final truncated line is a separate contiguous fragment. A page appearing more than once creates distinct resample units and never creates new adjacency.

The same master seed, deterministic child-seed schedule, target size, replicate count, and sampling algorithm apply to every reported run. Comparator and Voynich replicate indices are paired only for computing replicate-wise contrasts; this pairing does not imply matched linguistic content.

## Affix discovery and scoring

Prefix and suffix discovery use the same algorithm for every system and replicate:

- candidate lengths: 2 and 3 code points;
- candidate coverage: 2% through 20% of tokens, inclusive;
- maximum families per side: 5;
- candidate pool: the 80 most frequent candidates;
- greedy selection in descending count order with lexical tie-breaking;
- selected families may not be nested on the same side;
- a token is assigned to the first matching selected family or `OTHER`.

For a class `c`, self-clustering is the observed within-unit `c -> c` count divided by the expected count from pooled within-unit source and destination marginals. The continuous side score is the unweighted mean over supported discovered classes. A class is supported when both source and destination counts exceed 10 and its expected self-transition count exceeds 1.

The primary estimate excludes `OTHER`. A required sensitivity estimate includes `OTHER`. The primary continuous outputs are prefix score, suffix score, their ratio, and their minimum. Threshold buckets are secondary summaries.

## Threshold sensitivity and comparisons

Threshold sensitivity crosses elevation thresholds `1.05`, `1.10`, and `1.15` with ratio lower bounds `0.75`, `0.80`, and `0.85` and ratio upper bounds `1.20`, `1.25`, and `1.30`.

For each eligible comparator, the output reports replicate-wise differences in the continuous minimum score, a percentile interval, the probability that Voynich exceeds the comparator on both side scores, and a two-sided sign test with the corrected empirical estimate `(b + 1) / (B + 1)`. Benjamini-Hochberg correction covers the full declared comparator family. A corrected p-value is never reported as zero.

## Generated evidence

The canonical script generates JSON, CSV, Markdown, and SVG outputs. JSON provenance records every raw input hash, relevant code hashes, git revision, estimator version, configuration, master seed, replicate count, and exact command. No manually maintained JSON overrides these generated files.

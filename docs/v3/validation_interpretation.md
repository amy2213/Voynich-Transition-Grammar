# Version 3 corrected validation interpretation

Status: corrected pre-freeze validation complete; release gate remains closed pending final packaging and exact-head CI  
Validation date: 2026-09-29  
Estimator: `3.0.0` pre-freeze candidate  
Replicates per declared robustness profile: 200  
Authoritative validation run: #22, run ID `36624694412`, methodological head `cdbdc78f9887446b3b602349e22a4cfc30afc0f2`

## Executive result

Version 3.0.0 was re-audited before release after an external review identified
two remaining methodological weaknesses:

1. 90% without-replacement Voynich line samples overlapped too heavily to serve
   as the primary cluster-aware uncertainty summary.
2. Comparator regex tokenization could create false adjacency when excluded or
   split lexical material disappeared between surviving words.

Both issues are corrected in the current pre-freeze estimator.

The corrected result is narrower and more defensible:

- **Voynich prefix ordering is near neutral.** Under a page-block bootstrap,
  prefix ratio median is **1.020**, 95% replicate interval
  **[0.978, 1.064]**. The interval crosses 1.0.
- **Voynich suffix ordering is modestly self-clustering.** Under the same
  page-block bootstrap, suffix ratio median is **1.110**, 95% replicate
  interval **[1.074, 1.145]**. All 200 page-bootstrap replicates are at or
  above 1.0.
- The page-bootstrap minimum-side ratio is **1.020 [0.978, 1.064]**, so the
  project no longer claims that both Voynich edges are strictly above neutral.
- After boundary-safe comparator tokenization, all 14 sufficiently large
  comparators still have a minimum-side 95% interval entirely below 1.0 in the
  declared 28,447-token line/sentence deletion-stability analysis.
- All 15 comparators have a full-corpus minimum-side point estimate below 1.0.

This is a finite-corpus structural contrast under the declared corpora,
transcription, tokenizer rules, affix discovery, sequence boundaries, and
estimator. It is not a population confidence statement or a language
classifier.

## Why the page bootstrap governs Voynich neutrality

The 28,447-token without-replacement Voynich samples retain about 90% of the
available line material. They are useful as a **deletion/stability
sensitivity**: they ask whether the result changes when roughly 10% of the
lines are omitted.

They are not the primary uncertainty summary for Voynich because the
replicates overlap heavily.

Version 3 therefore uses page blocks as the cluster-aware robustness unit.
Pages are sampled with replacement while their nested lines remain separate
sequence units.

Corrected Voynich page-block results:

| Metric | Median | 95% replicate interval | Fraction >= 1 |
|---|---:|---:|---:|
| Prefix | **1.020** | **0.978–1.064** | 0.770 |
| Suffix | **1.110** | **1.074–1.145** | **1.000** |
| Minimum side | **1.020** | **0.978–1.064** | 0.770 |

Accordingly, the earlier `199/200` line-subsample statement is retained only
as a stability diagnostic and is not used as a headline inference.

## Boundary-safe comparator tokenization

Comparator tokenization now operates one whitespace item at a time.

A comparator item may contribute a token only when it contains exactly one
accepted target-alphabet run and any surrounding characters are punctuation.
If an item:

- contains no accepted target-alphabet run;
- contains digits or foreign-script material outside the accepted run; or
- splits into multiple accepted runs, such as `l'arte`;

the item terminates the current sequence.

Therefore surviving neighbors on opposite sides of excluded material never
become adjacent.

Regression tests explicitly cover:

- `word 123 word`;
- a foreign-script gap;
- a split orthographic form;
- valid one-character words; and
- punctuation-wrapped single tokens.

## Corrected full-corpus comparator values

| System | Prefix | Suffix | Minimum |
|---|---:|---:|---:|
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
| **Voynich** | **1.013** | **1.108** | **1.013** |

Arabic demonstrates why the seam correction mattered: its suffix point
estimate rises to approximately neutral, but its prefix remains below 1.0.
The cross-system observation therefore concerns the **minimum edge**, not a
claim that both edges of every comparator are anti-clustered.

## 28,447-token deletion/stability profile

This profile includes Voynich plus 14 sufficiently large comparators. Ottoman
Turkish is excluded because the preserved corpus is too small for this target.

After the boundary correction:

- Voynich line-deletion prefix: **1.013 [1.005, 1.025]**;
- Voynich line-deletion suffix: **1.108 [1.099, 1.116]**;
- Voynich line-deletion minimum: **1.013 [1.005, 1.025]**;
- **14/14** comparator minimum-side 95% replicate intervals remain entirely
  below 1.0.

This profile is evidence of stability to line/sentence deletion. For Voynich,
it is not the cluster-aware uncertainty summary.

Notable corrected comparator minimum-side intervals include:

- Arabic: **0.861 [0.741, 0.997]**;
- Georgian: **0.910 [0.841, 0.976]**;
- Swahili: **0.884 [0.839, 0.943]**.

## 14,380-token all-system sensitivity

At the smaller common target including Ottoman Turkish:

- Voynich minimum: **1.019 [0.985, 1.060]**;
- Voynich suffix: **1.108 [1.081, 1.132]**;
- the Voynich minimum interval crosses neutral;
- several comparator minimum intervals also widen enough to cross neutral,
  including Arabic and Georgian.

This profile is retained as a sample-size sensitivity and prevents the larger
28,447-token profile from being treated as universally scale-invariant.

## Exact repeated-token robustness

The frozen Voynich corpus contains:

- **249** exact adjacent repeated-token pairs;
- expected exact adjacent repeated-token pairs under within-line random order:
  **244.274**.

As a deliberately harsh robustness check, Version 3 breaks the sequence at
every exact adjacent repeated-token pair, removing that adjacency while
retaining the tokens in separate fragments.

Under that check:

- original suffix order ratio: approximately **1.108**;
- suffix order ratio after breaking exact repeats: **1.064**.

Exact repetition therefore contributes to the measured suffix effect but does
not fully account for it.

The earlier external-review figures of 205 observed versus 191 expected are not
used because they were not reproduced on the frozen repository corpus.

## Relationship to Version 2

The corrected Version 3 result reinforces the central Version 2 correction.

Version 2's pooled expectation mixed ordering with between-unit composition and
also contained a suffix-nesting defect and invalid cross-system replicate
pairing. Version 3 conditions on each unit's composition, uses side-aware
nesting, boundary-safe comparator tokenization, and no paired cross-system
p-value.

Version 2 remains frozen and reproducible historical evidence. Its
prefix/suffix cross-corpus interpretation is superseded, not silently rewritten.

## Retained independent transition findings

The separate CHEDY→QOK and AIIN→QOK analyses use within-line shuffling that
fixes line composition while destroying order. The Version 3 affix correction
does not invalidate those separate findings.

Their pooled observed/expected ratios remain descriptive effect-size
summaries; the within-line shuffle design is the relevant order-sensitive
component.

## What Version 3 does not establish

Version 3 does not establish:

- decipherment or translation;
- language identity;
- that Voynich is or is not a natural language;
- uniqueness among natural languages;
- syntax or semantics;
- a cipher, constructed-language, stenographic, hybrid, or other generating
  mechanism;
- generalization beyond the frozen tested corpora, transcription, tokenizer
  rules, discovery rules, and sequence-unit definitions.

No cross-system p-value is reported. Replicate indices are not paired across
systems.

## Validation provenance

Corrected dedicated validation:

- workflow: `Version 3 scientific validation`;
- run: #22;
- run ID: `36624694412`;
- methodological head:
  `cdbdc78f9887446b3b602349e22a4cfc30afc0f2`;
- result: **PASS**;
- artifact: `v3-validation-200-replicates`;
- artifact ID: `11060002732`;
- artifact ZIP SHA-256:
  `132ab897cb68a2d1ffe76c204000436761190939b0a4ea6aaca3d7a766fd1585`.

Corrected canonical/V2 compatibility:

- workflow: `Canonical pipeline and tests`;
- run: #85;
- run ID: `36624694574`;
- result: **PASS**;
- canonical evidence artifact ID: `11060427157`;
- artifact ZIP SHA-256:
  `3febe255027419722a452576ea5b06c80fb4458637d777001d62fa171665f944`.

The generated JSON and audit report are committed under `results/`.

## Recommended release wording

> Under an exact composition-conditioned within-unit ordering baseline, the
> Voynich EVA transcription shows modest suffix self-clustering
> (full-corpus ratio 1.108; page-block bootstrap median 1.110, 95% replicate
> interval 1.074–1.145), while prefix ordering is near neutral
> (page-block median 1.020, interval 0.978–1.064). After boundary-safe
> comparator tokenization, every tested comparator has a full-corpus
> minimum-edge ratio below 1.0, and all 14 sufficiently large comparators have
> minimum-edge 95% intervals below 1.0 in the declared 28,447-token
> deletion-stability analysis. This is a finite-corpus structural contrast,
> not evidence of decipherment, language identity, or natural-language
> uniqueness.

## Release recommendation

The corrected estimator and evidence are suitable to proceed through final
release packaging and exact-head CI. The Version 3 tag should remain uncreated
until those final gates pass.

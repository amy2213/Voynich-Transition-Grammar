# Version 3.1 preregistration protocol

Status: **protocol candidate; no Version 3.1 confirmatory result has been run**  
Prepared: 2026-09-29  
Project: Voynich Transition Grammar  
Planned estimator version: `3.1.0-dev`

## 1. Purpose

Version 3.1 addresses the post-release construct-validity and comparator-
sensitivity defects recorded in:

`docs/v3/post_release_defect_2026-09-29.md`

The primary correction is a position-aware within-unit null that conditions on
line endpoints. The second correction is mandatory affix-discovery sensitivity
reporting.

Version 3.1 will not promote the Version 3.0.0 cross-corpus headline merely by
rerunning the same modern-sentence comparators under a new null.

## 2. Prior knowledge disclosure

This protocol is written **after exploratory post-release diagnostics**. Those
diagnostics are not confirmatory Version 3.1 evidence.

Known exploratory observations include:

- removing the first and last token of each Voynich line changes the
  full-corpus prefix/suffix ratios to approximately 0.933/1.053;
- an exploratory fixed-endpoint full-corpus calculation gives approximately
  0.912/1.048;
- an exploratory 200-replicate fixed-endpoint page bootstrap gives
  approximately 0.919 [0.884, 0.954] prefix and
  1.048 [1.017, 1.086] suffix;
- the Version 3.0.0 Voynich prefix estimate is stable at approximately
  1.013–1.025 across several affix-discovery settings;
- Arabic is not threshold-stable: its weaker edge reaches approximately 1.010
  when discovery coverage is widened to 1%–30%;
- symmetric subtraction of exact-repeat contributions leaves the Voynich
  suffix ratio near 1.110.

These observations motivated the correction. They must not be used to alter
the protocol after the confirmatory run begins.

## 3. Frozen primary Voynich input

Primary transcription:

`data/raw/voynich/AncientLanguages_Voynich_snapshot/train.parquet`

Canonical source:

Zandbergen–Landini EVA rows already used by the project.

The existing frozen SHA-256 and canonical tokenization rules remain unchanged.

Primary natural sequence unit:

**physical manuscript line**

Primary resampling cluster:

**page**

No transition may cross a line, removed-token location, page-block copy,
sampling fragment, or other declared sequence boundary.

## 4. Primary Version 3.1 null

### 4.1 Fixed-endpoint position-aware null

For every natural sequence unit, the first and last token classes remain fixed.
Only the interior token classes are treated as exchangeable.

For a class `c` in a line of length `n >= 3`:

- let `m = n - 2` be the number of interior positions;
- let `k_c` be the number of interior occurrences of class `c`;
- let `I_first(c)` equal 1 when the first class is `c`, otherwise 0;
- let `I_last(c)` equal 1 when the last class is `c`, otherwise 0.

The exact expected number of adjacent `c -> c` transitions is:

```
k_c (k_c - 1) / m
+ I_first(c) * k_c / m
+ I_last(c)  * k_c / m
```

The first term is the expected number of interior-to-interior self-
transitions. The second and third terms are the expected first-to-interior and
interior-to-last self-transitions.

For `n = 2`, the sole transition is fully conditioned/fixed and its expected
self-transition count equals its observed self-transition indicator.

For `n = 1`, there is no transition.

The expected counts are summed over sequence units before the aggregate
observed/expected ratio is computed.

### 4.2 Primary score

For each side separately:

1. discover affix families under the declared primary discovery rule;
2. assign every token to the first matching affix family or `OTHER`;
3. exclude `OTHER` from the primary score;
4. include a class only when:
   - observed source count > 10;
   - observed destination count > 10;
   - fixed-endpoint expected self-transition count > 1;
5. sum observed same-class transitions over included classes;
6. sum fixed-endpoint expected same-class transitions over the same classes;
7. report aggregate observed / aggregate expected.

No pooled cross-line marginal expectation is used.

## 5. Primary affix-discovery rule

The primary rule is retained from Version 3.0.0 so that the null correction is
not confounded with a new preferred partition:

- family count: 5;
- minimum affix length: 2;
- maximum affix length: 3;
- minimum coverage: 2%;
- maximum coverage: 20%;
- candidate pool: 80;
- side-aware same-side nesting exclusion;
- lexical tie-breaking;
- minimum class support: 10;
- `OTHER` excluded from the primary score.

## 6. Mandatory discovery sensitivity grid

Every Version 3.1 result must report the primary setting plus the following six
pre-specified perturbations.

| ID | Families | Lengths | Coverage |
|---|---:|---|---|
| primary | 5 | 2–3 | 2%–20% |
| families-3 | 3 | 2–3 | 2%–20% |
| families-8 | 8 | 2–3 | 2%–20% |
| length-2-4 | 5 | 2–4 | 2%–20% |
| coverage-1-30 | 5 | 2–3 | 1%–30% |
| sparse-wide | 3 | 2–4 | 1%–30% |
| dense-wide | 8 | 2–4 | 1%–30% |

No setting may be dropped because it weakens separation.

For every system and setting, report:

- discovered prefix and suffix families;
- supported class counts;
- prefix ratio;
- suffix ratio;
- weaker-edge/minimum ratio.

For Voynich, report the range over all seven settings.

## 7. Primary Voynich robustness analysis

### 7.1 Full-corpus estimate

Report fixed-endpoint prefix and suffix ratios on all canonical Voynich lines.

### 7.2 Page-block bootstrap

Use 200 deterministic page-block bootstrap replicates.

Each sampled page contributes its original separate lines. A final partial
line, if required to hit the target token count, remains a separate contiguous
fragment.

Target:

90% of the canonical Voynich token count, matching the Version 3.0.0
page-bootstrap scale.

Seed schedule:

derive deterministic independent seeds from SHA-256 of the literal string

`Voynich-Transition-Grammar:v3.1.0:confirmatory`

plus the profile name and replicate index.

This removes discretionary seed selection.

Report medians, 2.5th/97.5th percentile replicate intervals, and within-profile
fractions below/at-or-above 1.0.

These are declared robustness distributions, not population confidence
intervals.

## 8. Primary Version 3.1 hypothesis

The primary confirmatory target is the **suffix side**.

### H1

Under the primary fixed-endpoint position-aware null, Voynich suffix
self-clustering remains above neutral.

The primary robustness criterion is satisfied only when:

1. full-corpus primary suffix ratio > 1.0; and
2. the lower 2.5th percentile of the 200-replicate page-bootstrap suffix
   distribution is > 1.0.

Because exploratory diagnostics already showed this direction, Version 3.1
must describe this as a **post-diagnostic confirmatory replication**, not a
blind preregistered discovery.

### Prefix

Prefix is a secondary descriptive outcome.

No Version 3.1 headline may describe prefix as neutral, elevated, or
anti-clustered without reporting the fixed-endpoint page-bootstrap interval.

## 9. Required line-edge sensitivity

Independently remove the first and last token from every line with at least
three tokens.

Report:

- full-corpus interior-only prefix and suffix ratios;
- 200-replicate page-bootstrap interior-only distributions.

This is a sensitivity analysis, not the primary estimator.

## 10. Exact-repeat sensitivity

Two repeat diagnostics are required and must not be conflated.

### 10.1 Symmetric subtraction

For every included affix class:

- subtract exact repeated-token self-transitions from observed same-class
  transitions;
- subtract the exact expected contribution of those repeated token identities
  from the null expectation;
- recompute the aggregate ratio.

This is the direct repeat-removal sensitivity.

### 10.2 Break-at-repeat stress test

Retain the Version 3.0.0 procedure that inserts a sequence boundary at every
exact repeated-token adjacency.

Label this explicitly as a **deliberately lopsided worst-case structural stress
test**, because it changes sequence structure and does not symmetrically remove
the corresponding null expectation.

The two numbers must be reported together.

## 11. Modern sentence comparators

The existing Leipzig/Gutenberg/CoNLL-U systems remain useful implementation and
scale sensitivities.

They are **secondary controls only** in Version 3.1.

For each modern/historical sentence comparator:

- use boundary-safe tokenization;
- apply the same fixed-endpoint null;
- report the complete seven-setting discovery grid;
- do not describe a comparator as intrinsically "below neutral" without
  stating the discovery setting;
- do not use the modern-sentence comparator set to make a general
  natural-language or manuscript-line claim.

No universal "every comparator is below neutral" headline is permitted unless
the statement is true under every pre-specified discovery setting being cited.

## 12. Manuscript-line comparator program

A stronger cross-corpus validation uses physical manuscript lines rather than
modern sentences.

### 12.1 Inclusion rules fixed before scoring

A candidate corpus may enter the manuscript-line validation set only when:

1. the source is an actual manuscript transcription, not a normalized modern
   edition;
2. physical line breaks are encoded or recoverable;
3. original spelling/word division is preserved sufficiently for deterministic
   tokenization;
4. editorial expansions, supplied text, deletions, and uncertain material are
   explicitly marked so a deterministic inclusion policy can be declared;
5. the corpus license permits reproducible research use;
6. inclusion is decided from metadata and transcription structure **before**
   any affix-order score is inspected.

### 12.2 Priority genres and dates

Prioritize:

- late-medieval technical prose;
- medical and recipe manuscripts;
- herbals/pharmacological material;
- astronomical/scientific prose or tables where lineation is recoverable;
- medieval Latin, Italian/vernacular Romance, and Germanic witnesses where
  suitable diplomatic data exist.

The comparison target is physical-line behavior, not superficial similarity to
Voynich content.

### 12.3 Candidate source identified before confirmatory scoring

CoReMA (Cooking Recipes of the Middle Ages) is a priority candidate because its
project documentation states that hyperdiplomatic TEI-XML is downloadable and
that physical page and line breaks are represented.

Candidate discovery does not authorize inclusion until the rules above are
checked and recorded in a comparator manifest.

## 13. Generating-mechanism control program

Mechanism controls are a separate explanatory test, not evidence of language
identity.

Priority executable mechanisms:

1. Timm & Schinner self-citation generator;
2. Rugg/Cardan-grille style generation;
3. a Stolfi-style probabilistic slot/word grammar;
4. a verbose cipher of Latin and/or Italian, with the exact implementation
   frozen before scoring.

Each mechanism must generate enough text for stable estimation and must enter
the same Version 3.1 pipeline.

For each mechanism report at minimum:

- fixed-endpoint prefix and suffix ratios;
- line-edge effect;
- discovery-grid sensitivity;
- CHEDY→QOK-like attraction and AIIN→QOK-like suppression when the generator
  uses compatible EVA-like output classes.

Synthetic line segmentation must be pre-specified. If the mechanism does not
generate physical lineation itself, line lengths must be sampled independently
from a frozen declared line-length distribution rather than tuned to reproduce
the target statistics.

No mechanism is selected or discarded after inspecting its score.

## 14. Internal heterogeneity

Secondary within-Voynich analyses will report the fixed-endpoint suffix effect
by:

- Currier A/B;
- manuscript section;
- scribal hand where metadata support is sufficient.

These analyses are descriptive robustness checks unless a separate hypothesis
family and multiplicity plan is registered before execution.

## 15. Cross-transcription replication

A non-EVA or independently tokenized transcription is a high-priority
robustness target.

Before analysis:

- identify the exact transcription source/version;
- document its token and line-boundary conventions;
- freeze its hash;
- specify any mapping or family-discovery change without consulting the
  resulting affix score.

Synthetic EVA recodings do not count as independent paleographic replication.

## 16. Claim rules

Version 3.1 may lead with the suffix result only if the primary H1 robustness
criterion passes.

A cross-corpus headline requires a separate successful manuscript-line control
analysis. Modern sentence comparators alone cannot support it.

A mechanism-discrimination statement requires the mechanism-control program and
must identify the exact mechanisms tested.

No result establishes:

- decipherment or translation;
- language identity;
- natural-language uniqueness;
- syntax or semantics;
- a particular generating mechanism merely because alternatives score
  differently.

## 17. Amendment rule

After this protocol is committed:

- any methodological change must be recorded in a dated
  `docs/v3_1/amendments/` file;
- the amendment must state whether it was made before or after seeing the
  affected result;
- confirmatory outputs generated before an unplanned methodological change
  remain archived and are not silently overwritten;
- no threshold may be changed solely because a comparator weakens the desired
  contrast.

## 18. Outside design review gate

Before Version 3.1 freezes:

1. publish the protocol/design, not only the conclusions, for outside review;
2. record substantive external objections and responses;
3. rerun only when an amendment is methodologically justified and logged;
4. keep the frozen Version 3.0.0 tag and post-release defect record intact.

## 19. Release gate

Version 3.1 cannot be tagged until all of the following are true:

- fixed-endpoint estimator unit tests pass;
- brute-force toy permutations verify the exact expectation;
- interior-only sensitivity is complete;
- symmetric repeat sensitivity is complete;
- all seven discovery settings are complete;
- 200-replicate page bootstrap is complete;
- manuscript-line comparator eligibility is either completed or the release
  explicitly makes **no cross-corpus manuscript claim**;
- external design review is recorded;
- full canonical compatibility passes;
- generated JSON/audit evidence is committed with hashes;
- public authority text matches the bounded result.

No Version 3.1 tag is authorized by this protocol document.

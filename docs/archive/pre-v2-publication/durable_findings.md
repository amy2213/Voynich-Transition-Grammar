# Durable Findings

Status as of May 2026. All claims tested against controls, conditioning, section splits, Currier types, frequency matching, and shuffled null models. This document records what survived, what was narrowed, and what was retired. The canonical source for all wording is the revised preprint (`docs/paper.pdf`).

Dataset: Zandbergen–Landini EVA transliteration, 31,608 tokens, 184 pages, 4,197 lines. Comparison set: 16 natural-language comparators (13 Leipzig Wikipedia 100K including Swahili, Georgian, Tagalog, and Mandarin Chinese; 2 Gutenberg literary; 1 Ottoman Turkish UD treebank), 1 shuffled-token control.

---

## Section 1: Retained Findings

Each finding records: **Observation** (what was measured), **Interpretation** (what it means), **Status** (retained / narrowed / retired), and **Caveats**.

### 1.1 Two distributed class-level transition effects

**Observation:** CHEDY→QOK attraction at 2.625x (obs=626, exp=238.5, p<0.001). AIIN→QOK repulsion at 0.504x (obs=160, exp=317.4, p<0.001). Split-half ranges: CHEDY→QOK [2.34, 2.67], AIIN→QOK [0.39, 0.53]. The effects operate at the family level: shuffling tokens within families preserves both effects perfectly (Δ=0.00). 369 unique CHEDY→QOK token pairs; top five pairs cover only 13.3% of total.

CHEDY→QOK is specific: after CHEDY, QOK=2.62x, OK=0.83x, OT=0.80x, AIIN=1.08x, OTHER=0.82x. The dependency extends beyond adjacency (+1: 2.62x, +2: 1.23x, +3: 1.32x, +4: 1.16x, +5: 1.02x), reaching 3–4 tokens before decaying to baseline.

**Per-scribe decomposition** (`scripts/08_per_scribe_analysis.py`, `results/per_scribe_results.json`):

| Hand | n_tokens | CHEDY→QOK ratio | CHEDY→QOK obs |
|---|---|---|---|
| 1 | 8,997 | 1.42x | 13 |
| 2 | 9,154 | 2.15x | 374 |
| 3 | 11,389 | 2.28x | 222 |
| 4 | 683 | 7.34x | 2 |
| 5 | 890 | 1.06x | 6 |

Nearly all observations (596 of 617) come from Hands 2 and 3. Hand 1 shows at most a weak effect on low n; Hands 4 and 5 are too small to interpret.

**Interpretation:** Class-level collocational structure, not fixed-phrase repetition. A property of Hands 2 and 3, not a uniform manuscript-wide rule. The aggregate 2.625x is the correct pooled statistic.

**Status:** Retained, narrowed to Hands 2 and 3. The earlier "holds across both scribal hands" framing is retired.

### 1.2 AIIN invariance

**Observation:** Page means: Currier A=15.0%, Currier B=15.0%. KS p=0.742. Bootstrap CI for A–B difference: [−1.95%, +2.02%]. AIIN is the only family with this property (all others differ significantly, p<0.005). AIIN does not self-cluster (SC≈0.98x). It passes OK (2.73x), OT (2.21x), and CHEDY (1.64x) through but blocks QOK (0.83x). AIIN is elevated at line-initial position (+3.2% residual after controls).

**Interpretation:** Consistent with a function-word-like structural role, but not confirmed. AIIN has 842 unique types — more than any other family — and higher positional entropy than CHEDY at every line position. These properties are the opposite of typical natural-language function-word behavior. The function-word reading is a statistical analogy, not a linguistic identification.

**Status:** Retained. Definition-sensitive (fails under strict p=0.004 and loose p=0.001 alternatives). Report only the standard-definition result as robust.

### 1.3 Bidirectional self-clustering symmetry

**Observation:** Prefix SC=1.524x, suffix SC=1.544x, ratio=0.99. Bootstrap 95% CI: prefix [1.41, 1.62], suffix [1.48, 1.60]. Unique among all 18 tested systems (16 NL + 1 shuffled + Voynich). All natural languages with elevated clustering are suffix-dominant (ratios 0.29–0.81). Four specifically selected bidirectional-morphology languages (Swahili, Ottoman Turkish, Georgian, Tagalog) all test SYMM-LOW. Mandarin (isolating) tests SYMM-LOW, confirming the SYMM-LOW floor.

**Alternative-path elimination (medieval abbreviation):** Applying standard 15th-century scribal abbreviations — prefix contractions com→c̃, pre→p̃, per→p̄ and suffix contractions -bus→;, -rum→ꝝ, -tur→t̄ — to expanded Latin text does not move it toward SYMM-HIGH. Even at 90%/95% abbreviation rates, Latin remains strongly SUFFIX-DOM (ratio 0.29). Abbreviation is not a viable path to the Voynich profile.

**Per-scribe decomposition** confirms SYMM-HIGH in each of the three dominant hands independently:

| Hand | n_tokens | Prefix SC | Suffix SC | Ratio | Bucket |
|---|---|---|---|---|---|
| 1 | 8,997 | 1.59x | 1.39x | 1.14 | SYMM-HIGH |
| 2 | 9,154 | 1.15x | 1.24x | 0.93 | SYMM-HIGH |
| 3 | 11,389 | 1.31x | 1.32x | 0.99 | SYMM-HIGH |
| 4 | 683 | — | — | — | Too small |
| 5 | 890 | — | — | — | Too small |

Hands 4 and 5 are too small (<1000 tokens each) to classify reliably.

**Cross-transcription stability:** SYMM-HIGH holds across all four alternative EVA-alphabet transcriptions (Currier PS ratio 0.85, FSG 0.84, Takahashi 0.86, Grove 0.99). The symmetry is not an artifact of Zandbergen–Landini tokenization. Validation under non-EVA character-boundary systems remains an open question.

**Root extraction:** Stripping EVA prefix/suffix wrappers compresses 7,255 token types to 3,193 root types (44% of original vocabulary). Root distribution is moderately Zipfian (R²=0.894, comparable to token-level R²=0.901). Currier A/B root vocabulary overlap increases slightly vs token-level (Jaccard 16% vs 14%), with weak but significant rank correlation (ρ=0.367). AIIN roots collapse to the AIIN morpheme itself (aii, ii, ai), confirming function-word-like structure. Results are consistent with affixal structure but not strong enough to confirm natural-language lexicon underneath. See `results/root_extraction_results.json`.

**Interpretation:** The SYMM-HIGH profile is a property of each of the three major scribes individually and is stable across four independent EVA-alphabet transcribers. It is not an aggregation artifact. No tested natural language, including four with textbook bidirectional morphology, reproduces it.

**Status:** Retained. Strongest surviving finding.

**Caveats:** Self-clustering absolute values are method-sensitive (range 0.93x to 1.45x depending on computation). The bidirectional ratio (0.99) is stable across all methods. Non-EVA alphabet validation remains untested.

### 1.4 Line-bounded transition reset

**Observation:** CHEDY→QOK within-line: 2.54x. Cross-line: 0.85x. AIIN→QOK within-line: 0.40x. Cross-line: 1.22x. Both effects reverse at line boundaries. The reset is universal across line lengths, sections, and Currier types and is not specific to paragraph boundaries. Self-clustering persists across line breaks (OK 2.24x, OT 3.03x, CHEDY 1.50x) — family neighborhoods span lines; transition effects do not. Whole-line family templates recur at only 1.04x above shuffled control (1.20x for coverage).

**Interpretation:** Consistent with lines functioning as clause-like or phrase-like units. Not proof of clausehood or syntax. The transition effects describe departures from independence in the class transition matrix — "class-level collocational structure" rather than predictive syntax. Family-bigram prediction gives 0.0% lift over baseline majority class; even 5-token family history gives only +3.6%.

**Status:** Retained.

### 1.5 Suffix agreement above chance

**Observation:** Suffix agreement ratios (observed same-ending / expected under independence):

| Family pair | Suffix agreement | z | n pairs |
|---|---|---|---|
| OK→OT | 1.75x | 3.3 | 76 |
| OK→OK | 1.67x | 2.8 | 110 |
| OT→OT | 1.49x | 1.9 | 105 |
| QOK→QOK | 1.41x | 5.2 | 301 |
| CHEDY→QOK | 1.18x | 3.5 | 469 |

Four of five pairs significant at z≥2.8. OT→OT at z=1.9 is below the conventional 1.96 threshold and is not claimed as significant.

CHEDY selects specific QOK subtypes (χ²=36.4, p=7.2×10⁻⁵). Multi-feature agreement (suffix + length + mantle + circles) compounds to 5–9x. Length agreement conditioned on suffix + frequency collapses to 1.00x — suffix is the primary feature.

**Interpretation:** Suffix-led agreement, possibly analogous to morphological concord.

**Status:** Retained. OT→OT borderline — do not cite it as significant without noting z=1.9.

### 1.6 Agreement cascades through three-token chains

**Observation:** (`scripts/07_cascade_uncertainty.py`, `results/cascade_uncertainty_results.json`)

| Chain | p(B→C ǀ ≡) | p(B→C ǀ ≠) | n_agree | n_disagree | Cascade (pp) | Conservative 95% CI |
|---|---|---|---|---|---|---|
| CHEDY→OTHER→CHEDY | 0.85 | 0.04 | 13 | 119 | +81 | [+48, +94] |
| CHEDY→QOK→CHEDY | 0.69 | 0.13 | 26 | 45 | +56 | [+24, +77] |
| QOK→OTHER→QOK | 0.62 | 0.18 | 26 | 61 | +44 | [+13, +67] |
| QOK→QOK→QOK | 0.52 | 0.19 | 27 | 16 | +33 | [−9, +63] |
| OT→OTHER→OT | 0.33 | 0.14 | 18 | 37 | +19 | [−12, +50] |

All five chains survive Benjamini–Hochberg FDR at α=0.05. The flagship CHEDY→OTHER→CHEDY cascade rests on n=13 agreement trials. Two chains (QOK→QOK→QOK, OT→OTHER→OT) have conservative composite CIs that touch zero; cite point estimates only with intervals.

Suffix agreement also jumps over OTHER tokens: QOK→[OTHER]→QOK at 2.32x (n=87), CHEDY→[OTHER]→CHEDY at 1.43x (n=132), OT→[OTHER]→OT at 1.87x (n=55).

**Interpretation:** Agreement cascades exist. Large but thinly sampled on the flagship chain. Do not cite +81pp as a precise point estimate.

**Status:** Retained.

### 1.7 Edit-distance graph structure

**Observation:** Hub-centered edit-distance-1 graphs. Top hubs: chedy→12 edit-1 neighbors, daiin→10, qokeedy→7. All 50 tested types per family connected. Four positionally-locked edit operations recur across all sections: insertion/deletion of 'e' (92% mid), 'd' (74% end), c↔s substitution (62% mid), 'l' (89% start).

**Interpretation:** The graph structure and the positional locking of edit operations are retained as descriptive observations. See §3.1 below for the retraction of the productive-morphology interpretation.

**Status:** Observation retained; morphological interpretation retired.

### 1.8 CHEDY avoids line-final position

**Observation:** Residual after full control: −2.7%. Present in both Currier types (A: −1.6%, B: −5.0%).

**Interpretation:** Consistent with CHEDY requiring a following token (from the CHEDY→QOK collocational pattern) that cannot appear after the line boundary. This is a description of the positional pattern, not proof of syntactic complementation.

**Status:** Retained.

### 1.9 Glyph-layer architecture

**Observation:** Clustering lives independently in crust-only (1.86x/2.01x) and mantle+core-only (1.88x/2.00x). Full tokens (1.29x/1.54x) diluted by cross-layer interference. Sequential transition structure lives primarily in circles (o, a, y) and core (gallows). Scrambling circles drops CHEDY→QOK from 2.50x to 1.75x. Family identity best predicted by crust characters (79.4% accuracy).

**Interpretation:** Different glyph zones carry structurally different information: crust carries identity, circles and core carry sequential structure, transition effects depend on word-final characters.

**Status:** Retained.

---

## Section 2: Narrowed Findings

### 2.1 AIIN as function word

**Narrowed.** Behavior consistent with a function-word role (invariant frequency, non-self-clustering, line-initial preference, selective carry-through), but AIIN has 842 unique types and higher positional entropy than CHEDY. Function words in natural language typically have low entropy and few variant forms. The function-word interpretation is a statistical analogy, not confirmed.

### 2.2 Self-clustering magnitude

**Narrowed.** Range 0.93x (page-level) to 1.45x (pooled backbone). The absolute value is method-sensitive. The bidirectional ratio (0.99) is stable. Report as a range, not a fixed number.

### 2.3 Formulaic genre identification

**Narrowed.** Section-specific vocabulary with shared class-level structure, open lexicon (71.4% hapax), productive slots (mean 6.6 unique fillers per frame) — all consistent with a formulaic domain text. But genre identification is inference from structural analogy. No medieval herbal, recipe, or formulary has been tested with the same pipeline.

### 2.4 Family-level collocational structure as "syntax"

**Narrowed.** The transition effects (CHEDY→QOK, AIIN→QOK repulsion) are statistically robust but have near-zero predictive power for next-token family (0.0% lift from family bigrams; +3.6% from 5-token history). Better described as "class-level collocational structure" or "departures from independence in the transition matrix" than as syntax. Token-level bigrams give 99% prediction, but this reflects repetitive token sequences and does not map to family-level prediction.

---

## Section 3: Retired Findings

### 3.1 Productive morphological paradigms (Finding 1.7 interpretation)

**Retired.** The log-frequency vs. edit-1 variant-count correlation (r=0.42–0.71) was interpreted as evidence of productive morphology. A character-trigram null model (`scripts/06_paradigm_null.py`, `results/paradigm_null_results.json`) shows Voynich's correlation is indistinguishable from a synthetic corpus containing no morphology:

| Family | Voynich real r | Null mean r | Null p95 | Exceeds null p95? |
|---|---|---|---|---|
| QOK | 0.60 | 0.48 | 0.61 | No |
| CHEDY | 0.38 | 0.36 | 0.42 | No |
| AIIN | 0.40 | 0.43 | 0.51 | No (below null mean) |

Chaucer at the same measurement produces r=0.20, below both Voynich and its null. The measurement is not a reliable morphological diagnostic. The productive-morphology interpretation is retracted. The graph structure observation is retained (§1.7).

**Consequences:** "Productive morphology" / "productive paradigms" language removed from all documents. Item 5 of the prior 8-item MVE checklist removed; checklist is now 7 items.

### 3.2 Arabic is the closest structural match

**Retired.** Arabic is SUFFIX-DOM (prefix 1.92x, suffix 2.66x, ratio 0.72). Voynich is SYMM-HIGH (ratio 0.99). Artifact of prefix-only measurement.

### 3.3 Uralic languages match Voynich

**Retired.** Estonian SC=1.35x and Finnish SC=1.16x were false positives from 10K-sentence corpora. At 100K sentences both are SUFFIX-DOM.

### 3.4 Self-clustering = 1.44x as a fixed value

**Retired.** Range 0.93x–1.45x depending on method. Report as a range.

### 3.5 CHEDY→QOK = 2.50x

**Corrected** to 2.625x from the frozen dataset. The 2.50x figure reflects token-parsing variation.

### 3.6 Entry-level template structure

**Retired** as a strong claim. Phase shifts are 0.8–2.3% — present but modest.

### 3.7 "Only compatible class" / "only hypothesis without unprecedented mechanisms"

**Retired.** A first-pass synthetic constructed system (`scripts/09_constructed_control.py`, `results/constructed_control_results.json`) satisfies 5 of 7 MVE checklist items by direct design. Items 1–4 and 6 are cheaply engineered. The earlier framing was not empirically grounded. See §4 below.

### 3.8 Suffix agreement "all significant z=3.4–5.0"

**Corrected.** OT→OT is z=1.9, below conventional significance threshold. Four of five pairs are significant at z≥2.8. The blanket "all significant" claim was wrong.

### 3.9 "CHEDY→QOK holds across both scribal hands"

**Retired.** Per-scribe decomposition shows the rule is concentrated in Hands 2 and 3 (§1.1). Hand 1 shows at most a weak effect on n=13.

---

## Section 4: Constructed-Control Consequences

A first-pass synthetic constructed corpus (`scripts/09_constructed_control.py`) was built with rules designed to satisfy each checklist item: Zipfian lexicon, four classes, class-specific attraction, suffix agreement, cascades, line-bounded reset, section-stable structure, and variant generation.

**Result:** 5 of 7 items satisfied. Items not satisfied: bidirectional SYMM-HIGH under auto-detected affixes (item 5) and open vocabulary at ~71% hapax (item 7).

**Interpretation:** Items 1–4 and 6 are cheaply engineered. The items that meaningfully discriminate encoded NL from a constructed system are items 5 and 7. A tuned generator targeting items 5 and 7 specifically has not been attempted. Until it is tested and shown to fail, the constructed-system hypothesis cannot be excluded.

**Revised conclusion:** Among the limited candidate classes implemented in the current pipeline, encoded structured language is the only tested class that satisfies all seven checklist items. Random generation, simple substitution ciphers, and the first-pass constructed control do not. This should be read as a constraint on tested models, not as exclusion of constructed, hybrid, stenographic, or unmodeled historical mechanisms; sophisticated constructed systems that explicitly engineer items 5 and 7 have not been tested. Current data do not discriminate among several structured generating mechanisms, including encoding-based and constructed-system possibilities.

---

## Section 5: Remaining Open Tests

1. **Non-EVA character-boundary validation.** Cross-transcription stability confirmed across four alternative EVA-alphabet transcriptions. Validation under non-EVA character-boundary systems (original Currier alphabet, original FSG alphabet, systems treating ch/sh as single glyphs) has not been performed. Most consequential untested objection.

2. **Tuned constructed-system control.** First-pass satisfied 5/7. A generator targeting items 5 and 7 simultaneously is the highest-priority adversarial test.

3. **Genre-matched medieval comparison.** No medieval herbal, recipe, or formulary tested. Historical Latin medical texts (Trotula, Circa instans, Macer Floridus) and Anglo-Saxon medical texts (Bald's Leechbook) are candidates.

4. **Additional language types.** Polysynthetic languages at corpus scale (Inuktitut, Greenlandic) and historical shorthand systems (Tironian notae) remain untested.

5. **Multiple-comparisons correction.** BH-FDR applied to 5 cascade chains. Cell-level p-values in the 6×6 transition matrix (36 cells) and family-pair suffix-agreement tests (~10 pairs) are not corrected. These are exploratory, not confirmatory.

---

## Methodological Caveats

1. All family definitions are EVA-specific. Cross-transcription validation performed across four alternative EVA-alphabet transcriptions. Non-EVA validation remains open.

2. All comparison languages are modern proxies except Middle English and Ottoman Turkish. No medieval genre-matched text tested.

3. Self-clustering values are method-sensitive. The bidirectional ratio (0.99) is stable; absolute values are not.

4. Numbers shift ~10–15% between runs due to token-parsing variation. All canonical values from frozen local datasets.

5. No decipherment is claimed or attempted.

6. The default pipeline (`run_all.py`) reproduces the core, cross-linguistic, stress, extended, paradigm-null, cascade-uncertainty, per-scribe, and constructed-control results (`scripts/01`–`scripts/04`, `scripts/06`–`scripts/09`). The cross-transcription analysis (`scripts/05_cross_transcription.py`) is run separately because it consumes the LSI interlinear file `LSI_ivtff_0d.txt` (sourced separately from the Hugging Face dataset used by the default pipeline); the LSI file is bundled at `data/raw/voynich/LSI_ivtff_0d.txt` and the precomputed output is committed at `results/cross_transcription_results.json`. 33 regression tests verify canonical values on every commit.

---

## Appendix: Minimum Viable Explanation Checklist (7 items)

Previously 8 items. Item 5 of the prior version ("Productive morphological paradigms") retired by the trigram-null test (§3.1). The "Constructed" column reflects empirical pass/fail from `scripts/09_constructed_control.py`, not assumption.

### 1. Line-bounded transition reset
Within-line CHEDY→QOK: 2.54x. Cross-line: 0.85x. Transition rates reverse at line boundaries.

### 2. CHEDY→QOK class specificity (in Hands 2 and 3)
CHEDY→QOK 2.15x–2.28x in Hands 2 and 3, while CHEDY→OK, CHEDY→OT, CHEDY→AIIN all ≤1.0x.

### 3. Suffix agreement above chance
Four family pairs at z≥2.8. OT→OT borderline at z=1.9. Multi-feature agreement 5–9x.

### 4. Agreement cascades through three-token chains
Five chains survive BH-FDR at α=0.05. Flagship +81pp at n=13 with conservative CI [+48, +94]pp.

### 5. Bidirectional self-clustering symmetry
Prefix SC 1.52x, suffix SC 1.54x, ratio 0.99. None of 16 tested NLs reproduces this. Holds independently in Hands 1, 2, and 3 and across four alternative EVA-alphabet transcriptions.

### 6. Section-stable coarse structure with shifting lexicon
Per-family rates and suffix-agreement patterns coherent across sections. Within-family Jaccard overlap 0.09–0.25.

### 7. Open vocabulary with natural-like distribution
71.4% hapax. Type/token ratio 0.23. Top-100 bigrams cover 3.7% of text.

### Checklist scoring

| # | Requirement | Encoded NL (theoretical) | Constructed (tested) | Simple cipher | Table/grille |
|---|---|---|---|---|---|
| 1 | Line-bounded transition reset | Y | **Y** (designed) | N | N |
| 2 | Class specificity | Y | **Y** (designed) | N | N |
| 3 | Suffix agreement | Y | **Y** (designed) | Destroys | N |
| 4 | Agreement cascades | Y | **Y** (designed) | N | N |
| 5 | Bidirectional SYMM-HIGH | Needs bidirectional encoding | **N** (not achieved) | Cannot produce | Cannot produce |
| 6 | Stable structure, shifting lexicon | Y | **Y** (designed) | If syllabic | Partial |
| 7 | Open vocabulary | Y | **N** (not achieved) | Partial | N |

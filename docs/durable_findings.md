# Durable Findings

Status as of April 2026. All claims tested against controls, conditioning, section splits, Currier types, frequency matching, and shuffled null models. This document records what survived, what weakened, and what was retired.

Dataset: Zandbergen-Landini EVA transliteration, 31,608 tokens, 184 pages, 4,197 lines. Comparison set: 16 natural-language comparators (13 Leipzig Wikipedia 100K including Swahili, Georgian, Tagalog, and Mandarin Chinese; 2 Gutenberg literary; 1 Ottoman Turkish UD treebank), 1 shuffled-token control.

---

## Section 1: Claims That Survived All Controls

### 1.1 Two distributed transition rules

CHEDY→QOK attraction at 2.63x (obs=626, exp=239, p<0.001). AIIN→QOK repulsion at 0.50x (obs=160, exp=317, p<0.001). Split-half ranges: CHEDY→QOK [2.34, 2.67], AIIN→QOK [0.39, 0.53].

Survived: section splits, Currier A/B, line-position controls (mid-position only: 2.37x), top-10 token removal (2.07x), frequency conditioning, section-specific measurement (herbal_A 2.62x, biological 1.82x, recipes 2.12x).

The rules operate at the family level: shuffling tokens within families preserves both effects perfectly (0.00 change). The rules describe class-level constraints, not specific token collocations.

CHEDY→QOK is specific to QOK. After CHEDY at +1 (ratio = observed rate / overall token rate): QOK=2.62x, OK=0.83x, OT=0.80x, AIIN=1.08x, OTHER=0.82x. CHEDY does not attract backbone families in general. It specifically attracts QOK and mildly repels OK, OT, and OTHER. Note: the core JSON transition matrix uses a different baseline (destination-position rate rather than overall rate), yielding CHEDY→AIIN=0.77x. Both computations are correct; the difference arises because AIIN's destination-position rate differs from its overall rate. The paper and this document use the overall-rate baseline for the specificity comparison.

The dependency extends beyond adjacency: +1=2.62x, +2=1.23x, +3=1.32x, +4=1.16x, +5=1.02x. It reaches 3-4 tokens forward but is strongest at immediate adjacency.

### 1.2 AIIN invariance

Page means: Currier A=15.0%, Currier B=15.0%. KS p=0.742. Bootstrap CI for A-B difference: [−2.0%, +2.0%].

AIIN does not self-cluster (SC=0.98x). It passes OK (2.73x), OT (2.21x), and CHEDY (1.64x) through but blocks QOK (0.83x).

AIIN is elevated at line-initial position (+3.2% residual after controlling for section, frequency, and window composition). This effect is specific to continuation lines (16.7% at ordinary line starts vs 9.8% at paragraph starts).

AIIN→QOK repulsion is strictly local: 0.42x at +1, already 1.16x at +2. AIIN blocks QOK only at immediate adjacency.

Caveat: invariance holds under the standard definition (contains "aiin" or "ain") but fails under strict (p=0.004) and loose (p=0.001) alternatives.

### 1.3 Bidirectional self-clustering symmetry

Prefix SC=1.524x, suffix SC=1.544x, ratio=0.99. Bootstrap 95% CI: prefix [1.41, 1.62], suffix [1.48, 1.60].

Unique among all tested systems. All 16 natural-language comparators with positive self-clustering are suffix-dominant (ratios 0.29–0.81). No tested system is prefix-dominant. Ottoman Turkish (the strongest candidate for bidirectional morphology due to Arabic prefix layer over Turkic suffixes) tested at prefix=0.70x, suffix=1.04x, ratio=0.67 — SYMM-LOW. Swahili (Bantu), which has textbook bidirectional morphology (prefix subject/class agreement + suffix tense/aspect markers), tested at prefix=0.79x, suffix=0.96x, ratio=0.82 — also SYMM-LOW. Georgian (Kartvelian), which has polypersonal prefix+suffix agreement, tested at prefix=0.98x, suffix=0.86x — SYMM-LOW. Tagalog (Austronesian), with infixation plus prefix/suffix morphology, tested at prefix=0.44x, suffix=0.41x — also SYMM-LOW. Having bidirectional morphology in a natural language does not produce Voynich's symmetric elevated clustering. Tested across 4 typologically distinct bidirectional-morphology languages (Swahili, Ottoman Turkish, Georgian, Tagalog), none approaches SYMM-HIGH.

Mandarin Chinese (Sinitic, isolating morphology) tested at prefix=0.82x, suffix=0.78x, ratio=1.04 — SYMM-LOW. As expected, an isolating language with no affixal morphology produces near-zero clustering in both directions. This establishes the SYMM-LOW floor for morphologically minimal systems.

Medieval Latin abbreviation simulation: applying standard 15th-century scribal abbreviations (prefix contractions com→c̃, pre→p̃, per→p̄ and suffix contractions -bus→;, -rum→ꝝ, -tur→t̄) to expanded Latin text does NOT move it toward SYMM-HIGH. Even at 90%/95% abbreviation rates, Latin remains strongly SUFFIX-DOM (ratio 0.29). Abbreviation is not a viable path to the Voynich profile.

Root extraction analysis (results/root_extraction_results.json): stripping EVA prefix/suffix wrappers compresses 7,255 token types to 3,193 root types (44% of original vocabulary). Root distribution is moderately Zipfian (R²=0.894, comparable to token-level R²=0.901). Currier A/B root vocabulary overlap increases slightly vs token-level (Jaccard 16% vs 14%), with weak but significant rank correlation (ρ=0.367). AIIN roots collapse to the AIIN morpheme itself (aii, ii, ai), confirming function-word-like structure. Results are consistent with affixal structure but not strong enough to confirm natural-language lexicon underneath.

The symmetry persists across all sections, Currier types, and line positions. Per-scribe breakdown: Hand 1 (9,024 tokens): SYMM-HIGH (1.52x/1.54x, ratio 0.99). Hand 3 (11,390 tokens): SYMM-HIGH (1.27x/1.32x, ratio 0.96). Hands 4 and 5 (small samples): SYMM-HIGH. Hand 2 (9,155 tokens): SYMM-LOW (1.10x/1.23x, ratio 0.89). The symmetry is carried primarily by Hands 1, 3, 4, and 5; Hand 2 shows weaker and more suffix-leaning clustering.

No encoding simulation reproduced the full profile (symmetric-high clustering + 71% hapax + grammatical variance CV=0.40 + transition rules >2.5x). Bidirectional padding of Arabic came closest (ratio 0.77) but missed symmetry and inflated hapax. Grammar-aware edge templating preserved transition rules (CV 0.35) but produced PREFIX-DOM, not SYMM-HIGH.

### 1.4 Lines are grammatical units

CHEDY→QOK within-line: 2.54x. Cross-line: 0.85x. The transition rule reverses at line boundaries. AIIN→QOK within-line: 0.40x. Cross-line: 1.22x. Also reverses.

The reset is universal: it occurs at every line-break type (after short lines, medium, long), in both Currier types, and is not specific to paragraph boundaries.

Self-clustering persists across line breaks (OK 2.24x cross-line, OT 3.03x, CHEDY 1.50x). Family neighborhoods span lines; sequential grammar does not. Lines are clausal units with internal syntax.

Whole-line family templates recur at only 1.04x above shuffled control (1.20x for coverage). Lines are NOT template-based. Each line has unique family composition, constrained by within-line grammar but not drawn from a fixed template library.

### 1.5 Suffix agreement between adjacent tokens

Suffix agreement ratios (observed same-ending / expected under independence): CHEDY→QOK 1.18x, QOK→QOK 1.41x, OK→OT 1.75x, OK→OK 1.67x, OT→OT 1.49x. All significant vs shuffled null model (z=3.4–5.0).

Survives frequency conditioning: CHEDY→QOK 1.20x after matching frequency bands, QOK→QOK 1.36x, OK→OT 1.72x, OK→OK 1.61x.

CHEDY selects specific QOK subtypes (Chi²=36.4, p=7.2×10⁻⁵). -dy CHEDY → 40% -dy QOK. -ey CHEDY → 32% -ey QOK. CHEDY strongly avoids qokchy (0.13x) — QOK tokens that share CHEDY's own mantle characters.

### 1.6 Multi-feature agreement

Adjacent tokens agree on multiple dimensions simultaneously. Combined agreement ratios (suffix + length + mantle + circles): OK→OT 8.74x, OK→OK 6.56x, QOK→QOK 5.00x, OT→OT 4.56x, CHEDY→QOK 7.64x.

Each added feature contributes independent predictive information. OK→OT: suffix alone 1.75x → suffix+length 3.44x → all four features 8.74x. The features are not redundant.

Length agreement conditioned on suffix+frequency collapses to 1.00x. Length is partially a downstream consequence of suffix — tokens with the same suffix tend to be similar length. Suffix is the primary agreement feature.

### 1.7 Agreement cascades through 3-token chains

When A and B agree on suffix, B→C agreement jumps dramatically: CHEDY→OTHER→CHEDY: if A≡B, B→C=85%; if A≠B, B→C=4% (80-point cascade). QOK→OTHER→QOK: 62% vs 18% (44-point). QOK→QOK→QOK: 52% vs 19% (33-point). CHEDY→QOK→CHEDY: 69% vs 13% (56-point).

Suffix agreement jumps over OTHER tokens: QOK→[OTHER]→QOK at 2.32x, CHEDY→[OTHER]→CHEDY at 1.43x, OT→[OTHER]→OT at 1.87x. The agreement system treats OTHER-family tokens as transparent.

Suffix cascades also persist across line boundaries (within-line cascade: +42pp; cross-line cascade: +48pp, n=21). This contrasts with the transition rules (§1.4), which reset at line breaks. The agreement system and the sequential grammar system have different boundary behaviors: suffix features propagate across lines even though CHEDY→QOK attraction does not.

### 1.8 Productive morphological paradigm structure

Each family has hub-centered edit-distance-1 graphs. Top hubs: chedy connects to 12 edit-1 neighbors, daiin to 10, qokeedy to 7. All 50 tested types per family are connected — no isolated nodes.

The same edit operations recur across all four major sections: insertion/deletion of 'e' (92% mid-position), insertion/deletion of 'd' (74% end-position), c↔s substitution (ch↔sh, 62% mid-position), insertion/deletion of 'l' (89% start-position). Operations are positionally locked to specific word positions — prefix-like, stem-internal, and suffix-like.

High-frequency stems generate more edit-1 variants: correlation (log-frequency vs variant count) r=0.516 for QOK, r=0.598 for CHEDY, r=0.686 for AIIN. Stems at frequency 100+ have 2–3x more variants than stems at frequency 2–5. Caveat: shuffled Voynich tokens (r=0.61) and trigram-generated null tokens (r=0.67) produce comparable or higher correlations. The frequency-variant correlation is partially a combinatorial property of Zipfian distributions on edit-distance graphs, not solely a morphological diagnostic. The stronger evidence for productive paradigms is the hub-centered graph structure, positionally locked edit operations, and cross-section consistency of those operations.

### 1.9 CHEDY avoids line-final position

Residual after full control (section + frequency + window composition): −2.7%. Present in both Currier types (A: −1.6%, B: −5.0%). Strongest in medium and long lines (−3.2% to −5.3%). Consistent with CHEDY requiring a within-clause complement (QOK) that cannot appear after the line boundary.

### 1.10 Glyph layer architecture

Clustering signal lives independently in both crust-only (1.86x/2.01x) and mantle+core-only (1.88x/2.00x) layers. Full tokens (1.29x/1.54x) are diluted by cross-layer interference.

Sequential grammar lives primarily in circles (o, a, y) and core (gallows). Scrambling circles drops CHEDY→QOK from 2.50x to 1.75x. Scrambling crust has no effect on transitions or self-clustering. Scrambling mantle has no effect.

Family identity is best predicted by crust characters (79.4% accuracy). QOK and OK are 100% predicted by their first character. CHEDY and AIIN are 99% predicted by their last character.

Different glyph zones encode different information: crust carries identity (content), circles and core carry sequential grammar, transition rules depend on word-final characters, self-clustering depends on interior structure.

---

## Section 2: Claims Weakened But Retained in Limited Form

### 2.1 AIIN as function word

Behavior is consistent with a function-word role: invariant frequency, non-self-clustering, line-initial preference, selective carry-through. But AIIN has 842 unique types — more than any other family — and higher positional entropy than CHEDY at every line position. Function words in natural language typically have LOW entropy (few variant forms). AIIN may be a function-word class that the encoding has diversified, or it may be a different kind of structural element altogether.

Status: consistent with function-word role but not confirmed. The high type count is unexplained.

### 2.2 Entry-level opening/closing templates

Position 1 on each page has QOK at 0.0% and OTHER at 78.0%. By position 5, CHEDY rises to 12.6%. Pages tend to open with OTHER-family tokens. AIIN shows a modest rising trend from OPEN to CLOSE (13.8% → 16.1%, +2.3%). But when measured as entry thirds, most families are STABLE across phases. The "opening-middle-closing" template is weaker than initially reported — the real structure is at the line level, not the entry level.

Status: line-initial and line-final family preferences are real and survive controls. Entry-level phase structure is modest at best.

### 2.3 Self-clustering magnitude

Pooled backbone: 1.451x. Page-level mean: 0.929x. The value is method-sensitive. Self-clustering is real (every family independently shows it in ablation) but the specific number depends on computation method. The bidirectional symmetry (prefix/suffix ratio 0.99) is stable regardless of method.

### 2.4 Formulaic genre identification

Section-specific vocabulary with shared grammar, open lexicon (71.4% hapax), productive slots (mean 6.6 unique fillers per frame), distributed within-section recurrence — all consistent with a formulaic domain text (herbal, medical, recipe). But genre identification is inference from structural analogy, not direct comparison against genre-matched corpora. No medieval herbal or recipe text has been tested with the same pipeline for structural comparison.

### 2.5 Family-level grammar as "syntax"

The transition rules (CHEDY→QOK, AIIN→QOK repulsion) are statistically robust but have near-zero predictive power for next-token family (59.6% = baseline majority class). Family bigram prediction gives 0.0% lift. Even family history of 5 gives only +3.6%. The grammar is a weak statistical tendency, not strong syntactic prediction. Token-level bigrams give 99% prediction — the text is highly repetitive at the token level, but this doesn't map to family-level prediction.

The grammar is real but weak: it describes departures from independence in the transition matrix, not usable prediction rules. It is better described as "collocational preference with class-level structure" than as "syntax."

---

## Section 3: Claims Retired

### 3.1 Arabic is the closest structural match

Retired. Arabic is suffix-dominant (prefix 1.92x, suffix 2.66x, ratio 0.72). Voynich is symmetric (ratio 0.99). The earlier finding was an artifact of measuring only prefix families. Under bidirectional analysis, Arabic and Voynich occupy different structural categories (SUFFIX-DOM vs SYMM-HIGH).

### 3.2 Uralic languages (Estonian, Finnish) match Voynich

Retired. Estonian SC=1.35x and Finnish SC=1.16x were false positives from 10K-sentence corpora. At 100K sentences: Estonian prefix=0.96x, Finnish prefix=1.01x. Both are suffix-dominant under bidirectional analysis. The corpus-size artifact inflated prefix clustering for small samples.

### 3.3 15 languages compared

Corrected. 16 natural-language comparators (12 Leipzig including Swahili, Georgian, and Tagalog; 2 Gutenberg; 1 Ottoman Turkish UD) + 3 pending (Uzbek, Kazakh, Mongolian) + 1 control. Earlier session counts included ad-hoc downloads and miscounted Voynich as a comparator.

### 3.4 Self-clustering = 1.44x

Retired as a fixed number. Range: 0.93x (page-level) to 1.45x (pooled backbone) depending on method. The value is method-sensitive and should be reported as a range.

### 3.5 CHEDY→QOK = 2.50x

Corrected. Canonical value from frozen dataset: 2.625x. The 2.50x figure reflects token-parsing variation in earlier runs. Both values are within the split-half range [2.34, 2.67].

### 3.6 Entry-level template structure (opening/middle/closing phases)

Retired as a strong claim. When measured as entry thirds, phase shifts are 0.8–2.3% — present but modest. The dramatic initial-position effects (QOK at 0.0% in position 1) are real but concentrated in the first 1-2 tokens, not sustained across entry phases.

### 3.7 Constructed system as equally plausible

Weakened substantially. No tested constructed system reproduces the combination of: multi-feature suffix agreement cascading through chains, hub-centered paradigm morphology with frequency-correlated productivity, cross-section consistent transformation rules, open vocabulary with 71% hapax, and bidirectional self-clustering symmetry. The constructed-system hypothesis requires engineering all of these properties independently, which demands linguistic sophistication with no known 15th-century precedent. It remains logically possible but substantially more expensive than encoded natural language.

---

## Methodological Caveats (apply to all claims)

1. All family definitions are EVA-specific. Cross-transcription validation has been performed using the LSI interlinear file (Currier, FSG/Friedman, Takahashi, and Grove transcriptions, all mapped to EVA alphabet but with independent tokenization). All four transcriptions produce SYMM-HIGH bidirectional symmetry, CHEDY→QOK attraction (2.01–2.48x), AIIN→QOK repulsion (0.21–0.47x), and line-bounded grammar reset. The core findings are stable across transcribers. Validation under non-EVA alphabets (original Currier alphabet, original FSG alphabet) remains an open question.

2. All comparison languages are modern proxies (Leipzig Wikipedia) except Middle English (Gutenberg) and Ottoman Turkish (UD treebank). No medieval herbal, recipe, or formulaic text has been tested with the same pipeline.

3. Self-clustering values are method-sensitive. The bidirectional ratio (0.99) is stable; the absolute values are not.

4. The suffix agreement cascade effect (Test 1.7) has been tested only for suffix features. Whether mantle, circle, or other glyph dimensions show the same cascade behavior is untested.

5. Numbers shift ~10-15% between runs due to token-parsing variation. All canonical values are from frozen local datasets.

6. No decipherment is claimed or attempted.

7. Findings 1.1–1.3 are reproducible via scripts 01–03. Findings 1.4–1.10 are reproducible via 04_extended_analysis.py, which produces results/extended_analysis_results.json. All 27 canonical values are verified by the regression test suite (tests/test_canonical_values.py). Some values in this document differ slightly from the scripted output due to differences in computation path (e.g., family detection method, stratification granularity); the scripted values are canonical for reproduction purposes.
 All findings describe statistical structure, not semantic content. The project identifies constraints that any decipherment theory must satisfy, but does not identify the manuscript's language or meaning.

---

## Appendix: Minimum Viable Explanation Requirements

Any proposed explanation of the Voynich Manuscript text — whether decipherment, generation theory, cipher identification, or hoax mechanism — must account for all of the following simultaneously. Explanations that address some but not others are incomplete.

### 1. Line-bounded grammar reset
Within-line CHEDY→QOK attraction is 2.54x. Cross-line it drops to 0.85x. The transition rules operate within lines and reset at every line boundary regardless of line length, section, or Currier type. The explanation must produce text where sequential grammar is line-internal.

### 2. CHEDY→QOK specificity
CHEDY attracts QOK at 2.62x while simultaneously repelling OK (0.83x) and OT (0.80x). This is a targeted class-to-class dependency, not a general content-density effect. The explanation must produce specific asymmetric attraction between particular word classes.

### 3. Suffix-led multi-feature agreement
Adjacent tokens from specific family pairings agree on suffix class at 1.18–1.75x above chance, with the effect compounding across suffix + length + mantle to 5–9x. The explanation must produce morphological concord between adjacent content words.

### 4. Agreement cascades through three-token chains
When two adjacent tokens agree on suffix, the probability of the next token also agreeing jumps by 20–80 percentage points. Agreement propagates across intervening OTHER tokens (QOK→[OTHER]→QOK at 2.32x, CHEDY→[OTHER]→CHEDY at 1.43x). The explanation must produce feature propagation across multi-token spans.

### 5. Productive morphological paradigms
Each family contains hub-centered edit-distance graphs where high-frequency stems have 2–3x more morphological variants than low-frequency stems (r = 0.52–0.69). The same positionally constrained edit operations (prefix-like, stem-internal, suffix-like) recur across all four major sections while the specific vocabulary changes. The explanation must produce a productive morphological system with frequency-correlated variant generation.

### 6. Bidirectional self-clustering symmetry
Prefix SC = 1.52x, suffix SC = 1.54x, ratio = 0.99. No tested natural language (0 of 16) produces this. All natural languages with positive self-clustering are suffix-dominant. The explanation must produce balanced elevated clustering at both word beginnings and word endings simultaneously.

### 7. Section-stable grammar with shifting lexicon
Transition rules, suffix agreement, morphological operations, and family proportions are consistent across herbal, biological, and recipe sections. But within-family vocabulary overlap between sections is only 0.09–0.25 (Jaccard). The explanation must produce a system where the grammatical infrastructure is shared but the specific word inventory changes by topic.

### 8. Open vocabulary with natural-like distribution
71.4% hapax legomena. Type/token ratio 0.23. Grammatical variance CV = 0.40 with the transition rules breaking in 6% of 500-token windows. Top-100 bigrams cover only 3.7% of text. Frame slots accept mean 6.6 unique fillers. The explanation must produce a genuinely open, non-template vocabulary with natural-like frequency distribution and occasional rule violations.

### Checklist

| # | Requirement | Encoded natural language | Constructed system | Simple cipher | Table/grille generation |
|---|---|---|---|---|---|
| 1 | Line-bounded grammar | Yes (clause = line) | Possible if designed | No mechanism | No mechanism |
| 2 | Specific class attraction | Yes (inherited syntax) | Requires design | No mechanism | No mechanism |
| 3 | Suffix agreement | Yes (morphological concord) | No known precedent | Destroys morphology | No mechanism |
| 4 | Agreement cascades | Yes (feature propagation) | No known precedent | No mechanism | No mechanism |
| 5 | Productive paradigms | Yes (inflectional system) | No 15th-c. precedent | Destroys paradigms | No mechanism |
| 6 | Bidirectional symmetry | Requires syllabic encoding | Possible if designed | Cannot produce | Cannot produce |
| 7 | Stable grammar, shifting lexicon | Yes (topic variation) | Requires elaborate design | Preserved if syllabic | Partial |
| 8 | Open vocabulary, natural distribution | Yes (natural property) | Requires Zipf engineering | Partially preserved | No (template-bound) |

Only encoded natural language satisfies all eight requirements without requiring mechanisms that lack historical precedent. Constructed systems can satisfy requirements 1, 2, 5, and 6 individually but have no known 15th-century precedent for requirements 3, 4, and 5 (morphological concord, agreement cascades, and productive paradigms). Simple ciphers and table/grille generation fail requirements 1–6.

This does not prove encoded natural language. It establishes that encoded natural language is the only hypothesis that does not require historically unprecedented mechanisms.

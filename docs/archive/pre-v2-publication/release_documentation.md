# Release Documentation

## 1. Claim Ledger

| Claim | Status | Evidence Basis | Where It Appears | Public Phrasing |
|---|---|---|---|---|
| Voynich has non-random sequential constraints | **Supported** | Chi²=1408, p<10⁻²⁸¹; shuffle control = 0.7 | README, paper, dashboard | "The transition matrix departs significantly from independence" |
| CHEDY→QOK attraction (2.63x) manuscript-wide | **Narrowed** | Obs=626, exp=239 aggregate. Per-scribe: Hand 2 = 2.15x (n=374), Hand 3 = 2.28x (n=222). Hand 1 = 1.42x (n=13). Hand 5 = 1.06x (n=6). Effect is concentrated in Hands 2 and 3. | README, paper, JSON, `results/per_scribe_results.json` | "CHEDY→QOK is a property of Hands 2 and 3, not a uniform manuscript-wide rule" |
| AIIN→QOK repulsion (0.50x) | **Supported** | obs=160, exp=317, split-half [0.39, 0.53], holds across text types | README, paper, dashboard, JSON | "AIIN→QOK repulsion at 0.50x" |
| AIIN invariance at 15% across Currier A/B | **Supported with caveat** | KS p=0.742, bootstrap CI [−2.0%, +2.0%]; BUT fails under strict (p=0.004) and loose (p=0.001) definitions | README, paper, dashboard, JSON | "Invariant under standard definition; sensitive to alternative definitions" |
| AIIN has function-word-like behavior | **Supported with caveat** | Non-self-clustering, selective carry-through, invariance. But 842 unique types — higher entropy than CHEDY at every line position, opposite of typical function-word pattern. | README, paper, dashboard | "Consistent with a function-word role; type-count entropy complicates the interpretation" |
| Transition rules are "grammar" | **Narrowed** | χ² significant but predictive lift near 0% at family-bigram, +3.6% at 5-gram. Real statistical pattern, weak predictive power. | README, paper | "Collocational preference with class-level structure; not predictive syntax" |
| Arabic is the closest structural match | **Retired** | Was based on prefix-only SC. Arabic is suffix-dominant (ratio 0.72); Voynich is symmetric (ratio 0.99) | Corrections log only | Do not use. Replaced by bidirectional symmetry finding |
| Uralic languages match Voynich | **Retired** | Estonian 1.35x and Finnish 1.16x were false positives from 10K corpora. At 100K: 0.96x and 0.91x prefix | Corrections log only | Do not use |
| Bidirectional self-clustering symmetry | **Supported and strengthened** | Prefix 1.52x, suffix 1.54x, ratio 0.99, bootstrap CI prefix [1.41, 1.62], suffix [1.48, 1.60]. Unique among 16 tested natural-language comparators. Independently SYMM-HIGH in Hands 1, 2, 3 (94% of corpus). Survives across 4 alternative EVA-alphabet transcriptions (Currier, FSG, Takahashi, Grove). | README, paper, dashboard, JSON | "Voynich is the only tested system with elevated, balanced self-clustering in both directions; holds across scribes and alternative transcriptions" |
| Prefix-family method has directional bias | **Supported** | Suffix test reverses rankings: Finnish 0.96x→1.51x, Estonian 0.96x→2.33x | README, paper, JSON | "The prefix-family method inherently favors languages with consistent prefixing morphology" |
| Cross-transcription stability | **Tested across 4 EVA-alphabet transcriptions** | Currier, FSG, Takahashi, Grove all produce SYMM-HIGH. Non-EVA-alphabet transcriptions not yet tested. | Paper, README, JSON | "Stable across Currier/FSG/Takahashi/Grove transcriptions; non-EVA alphabets remain an open question" |
| "Productive morphological paradigms" (Finding 1.8) | **Retired** | Log-freq vs edit-1 variant correlation r = 0.42–0.71. Trigram null produces comparable r (mean 0.36–0.48, Voynich never exceeds null 95th percentile). Chaucer at same measurement r = 0.20. The correlation is a Zipfian-edit-graph property, not evidence of morphology. | `results/paradigm_null_results.json`, `durable_findings.md` §1.8 | "Retired. Hub-centered edit-graph structure retained as descriptive observation without morphological interpretation" |
| "Encoded NL is the only compatible class" (§5) | **Retired** | A first-pass synthetic constructed system (`09_constructed_control.py`) satisfies 5 of 7 testable MVE items by direct design (items 1, 2, 3, 4, 6). Items 5 (bidirectional symmetry) and 7 (open vocabulary) discriminate; 1-4 and 6 do not. | `results/constructed_control_results.json`, `durable_findings.md` MVE appendix | "Among tested classes (random, shuffle, simple cipher, first-pass constructed control), encoded NL is compatible with all 7 items. Sophisticated constructed systems that engineer items 5 and 7 have not been ruled out." |
| Agreement cascades +20-80pp (point estimates) | **Supported with CIs added** | All 5 chains survive Benjamini-Hochberg FDR at α=0.05. Flagship +81pp has conservative 95% CI [+48, +94]pp on n=13. Two chains (QOK→QOK→QOK, OT→O→OT) have CIs touching zero. | `results/cascade_uncertainty_results.json`, JSON | "+19 to +81pp point estimates; all 5 chains survive FDR; flagship cascade CI [+48, +94]pp with n=13" |
| Voynich is written in [specific language] | **Not tested** | No semantic analysis performed. Structural comparison only | Explicit in limitations | "These findings do not identify the manuscript's language" |
| Decipherment or semantic content | **Not tested** | Entirely outside scope | Explicit in limitations | "No decipherment is claimed or attempted" |
| Ottoman Turkish match | **Tested (small corpus)** | UD treebank 16,890 words: prefix 0.70x, suffix 1.04x, ratio 0.67 — SYMM-LOW | README, durable_findings | "Ottoman Turkish tested: SYMM-LOW. Not a match. Larger corpus would be preferable." |
| Two independent structural layers | **Supported with caveat** | Ablation: QOK/OT drive SC, CHEDY/AIIN drive transition rules. Interpretation is structural, not semantic; depends on EVA layer definitions | Paper | "Self-clustering and transition rules are carried by different families under EVA-layer ablations" |

## 2. Abstract

We analyze sequential constraints between token families in the Voynich Manuscript (Beinecke MS 408) using the Zandbergen-Landini EVA transliteration (31,608 tokens, 184 pages). We identify two class-level transition effects: CHEDY→QOK attraction (2.63x aggregate, primarily from Hands 2 and 3) and AIIN→QOK repulsion (0.50x), both distributed across hundreds of unique token pairs. The AIIN family density is invariant at 15.0% across Currier A and B language modes (KS p=0.742) under the standard definition.

We introduce a bidirectional self-clustering test comparing prefix-family and suffix-family self-similarity across 16 natural-language comparators and a shuffled-token control. Four languages specifically selected to stress the uniqueness claim — Swahili (Bantu, prefix+suffix morphology), Georgian (Kartvelian, polypersonal agreement), Tagalog (Austronesian, infixation + affixation), and Mandarin (Sinitic, isolating) — all test SYMM-LOW. Voynich is the only tested system with balanced elevated clustering in both directions (prefix 1.52x, suffix 1.54x, ratio 0.99). The SYMM-HIGH profile holds independently in each of the three major scribal hands (94% of corpus) and across four alternative EVA-alphabet transcriptions (Currier, FSG, Takahashi, Grove).

Three further analyses test standard objections. (i) A character-trigram null model for the log-frequency vs edit-1 variant-count correlation previously interpreted as "productive morphology": Voynich r does not exceed the null's 95th percentile for any family; the productive-morphology interpretation is retired. (ii) Wilson-score 95% confidence intervals and Benjamini-Hochberg FDR correction on the five agreement-cascade chains: all survive FDR; the flagship +81pp effect has conservative CI [+48, +94]pp on n=13. (iii) A first-pass synthetic constructed-system control: satisfies 5 of 7 MVE checklist items by direct design, fails on bidirectional symmetry and 71%+ hapax.

These findings establish structural constraints that any decipherment or generation theory must account for but do not identify the manuscript's language or content. The narrower claim that survives this revision: among hypotheses tested against the actual pipeline (random, shuffled, simple substitution cipher, first-pass constructed), encoded structured language is the most plausible. Sophisticated constructed or hybrid systems that engineer bidirectional symmetry and open vocabulary have not been tested and cannot be excluded.

## 3. Executive Summary

**What is this?** A statistical analysis of word-group patterns in the Voynich Manuscript — an undeciphered 15th-century book. We measure how groups of similar-looking words follow each other, and compare those patterns against 16 real languages and 1 shuffled-token control.

**What did we find?**

1. The manuscript has real above-chance class-level patterns. Specifically, CHEDY-family words tend to be followed by QOK-family words more than chance predicts, and AIIN-family words tend to block QOK. These effects are distributed (77% of individual CHEDY tokens participate) rather than being fixed phrases. But per-scribe analysis shows the CHEDY→QOK effect is primarily a property of two of the five scribes.

2. AIIN density stays near 15% across both "language modes" (Currier A and B) of the manuscript, consistent with some structural role like a filler or particle — though AIIN has an unusually high number of distinct types for a function word.

3. Voynich clusters equally at word beginnings AND word endings (bidirectional symmetry). Every real language we tested clusters more at one end than the other. This property holds independently in each of the three major scribes and across four alternative transliterations. No tested natural language produces this.

**What we tried and found NOT supported:**

- Earlier versions described "productive morphology" based on a log-frequency correlation. We ran that correlation against a null model that contains no morphology; the null matches or exceeds Voynich, and Chaucer at the same definition is lower. **The productive-morphology claim is retired.**

- Earlier versions said "encoded natural language is the only compatible class." We built a synthetic constructed corpus with designed rules matching the checklist. It satisfied 5 of 7 items directly. **The "only compatible class" claim is retired.** What survives: the symmetric self-clustering and the 71% hapax rate discriminate; the other items do not.

**Major caveats:**
- Word families defined by EVA character strings. Bidirectional symmetry tested across four EVA-alphabet transcriptions and survives; non-EVA-alphabet transcriptions remain untested.
- Comparison languages are modern proxies (Leipzig Wikipedia) with two historical exceptions (Chaucer, KJV) and one small medieval corpus (Ottoman Turkish UD).
- "Grammar" as used in this project is a weak statistical tendency with near-zero family-bigram predictive power. It is better called "class-level collocational preference."
- No decipherment is claimed.

**What could outside experts test?** Define token families under non-EVA-alphabet transcriptions (FSG characters, Currier characters). Test sophisticated constructed systems that explicitly engineer bidirectional symmetry plus Zipfian open-vocabulary distributions. Test against medieval herbal and recipe corpora with this pipeline. Analyze cross-transcription high-confidence word-boundary subset.


## 4. Release Checklist

- [x] README matches canonical JSON results
- [x] Paper matches canonical JSON results
- [x] Dashboard matches canonical JSON results
- [x] All 13 result files present (core, cross-linguistic, stress, corpus-size, prefix-suffix, extended, cross-transcription, paradigm-null, cascade-uncertainty, per-scribe, constructed-control, root-extraction, validation)
- [x] Manifests present (CSV, JSON, download_results, source_notes)
- [x] Validation report present and current
- [x] Raw data bundled in repo (226MB); fetch script is optional rebuild tool
- [x] Pending datasets labeled as pending (Uzbek, Kazakh, Mongolian)
- [x] "Arabic-only match" claim retired from all active materials
- [x] "Uralic match" claim retired from all active materials
- [x] Bidirectional symmetry is the central cross-linguistic finding
- [x] Limitations are explicit in README, paper, and this document
- [x] No language-identification claims
- [x] No decipherment claims
- [x] Corrections log documents all retired claims
- [x] Quick-start instructions work from project root
- [x] Scripts use local frozen data, not live downloads

## 5. Public Limitations

These limitations are inherent to the current analysis and should not be minimized:

1. **EVA-family dependence.** All family definitions (QOK, OK, OT, CHEDY, AIIN) are based on the EVA transliteration alphabet. Cross-transcription stability has been confirmed across four alternative EVA-alphabet transcriptions (Currier, FSG, Takahashi, Grove). Results under non-EVA character-boundary systems could differ and remain untested.

2. **Modern comparison corpora.** All Leipzig comparison languages are modern Wikipedia text. They are structural proxies for their language families, not medieval equivalents. Historical Latin, Old French, and medieval Italian are not tested. Ottoman Turkish was tested with a small UD corpus (SYMM-LOW) but a larger historical corpus is needed.

3. **No decipherment.** This analysis identifies statistical patterns in token sequences. It does not decode any text, identify any language, or assign meaning to any word.

4. **Method sensitivity.** Self-clustering values range from 0.93x (page-level) to 1.45x (pooled backbone) depending on computation method. The prefix/suffix comparison is stable but uses auto-detected affix families that may vary across runs.

5. **Directional bias.** The prefix-family method used in earlier Voynich research inherently favors languages with consistent prefixing morphology. The suffix extension corrects this but introduces its own auto-detection uncertainty.

6. **AIIN invariance is definition-dependent.** It holds under the standard definition (contains "aiin" or "ain") but fails under stricter (p=0.004) and looser (p=0.001) alternatives.

7. **Ottoman Turkish tested with small corpus only.** UD treebank (16,890 words) shows SYMM-LOW, not a match. A larger historical corpus is needed for confirmation given the manuscript's probable 15th-century origin.

8. **Cross-transcription validation scope.** Results are stable across four alternative EVA-alphabet transcriptions (Currier, FSG, Takahashi, Grove). Validation under non-EVA character-boundary systems (original Currier alphabet, original FSG alphabet with different glyph groupings) remains an open question.

## 6. GitHub Release Text

**Repo description:**
Statistical analysis of sequential token-family constraints in the Voynich Manuscript, with bidirectional self-clustering comparison against 16 natural-language comparators.

**Tagline:**
Quantitative transition grammar analysis of the Voynich Manuscript. Identifies distributed sequential rules, a structural constant, and a unique bidirectional self-clustering signature.

**Release title:**
v1.0 — Transition Grammar with Bidirectional Self-Clustering Analysis

**Release notes:**
First public release. Includes frozen datasets (226MB), reproducible analysis scripts (00–09), interactive React dashboard, and research paper (revised v2). Key findings: two robust transition rules (CHEDY→QOK 2.63x aggregate in Hands 2 and 3, AIIN→QOK 0.50x), AIIN invariance at 15% across language modes, and bidirectional self-clustering symmetry unique among 16 tested comparators. A productive-morphology interpretation has been retired; a first-pass constructed-system control satisfies 5 of 7 checklist items. All comparison corpora are modern proxies; no language identification or decipherment is claimed.

**Topic tags:**
voynich-manuscript, computational-linguistics, statistical-analysis, digital-humanities, historical-cryptography, morphological-analysis

**Suggested first 3 issues:**

1. **Cross-transcription validation: FSG/Currier family definitions** — Define equivalent token families under non-EVA transcription alphabets and test whether transition rules and self-clustering hold.

2. **Ottoman Turkish with larger corpus** — The UD treebank (16,890 words) shows SYMM-LOW. Source a larger digitized Ottoman Turkish corpus to confirm this result.

3. **Constructed language and cipher controls** — Test whether Enochian, Esperanto, or a Cardan grille with positional constraints can produce bidirectional self-clustering symmetry.

## 7. Top 10 Ways a Reader Could Misread This Repo

| # | Misreading | Why It Is Wrong | How the Package Prevents It |
|---|---|---|---|
| 1 | "They identified the language as Arabic" | The Arabic prefix-match was retired. Voynich is symmetric-high; Arabic is suffix-dominant. Different structural types. | Corrections log documents retirement. README centers bidirectional symmetry. Paper §4 explains. |
| 2 | "They decoded the manuscript" | No semantic analysis was performed. No word meanings are assigned. | Limitations section, abstract, and conclusions all state this explicitly. |
| 3 | "The manuscript is proven to be a real language" | Findings are consistent with but not proof of natural language. A complex constructed system could produce similar statistics. | README "What Is NOT Being Claimed" and "Limitations" sections. Paper §5. |
| 4 | "Finnish and Estonian match Voynich" | This was a false positive from 10K corpora. At 100K sentences both drop below 1.0x prefix SC. | Corrections log. Corpus-size analysis in results/. README states explicitly. |
| 5 | "The results depend on which transcription you use" | Within EVA, results are stable (SC 1.51–1.52x across 5 transcriptions). But FSG/Currier have not been tested. | Paper §3, README caveats. Limitation explicitly stated. |
| 6 | "They compared against medieval languages" | All Leipzig corpora are modern Wikipedia. Only Chaucer and KJV are historical. | Source notes, manifests, README, paper §2.3 all state "modern proxies." |
| 7 | "Self-clustering of 1.45x is a fixed number" | It ranges from 0.93x to 1.45x depending on method. | README caveats, paper §3.3, dashboard self-clustering tab all report the range. |
| 8 | "AIIN is definitely a function word" | Behavior is consistent with a function-word role, but this is a statistical observation, not a linguistic identification. | Claim ledger: "supported with caveat." Paper uses "consistent with." |
| 9 | "The bidirectional symmetry proves the text is artificial" | Symmetry is unusual but does not establish artificiality. An untested natural language could have this property. | Paper §4 lists four possible interpretations including natural language. |
| 10 | "15 languages were compared" | 16 natural-language comparators (13 Leipzig + 2 Gutenberg + 1 Ottoman Turkish UD) + 1 shuffled-token Voynich control = 18 tested systems total. Voynich is the target system, not a comparator. | README, prefix_suffix_analysis.json. |

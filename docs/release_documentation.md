# Release Documentation

## 1. Claim Ledger

| Claim | Status | Evidence Basis | Where It Appears | Public Phrasing |
|---|---|---|---|---|
| Voynich has non-random sequential constraints | **Supported** | Chi²=1408, p<10⁻²⁸¹; shuffle control = 0.7 | README, paper, dashboard | "The transition matrix departs significantly from independence" |
| CHEDY→QOK attraction (2.63x) | **Supported** | obs=626, exp=239, split-half [2.34, 2.67], holds across text types | README, paper, dashboard, JSON | "CHEDY→QOK attraction at 2.63x, robust across sections and text types" |
| AIIN→QOK repulsion (0.50x) | **Supported** | obs=160, exp=317, split-half [0.39, 0.53], holds across text types | README, paper, dashboard, JSON | "AIIN→QOK repulsion at 0.50x" |
| AIIN invariance at 15% across Currier A/B | **Supported with caveat** | KS p=0.742, bootstrap CI [−2.0%, +2.0%]; BUT fails under strict (p=0.004) and loose (p=0.001) definitions | README, paper, dashboard, JSON | "Invariant under standard definition; sensitive to alternative definitions" |
| AIIN has function-word-like behavior | **Supported with caveat** | Non-self-clustering, selective carry-through, invariance. Consistent with but not proof of function-word role | README, paper, dashboard | "Consistent with a function-word role" |
| Transition rules are grammatical, not phrasal | **Supported** | 77% of CHEDY tokens participate, 369 unique pairs, top-5 cover 13.3% | README, paper, dashboard, JSON | "Distributed across individual tokens — class-level constraint" |
| Arabic is the closest structural match | **Retired** | Was based on prefix-only SC. Arabic is suffix-dominant (ratio 0.72); Voynich is symmetric (ratio 0.99) | Corrections log only | Do not use. Replaced by bidirectional symmetry finding |
| Uralic languages match Voynich | **Retired** | Estonian 1.35x and Finnish 1.16x were false positives from 10K corpora. At 100K: 0.96x and 0.91x prefix | Corrections log only | Do not use |
| Bidirectional self-clustering symmetry | **Supported** | Prefix 1.52x, suffix 1.54x, ratio 0.99, bootstrap CI prefix [1.41, 1.62], suffix [1.48, 1.60]. Unique among 13 tested natural-language comparators | README, paper, dashboard, JSON | "Voynich is the only tested system with elevated, balanced self-clustering in both directions" |
| Prefix-family method has directional bias | **Supported** | Suffix test reverses rankings: Finnish 0.96x→1.51x, Estonian 0.96x→2.33x | README, paper, JSON | "The prefix-family method inherently favors languages with consistent prefixing morphology" |
| Cross-transcription stability (EVA) | **Supported with caveat** | Stable across 5 EVA-based transliterations (SC 1.51–1.52x). FSG/Currier NOT tested | Paper, README | "Stable across EVA transliterations; FSG/Currier family definitions not yet implemented" |
| Voynich is written in [specific language] | **Not tested** | No semantic analysis performed. Structural comparison only | Explicit in limitations | "These findings do not identify the manuscript's language" |
| Decipherment or semantic content | **Not tested** | Entirely outside scope | Explicit in limitations | "No decipherment is claimed or attempted" |
| Ottoman Turkish match | **Tested (small corpus)** | UD treebank 16,890 words: prefix 0.70x, suffix 1.04x, ratio 0.67 — SYMM-LOW | README, durable_findings | "Ottoman Turkish tested: SYMM-LOW. Not a match. Larger corpus needed." |
| Two independent structural layers | **Supported with caveat** | Ablation: QOK/OT drive SC, CHEDY/AIIN drive transition rules. Interpretation is structural, not semantic | Paper | "Self-clustering and transition rules are carried by different families" |

## 2. Abstract

We analyze sequential constraints between token families in the Voynich Manuscript (Beinecke MS 408) using the Zandbergen-Landini EVA transliteration (31,608 tokens, 184 pages). We identify two robust transition rules: CHEDY→QOK attraction (2.63x, p<0.001) and AIIN→QOK repulsion (0.50x, p<0.001), both distributed across 77% of individual CHEDY tokens and 369 unique token pairs. The AIIN family density is invariant at 15.0% across Currier A and B language modes (KS p=0.742) and exhibits function-word-like behavior.

We introduce a bidirectional self-clustering test comparing prefix-family and suffix-family morphological self-similarity across 13 natural-language comparators and 1 shuffled-token control. All natural languages with positive self-clustering are suffix-dominant. Swahili (Bantu), despite rich bidirectional morphology, also tests SYMM-LOW. Voynich is the only tested system with elevated, balanced clustering in both directions (prefix 1.52x, suffix 1.54x, ratio 0.99). This bidirectional symmetry does not match any tested language family and represents the manuscript's most distinctive measurable structural property.

These findings establish structural constraints that any decipherment or generation theory must account for but do not identify the manuscript's language or content. The prefix-family method used in earlier Voynich research has a directional bias that favors prefix-morphology languages; this bias is documented and corrected in our analysis. All comparison corpora are modern proxies, not medieval texts.

## 3. Executive Summary

**What is this?** A statistical analysis of word-group patterns in the Voynich Manuscript — an undeciphered 15th-century book. We measure how groups of similar-looking words follow each other, and compare those patterns against 11 real languages and 1 shuffled-token control.

**What did we find?**

1. The manuscript has real grammatical rules. Two specific word-group sequences occur far more (or less) often than chance predicts, and this holds everywhere in the text — different sections, different scribes, different line lengths.

2. One word-group (AIIN) appears at exactly 15% of all words regardless of which "language mode" the text is in. It behaves like a function word — the Voynich equivalent of "the" or "and."

3. The most distinctive finding: when we measure whether similar words cluster together, Voynich clusters equally at word beginnings AND word endings. Every real language we tested clusters more at one end than the other. No tested language does what Voynich does.

**Why was the "Arabic match" retired?** Earlier analysis used only word-beginning patterns, which favored Arabic because of its definite article (al-). When we added word-ending patterns, Arabic turned out to cluster much more strongly at endings — it's lopsided, not balanced like Voynich. The match was partially a measurement artifact.

**Why does the symmetry matter?** It means Voynich's structure doesn't map onto any tested natural language's morphology. Whatever system produced this text encodes regularity at both ends of words simultaneously. Real languages don't do that — they're either prefix-heavy (none tested) or suffix-heavy (Arabic, Finnish, Estonian) or flat (English, Turkish).

**Major caveats:** We analyzed transliterated text, not the original script — our word groups may not correspond to real character units. All comparison languages are modern, not medieval. Ottoman Turkish was tested with a small UD treebank (16,890 words) and shows SYMM-LOW — not a match. A larger corpus is needed. We identify structure, not meaning — no decipherment is claimed.

**What could outside experts test?** Define equivalent word families under non-EVA transcription alphabets (FSG, Currier). Test Ottoman Turkish. Test constructed languages and ciphers. Verify whether EVA prefix families map to paleographic character boundaries.

## 4. Release Checklist

- [x] README matches canonical JSON results
- [x] Paper matches canonical JSON results
- [x] Dashboard matches canonical JSON results
- [x] All 6 result files present (core, cross-linguistic, stress, corpus-size, prefix-suffix, validation)
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

1. **EVA-family dependence.** All family definitions (QOK, OK, OT, CHEDY, AIIN) are based on the EVA transliteration alphabet. They may not correspond to meaningful character-level units in the original script. Results under FSG or Currier alphabets could differ.

2. **Modern comparison corpora.** All Leipzig comparison languages are modern Wikipedia text. They are structural proxies for their language families, not medieval equivalents. Historical Latin, Old French, and medieval Italian are not tested. Ottoman Turkish was tested with a small UD corpus (SYMM-LOW) but a larger historical corpus is needed.

3. **No decipherment.** This analysis identifies statistical patterns in token sequences. It does not decode any text, identify any language, or assign meaning to any word.

4. **Method sensitivity.** Self-clustering values range from 0.93x (page-level) to 1.45x (pooled backbone) depending on computation method. The prefix/suffix comparison is stable but uses auto-detected affix families that may vary across runs.

5. **Directional bias.** The prefix-family method used in earlier Voynich research inherently favors languages with consistent prefixing morphology. The suffix extension corrects this but introduces its own auto-detection uncertainty.

6. **AIIN invariance is definition-dependent.** It holds under the standard definition (contains "aiin" or "ain") but fails under stricter (p=0.004) and looser (p=0.001) alternatives.

7. **Ottoman Turkish tested with small corpus only.** UD treebank (16,890 words) shows SYMM-LOW, not a match. A larger historical corpus is needed for confirmation given the manuscript's probable 15th-century origin.

8. **Cross-transcription validation is incomplete.** Results are stable across EVA-based transliterations but have not been tested with non-EVA alphabets that assign different character boundaries.

## 6. GitHub Release Text

**Repo description:**
Statistical analysis of sequential token-family constraints in the Voynich Manuscript, with bidirectional self-clustering comparison against 13 natural-language comparators.

**Tagline:**
Quantitative transition grammar analysis of the Voynich Manuscript. Identifies distributed sequential rules, a structural constant, and a unique bidirectional self-clustering signature.

**Release title:**
v1.0 — Transition Grammar with Bidirectional Self-Clustering Analysis

**Release notes:**
First public release. Includes frozen datasets (226MB), reproducible analysis scripts, interactive React dashboard, and research paper. Key findings: two robust transition rules (CHEDY→QOK 2.63x, AIIN→QOK 0.50x), AIIN invariance at 15% across language modes, and bidirectional self-clustering symmetry unique among 13 tested comparators. All comparison corpora are modern proxies; no language identification or decipherment is claimed.

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
| 10 | "15 languages were compared" | 13 natural-language comparators (10 Leipzig + 2 Gutenberg + 1 Ottoman Turkish UD) + 3 pending + 1 control. Voynich is the target system, not a comparator. | README, prefix_suffix_analysis.json. |

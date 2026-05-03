# Voynich Manuscript: Transition Grammar Analysis

[![DOI](https://zenodo.org/badge/1214800385.svg)](https://doi.org/10.5281/zenodo.19996904)

The Voynich Manuscript is a 15th-century book that nobody can read. The script is unknown, the language (if it is a language) is unidentified, and every proposed decipherment has failed verification. This project doesn't try to decode it. Instead, it measures the statistical structure of the text and asks: what kind of system could have produced these patterns?

The answer is narrower than it first appeared. The text shows statistical regularities that operate within lines and reset at line boundaries, above-chance agreement on word endings between adjacent words, and one distinctive property: balanced elevated self-clustering at both word beginnings and word endings, a profile not shared by any of the 16 natural languages we tested. Within the limited candidate classes implemented in the current pipeline, these findings are inconsistent with random generation and with simple letter-substitution ciphers. They are *not* a basis for excluding sophisticated constructed, hybrid, stenographic, or unmodeled historical mechanisms — a first-pass synthetic constructed control already produced 5 of 7 testable checklist properties (see `results/constructed_control_results.json`). The findings narrow the space of viable explanations against tested models; they do not localize a single one.

**[Interactive Dashboard](https://amy2213.github.io/Voynich-Transition-Grammar/dashboard/voynich_dashboard.html)** · **[Read Paper (PDF)](https://amy2213.github.io/Voynich-Transition-Grammar/docs/paper.pdf)** · **[Durable Findings](docs/durable_findings.md)**

> **Preprint package (May 2026):** *Voynich Manuscript Token-Structure Analysis: Reproducible Corpus Methods and Cross-Linguistic Baselines.* Status: Preprint package prepared for external archival and submission. PDF: [docs/paper.pdf](docs/paper.pdf) (also available as [docs/voynich-token-structure-analysis-2026-05.pdf](docs/voynich-token-structure-analysis-2026-05.pdf)). arXiv source bundle: [supplementary/arxiv_submission_v2.zip](supplementary/arxiv_submission_v2.zip).

## Claim Boundary

This project does not claim semantic decipherment or translation of the Voynich Manuscript. It reports reproducible structural regularities and defines falsifiable constraints that future explanations should address.

The paper and archived release package are the canonical scholarly artifacts. The dashboard is an interactive companion for exploring results.

---

## The key finding nobody else has shown

When you group Voynich words into families by their beginning characters and measure how often the same family appears next to itself, you get a self-clustering score. Do the same thing with ending characters. In every natural language we tested, one direction dominates — endings cluster more than beginnings (suffix-dominant), or neither clusters much. Voynich is the only system where both directions cluster equally and strongly.

| System | Prefix SC | Suffix SC | Ratio | Type |
|---|---|---|---|---|
| **Voynich** | **1.52x** | **1.54x** | **0.99** | **Symmetric-High** |
| Arabic | 1.92x | 2.66x | 0.72 | Suffix-Dominant |
| Latin | 1.11x | 2.93x | 0.38 | Suffix-Dominant |
| Estonian | 0.96x | 2.33x | 0.41 | Suffix-Dominant |
| Finnish | 1.01x | 1.51x | 0.67 | Suffix-Dominant |
| Ottoman Turkish | 0.70x | 1.04x | 0.67 | Symmetric-Low |
| Turkish | 0.91x | 0.98x | 0.92 | Symmetric-Low |
| Swahili | 0.79x | 0.96x | 0.82 | Symmetric-Low |
| Georgian | 0.98x | 0.86x | 1.14 | Symmetric-Low |
| Tagalog | 0.44x | 0.41x | 1.08 | Symmetric-Low |
| Mandarin (Pinyin) | 0.82x | 0.78x | 1.04 | Symmetric-Low |
| Gibberish (shuffled) | 0.92x | 0.97x | 0.96 | Symmetric-Low |

Full table with all 18 systems in [results/prefix_suffix_analysis.json](results/prefix_suffix_analysis.json). This comparison covers 13 modern-proxy languages (Leipzig Wikipedia 100K), 2 historical literary texts (Gutenberg), 1 Ottoman Turkish UD treebank, and 1 shuffled-token control.

### Comparator Set Terminology

To keep counts consistent throughout this repository:

> The comparison set contains **18 tested systems** total: the Voynich corpus, **16 natural-language comparators**, and **1 shuffled-token Voynich control**. The 16 natural-language comparators consist of **13 Leipzig Wikipedia 100K modern-proxy corpora**, **2 historical literary texts** (Project Gutenberg), and **1 small Ottoman Turkish UD treebank**.

Voynich itself is the target system, not a comparator. The shuffled-token "Gibberish" control is generated from the Voynich corpus by random permutation. The arithmetic is `1 + 16 + 1 = 18`, with `13 + 2 + 1 = 16` for the natural-language subset.

This matters because it constrains what the writing system can be. A simple letter-substitution cipher would preserve the source language's suffix dominance. Whatever produced Voynich imposes regularity at both word boundaries simultaneously. This is consistent with several structured generating mechanisms, including some encoding-based and constructed-system possibilities; current data do not discriminate among them.

---

## What else the analysis found

**Class-level sequential constraints exist.** One word family (CHEDY) is followed by another (QOK) at 2.63x above chance, while a third family (AIIN) is followed by QOK at 0.50x — a repulsion, not an attraction. These effects are distributed — 77% of individual CHEDY-type words participate across 369 unique word pairs, not a handful of fixed phrases. The CHEDY→QOK effect is strongest in scribal Hands 2 and 3 (which wrote most of the biological and recipe sections) and is essentially absent in Hand 1 (see `results/per_scribe_results.json`). At the family-prediction level the effect is statistically significant but predictively weak: family-bigram prediction gives ~0% lift over the baseline majority class, 5-token family history gives only +3.6%. It is better described as "collocational preference with class-level structure" than as "grammar" in the sense of predictive syntax.

**Transition rules reset at line boundaries.** The CHEDY→QOK effect is 2.54x within a line but drops to 0.85x across line breaks. Whatever the rule is, it is line-internal. Word-family neighborhoods, by contrast, persist across lines. This pattern is consistent with lines functioning as clause-like or phrase-like units but does not prove it; any rule that resets at line boundaries (scribal, prosodic, formulaic) would produce the same signature.

**Adjacent words agree on their endings at above-chance rates.** When one word ends in -dy, the next word is more likely to also end in -dy than chance predicts (1.18x–1.75x depending on family pair; OT→OT is borderline at z≈1.9). The effect compounds across multiple features (suffix + length + mantle = 5–9x). Agreement propagates through 3-token chains at above-chance rates, with five tested chains all surviving Benjamini-Hochberg FDR correction at α=0.05. The headline CHEDY→OTHER→CHEDY cascade is +81 percentage points with conservative 95% CI of [+48, +94] pp, based on n=13 agreement trials and n=119 disagreement trials. The effect is real but, for the flagship chain, thinly sampled. See `results/cascade_uncertainty_results.json`.

**Hub-centered edit-distance graphs exist, but the "productive morphology" interpretation is not supported.** Each word family contains hub-centered networks of similar words at edit distance 1. The previously reported log-frequency vs variant-count correlation (r = 0.42–0.71) was interpreted as evidence of productive morphology. A character-trigram null model — a synthetic corpus matching Voynich's character bigram statistics but containing no morphology — produces comparable or higher correlations (r ≈ 0.36–0.48 for the same families). Voynich's correlation does not exceed the null's 95th percentile. Chaucer's Middle English produces r = 0.20 at the same measurement, below both Voynich and the null. The correlation appears to be a Zipfian-edit-graph combinatorial property, not evidence of productive morphology. See `results/paradigm_null_results.json`. This finding has been retired from the Minimum Viable Explanation checklist.

**One word family has function-word-like density behavior with caveats.** AIIN appears at ~15% of tokens in both Currier A and B language modes (KS p = 0.742) under the standard definition (tokens containing "aiin" or "ain"). Under stricter or looser definitions the invariance fails (p = 0.004 and p = 0.001 respectively). AIIN does not self-cluster, is elevated at line beginnings, and passes other families through but blocks QOK. This is consistent with some structural role in the text. The "function word" interpretation is tempered by AIIN having 842 unique types — more than any other family, and higher entropy than CHEDY at every line position, which is the opposite of typical natural-language function-word behavior.

---

## What this does NOT claim

This project does not decode any text, identify any language, or assign meaning to any word. Structural similarity is not linguistic identification. The comparison set covers 16 languages but not every language type — Sinitic, polysynthetic, and historical shorthand systems are untested. The bidirectional symmetry does not prove the text is artificial; an untested natural language could have this property. All analysis uses the EVA transliteration, which may not correspond to the original script's character boundaries.

---

## Minimum viable explanation checklist

The following seven measured properties collectively describe the statistical structure of the Voynich text. Any proposed explanation must account for them.

1. **Line-bounded transition reset** — family transition rates reverse at line boundaries (CHEDY→QOK within-line 2.54x vs cross-line 0.85x)
2. **Specific class-level transition** — CHEDY→QOK 2.63x while CHEDY→OK 0.83x, CHEDY→OT 0.80x. Property of Hands 2 and 3 specifically; not a uniform manuscript-wide rule
3. **Suffix agreement** — adjacent-word ending-class match rate above chance at 1.18–1.75x (OK→OT, OK→OK, QOK→QOK, CHEDY→QOK, CHEDY→QOK-by-subtype); OT→OT is borderline
4. **Agreement cascades** — conditional propagation through 3-token chains; five tested chains all survive Benjamini-Hochberg FDR at α=0.05; effect sizes +19pp to +81pp with wide CIs on the flagship +81pp effect
5. **Bidirectional self-clustering** — prefix SC 1.52x, suffix SC 1.54x, ratio 0.99; present independently in Hands 1, 2, and 3 (94% of corpus); SYMM-HIGH profile survives all four alternative EVA-alphabet transcriptions tested (Currier, FSG, Takahashi, Grove)
6. **Section-stable coarse grammar with shifting lexicon** — per-family rates and within-line/cross-line asymmetry similar across sections; within-family Jaccard overlap 0.09–0.25
7. **Open vocabulary** — 71.4% hapax, type/token ratio 0.23, top-100 bigrams cover only 3.7% of text

A previously listed eighth requirement — "productive morphological paradigms" based on a log-frequency vs edit-1 variant-count correlation (r = 0.42–0.71) — has been retired. The correlation is not distinguishable from a character-trigram null model and is lower in Chaucer than in Voynich-trigram-null; the interpretation was not supported. See `docs/durable_findings.md` §1.8 for the retraction record and `results/paradigm_null_results.json` for the test.

### What the checklist discriminates

Not all seven items discriminate between candidate explanations. A first-pass constructed control (`scripts/09_constructed_control.py`) designed with the corresponding rules satisfies items 1, 2, 3, 4, and 6 directly by construction. Item 5 (bidirectional symmetry with the specific SYMM-HIGH profile) and item 7 (71%+ hapax) were not achieved by that first attempt. At current evidence, the items that meaningfully discriminate sophisticated constructed systems from encoded natural language are items 5 and 7; the others do not, and earlier claims in this project that they did were overstated. See `results/constructed_control_results.json`.

Among the limited candidate classes implemented in the current pipeline — random generation, shuffled-token controls, simple substitution ciphers preserving source-language structure, and one first-pass synthetic constructed system — encoded structured language is the only tested class that satisfies all seven checklist items. This should be read as a constraint on tested models, not as exclusion of constructed, hybrid, stenographic, or unmodeled historical mechanisms; sophisticated constructed systems that engineer items 5 and 7 specifically have not been tested. Details in [docs/durable_findings.md](docs/durable_findings.md).

---

## Reproduction

```bash
pip install datasets scipy numpy pandas pyarrow

# One-command pipeline (recommended):
python run_all.py

# Or run individual scripts:
python scripts/00_validate_datasets.py   # Verify bundled data checksums
python scripts/01_core_analysis.py       # Transition rules, AIIN invariance
python scripts/02_cross_linguistic.py    # Cross-linguistic comparison
python scripts/03_stress_tests.py        # Robustness checks

# Verify canonical values match published numbers:
python run_all.py --tests
```

Raw data is bundled in this repository. Canonical values are verified by `tests/test_canonical_values.py` and a CI workflow runs validation on every push.

For a step-by-step reviewer-facing guide — environment, default pipeline, validation and tests, cross-transcription script, expected outputs, and known limitations — see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Cross-Transcription Reproducibility Note

The default pipeline in `run_all.py` reproduces the core analysis, comparator analysis, stress tests, extended analysis, paradigm null, cascade uncertainty, per-scribe analysis, and constructed-control results (`scripts/01`–`scripts/04`, `scripts/06`–`scripts/09`).

The cross-transcription analysis (`scripts/05_cross_transcription.py`) is **not** part of the default pipeline. It is run separately because it consumes a different input artifact — the LSI interlinear file `LSI_ivtff_0d.txt` (Landini & Zandbergen 1998, voynich.nu beta data) — which sits outside the AncientLanguages/Voynich Hugging Face dataset that the default pipeline depends on. The LSI file is bundled in this repository at [data/raw/voynich/LSI_ivtff_0d.txt](data/raw/voynich/LSI_ivtff_0d.txt) with provenance recorded in [data/manifests/source_notes.md](data/manifests/source_notes.md), and the precomputed analysis output is committed at [results/cross_transcription_results.json](results/cross_transcription_results.json).

To re-run the cross-transcription analysis from the bundled LSI file:

```bash
python scripts/05_cross_transcription.py
```

This separation prevents the default pipeline from claiming to reproduce an analysis whose input is sourced separately.

## Repository contents

```
run_all.py        One-command reproduction of the full pipeline (scripts 00–09)
scripts/          10 analysis scripts (validate, core, cross-linguistic, stress, extended,
                  cross-transcription, paradigm null, cascade uncertainty, per-scribe,
                  constructed control)
tests/            Canonical value regression tests (33 tests)
data/raw/         Frozen datasets (~308 MB, 21 entries with SHA-256 checksums)
data/manifests/   Dataset manifest (JSON), provenance records, source notes with full citations
results/          13 canonical output files (JSON + validation report)
dashboard/        Interactive HTML dashboard with 8 tabs including cross-transcription and MVE
docs/             Research paper (LaTeX + PDF), durable findings, release documentation,
                  paper revision notes
.github/          CI workflow (validates datasets + regression tests on every push)
index.html        Redirect to dashboard for GitHub Pages
```

## Data sources

- [AncientLanguages/Voynich](https://huggingface.co/datasets/AncientLanguages/Voynich) (Zandbergen-Landini transliteration)
- [Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/) (Wikipedia 100K editions)
- [Project Gutenberg](https://www.gutenberg.org/) (#22120 Middle English, #10900 KJV)
- [UD Ottoman Turkish](https://github.com/UniversalDependencies/UD_Ottoman_Turkish-DUDU) (DUDU treebank)
- Full provenance: [data/manifests/source_notes.md](data/manifests/source_notes.md)

## Corrections from earlier versions

| Earlier claim | Current status | Reason |
|---|---|---|
| Arabic is the closest match | Retired | Arabic is suffix-dominant (0.72); Voynich is symmetric (0.99) |
| Estonian SC = 1.35x, Finnish = 1.16x | Retired | False positives from 10K-sentence corpora |
| 15 languages compared | Corrected to 16 comparators + 3 pending + 1 control | Swahili, Georgian, Tagalog, Mandarin added across revisions |
| Self-clustering = 1.44x | Reported as range: 0.93x–1.45x | Method-sensitive |
| "Productive morphology" (Finding 1.8) | **Retired** | r = 0.42–0.71 does not exceed a character-trigram null that contains no morphology; Chaucer at the same definition produces r = 0.20. The edit-graph correlation is a combinatorial Zipfian property, not morphology. See `results/paradigm_null_results.json`. |
| "Only compatible class" phrasing in §5 | **Retired** | A first-pass synthetic constructed system (`09_constructed_control.py`) satisfies 5 of 7 checklist items by design. Items 1–4 and 6 do not discriminate NL from constructed systems. Only items 5 (bidirectional symmetry) and 7 (open vocabulary) currently distinguish them. |
| "Holds across both scribal hands" (transition rules) | Corrected | CHEDY→QOK is a property of Hands 2 and 3. Hand 1 shows the rule only at 1.42x on 13 observations; Hand 5 shows essentially no effect. See `results/per_scribe_results.json`. |

## Limitations

- **EVA-dependent for family definitions.** Token families (QOK, OK, OT, CHEDY, AIIN) are defined by EVA character strings. Bidirectional self-clustering has been tested across four alternative EVA-alphabet transcriptions (Currier, FSG, Takahashi, Grove) — all produce SYMM-HIGH, so the finding is not an artifact of the specific ZL tokenization. But non-EVA character-boundary systems have not been tested.
- **Tokenization-stability untested across disagreeing word boundaries.** The four transcriptions differ in word-boundary placement in many loci. A dedicated high-confidence-boundary analysis (restricting to tokens whose boundaries all transcriptions agree on) has not been performed.
- **Modern proxies.** Leipzig corpora are modern Wikipedia text, not medieval literature.
- **Ottoman Turkish corpus is small.** UD treebank (16,890 words) shows SYMM-LOW but a larger historical corpus would be preferable.
- **Method-sensitive self-clustering magnitude.** Self-clustering ranges from 0.93x to 1.45x by method. The prefix/suffix ratio (0.99) is stable.
- **"Grammar" is a weak statistical tendency, not predictive syntax.** Family-bigram prediction gives ~0% lift over baseline; 5-token history gives +3.6%. The patterns documented here are collocational preferences with class-level structure; they do not make the text predictable at the family level.
- **Constructed-system hypothesis tested only at one design point.** The single synthetic constructed control cannot rule out arbitrarily sophisticated constructed systems.
- **No decipherment.** Structure only, not semantics.

## What remains open

- High-confidence-boundary analysis across transcriptions (Currier/FSG/Takahashi/ZL agreement subset)
- Testing of non-EVA-alphabet character-boundary systems (FSG character set directly, not just FSG word boundaries)
- Ottoman Turkish comparison with a larger historical corpus
- Constructed language and cipher controls beyond the single first-pass generator (Enochian, Lingua Ignota digitized, Alberti-style polyalphabetic with bidirectional padding)
- Whether any natural language has bidirectional clustering symmetry (16 tested, none so far)
- Whether EVA families correspond to paleographic character boundaries
- Genre-matched structural comparison against medieval herbals, recipe texts, and medical formularies

## Preprint / Research Package

- **Title:** Voynich Manuscript Token-Structure Analysis: Reproducible Corpus Methods and Cross-Linguistic Baselines
- **Author:** Amy Laird (Independent Researcher)
- **Date:** May 2026
- **Status:** Preprint package prepared for external archival and submission.

**Description.** This paper presents a reproducible computational analysis of the Voynich Manuscript as a structured token system. It does not claim decipherment or translation. It tests line-bounded effects, token-family transition behavior, cross-linguistic comparator corpora, and stress tests against natural-language baselines.

### Files

- Manuscript PDF: [docs/paper.pdf](docs/paper.pdf) (canonical link, kept stable for GitHub Pages)
- Same PDF, dated filename: [docs/voynich-token-structure-analysis-2026-05.pdf](docs/voynich-token-structure-analysis-2026-05.pdf)
- LaTeX source: [docs/main.tex](docs/main.tex), [docs/main.bbl](docs/main.bbl), [docs/references.bib](docs/references.bib)
- Figures: [docs/figures/](docs/figures/)
- arXiv source bundle: [supplementary/arxiv_submission_v2.zip](supplementary/arxiv_submission_v2.zip)
- Bundle README: [docs/arxiv_submission_README.txt](docs/arxiv_submission_README.txt)
- Previous version: [docs/archive/paper_april_2026.pdf](docs/archive/paper_april_2026.pdf)

### External links

- GitHub Repository: <https://github.com/amy2213/Voynich-Transition-Grammar>
- GitHub Release: <https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v1.0.1-preprint>
- Project Dashboard: <https://amy2213.github.io/Voynich-Transition-Grammar/>
- Preprint PDF: <https://amy2213.github.io/Voynich-Transition-Grammar/docs/voynich-token-structure-analysis-2026-05.pdf>
- Zenodo archived release DOI: <https://doi.org/10.5281/zenodo.19996904>
- Zenodo latest-version DOI: <https://doi.org/10.5281/zenodo.19996905>
- OSF Preprint: pending
- arXiv: pending

## License

Code: MIT. Voynich Manuscript: Public domain. Leipzig Corpora: CC-BY. Gutenberg: Public domain. UD Ottoman Turkish: CC-BY-SA.

# Voynich Manuscript: Transition Grammar Analysis

The Voynich Manuscript is a 15th-century book that nobody can read. The script is unknown, the language (if it is a language) is unidentified, and every proposed decipherment has failed verification. This project doesn't try to decode it. Instead, it measures the statistical structure of the text and asks: what kind of system could have produced these patterns?

The answer is surprisingly specific. The text has grammatical rules that operate within lines and reset at line boundaries, morphological agreement between adjacent words where the ending of one word predicts the ending of the next, and a unique structural symmetry that no tested natural language shares. These properties together rule out random generation, simple ciphers, and template-based hoax mechanisms. The strongest remaining explanation is encoded structured language — plausibly natural language under a cipher that preserves the source system's grammar. The structural profile is consistent with a formulaic domain text (herbal, recipe, or medical collection), though this genre inference has not been tested against genre-matched comparison corpora.

**[Interactive Dashboard](https://amy2213.github.io/Voynich-Transition-Grammar/dashboard/voynich_dashboard.html)** · **[Research Paper (PDF)](https://amy2213.github.io/Voynich-Transition-Grammar/docs/paper.pdf)** · **[Durable Findings](docs/durable_findings.md)**

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

This matters because it constrains what the writing system can be. A simple letter-substitution cipher would preserve the source language's suffix dominance. Whatever produced Voynich operates on both word boundaries simultaneously — consistent with a syllabic or morpheme-level encoding.

---

## What else the analysis found

**Words follow grammatical rules.** One word family (CHEDY) attracts another (QOK) at 2.63x above chance, while a third family (AIIN) blocks QOK at 0.50x. These aren't fixed phrases — 77% of individual CHEDY-type words participate across 369 unique word pairs. The rules hold across every section of the manuscript, both scribal hands, and all line lengths.

**Lines are grammatical units.** The CHEDY→QOK attraction is 2.54x within a line but drops to 0.85x across line breaks. The grammar resets at every line boundary, suggesting each line is a clause or phrase, not arbitrary text wrapping. But word-family neighborhoods persist across lines — topics span multiple lines even though syntax doesn't.

**Adjacent words agree on their endings.** When one word ends in -dy, the next word is more likely to also end in -dy than chance predicts (1.18x–1.75x depending on family pair). This agreement compounds when you track multiple features simultaneously (suffix + length + mantle = 5–9x). The agreement cascades through chains of three or more words, with conditional lifts of 20–80 percentage points, and jumps over intervening function-like words.

**The morphology looks productive.** Each word family contains hub-centered networks of similar words (edit distance 1) where high-frequency stems have 2–3x more variants than low-frequency stems. The same four edit operations (prefix-like, stem-internal, suffix-like) recur across all manuscript sections while the specific vocabulary changes. This frequency-productivity correlation is consistent with productive morphology, though it has not yet been tested against a combinatorial null model (high-frequency strings may have more edit-distance-1 neighbors trivially).

**One word family behaves like a function word.** AIIN appears at exactly 15.0% of tokens in both Currier A and B language modes (KS p = 0.742). It doesn't cluster with itself. It's elevated at line beginnings. It passes other word families through but blocks QOK. This is consistent with a conjunction, article, or structural particle — something like "and" or "take" in a recipe text.

---

## What this does NOT claim

This project does not decode any text, identify any language, or assign meaning to any word. Structural similarity is not linguistic identification. The comparison set covers 16 languages but not every language type — Sinitic, polysynthetic, and historical shorthand systems are untested. The bidirectional symmetry does not prove the text is artificial; an untested natural language could have this property. All analysis uses the EVA transliteration, which may not correspond to the original script's character boundaries.

---

## Minimum viable explanation checklist

Any theory about the Voynich Manuscript — decipherment, hoax mechanism, or constructed language — must account for all eight of these properties simultaneously. Theories that explain some but not others are incomplete.

1. **Line-bounded grammar** — syntax resets at every line break
2. **Specific class attraction** — CHEDY attracts QOK specifically, not content words generally
3. **Suffix agreement** — adjacent words agree on ending class at 1.18–1.75x
4. **Agreement cascades** — feature matching propagates through 3-token chains
5. **Productive paradigms** — hub-centered morphological networks with frequency-correlated variant counts
6. **Bidirectional symmetry** — prefix/suffix clustering ratio of 0.99, unique among 18 tested systems (16 natural languages + 1 shuffled control + Voynich)
7. **Stable grammar, shifting vocabulary** — same rules across sections, but only 9–25% vocabulary overlap
8. **Open vocabulary** — 71.4% hapax, natural-like frequency distribution, not template-generated

Among the explanation classes tested with this pipeline (random generation, simple ciphers, template-based generation), encoded structured language is the only one compatible with all eight requirements. More sophisticated constructed systems remain untested and cannot be excluded. Details and scoring against alternative hypotheses in [docs/durable_findings.md](docs/durable_findings.md).

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

## Repository contents

```
run_all.py        One-command reproduction of the full pipeline
scripts/          6 analysis scripts (fetch, validate, core, cross-linguistic, stress, extended, cross-transcription)
tests/            Canonical value regression tests (27 tests)
data/raw/         Frozen datasets (~308 MB, 21 entries with SHA-256 checksums)
data/manifests/   Dataset manifest (JSON), provenance records, source notes with full citations
results/          9 canonical output files (JSON + validation report)
dashboard/        Interactive HTML dashboard with 8 tabs including cross-transcription and MVE
docs/             Research paper (LaTeX + PDF), durable findings, release documentation
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
| 15 languages compared | Corrected to 16 comparators + 3 pending + 1 control | Swahili added; earlier session used undocumented downloads |
| Self-clustering = 1.44x | Reported as range: 0.93x–1.45x | Method-sensitive |

## Limitations

- **EVA-dependent.** Family definitions may not map to real character units in the original script. FSG/Currier alphabets untested.
- **Modern proxies.** Leipzig corpora are Wikipedia text, not medieval literature.
- **Ottoman Turkish corpus is small.** UD treebank (16,890 words) shows SYMM-LOW but a larger historical corpus is needed.
- **Method-sensitive.** Self-clustering ranges from 0.93x to 1.45x by method. The prefix/suffix ratio (0.99) is stable.
- **Partial reproducibility.** Core findings (1.1–1.3) have scripted reproduction with regression tests. Newer findings (line structure, suffix agreement, cascades, paradigm morphology) are documented in durable_findings.md with methods and values but not yet packaged as standalone scripts.
- **No decipherment.** Structure only, not semantics.

## What remains open

- Cross-transcription validation under FSG/Currier alphabets
- Ottoman Turkish comparison with a larger historical corpus
- Constructed language and cipher controls (Enochian, Esperanto, Cardan grille)
- Whether any natural language has bidirectional clustering symmetry
- Whether EVA families correspond to paleographic character boundaries
- Genre-matched structural comparison against medieval herbals, recipe texts, and medical formularies

## License

Code: MIT. Voynich Manuscript: Public domain. Leipzig Corpora: CC-BY. Gutenberg: Public domain. UD Ottoman Turkish: CC-BY-SA.

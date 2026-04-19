# Voynich Manuscript: Transition Grammar Analysis

Statistical analysis of sequential word-group constraints in the Voynich Manuscript (Beinecke MS 408). Compares the manuscript's structural properties against 11 verified natural-language comparators and 1 shuffled-token control, identifying a bidirectional self-clustering signature unique among tested systems.

This project does not claim to identify the manuscript's language or decode its content.

https://amy2213.github.io/Voynich-Transition-Grammar/

## What Was Tested

We define five word families based on the EVA transliteration alphabet (QOK, OK, OT, CHEDY, AIIN) and measure how they follow each other across 31,608 tokens on 184 pages. We compare the same metrics — computed identically — against 9 modern-proxy languages (Leipzig Wikipedia 100K), 2 historical literary texts (Gutenberg), and 1 shuffled-token control.

## Three Strongest Findings

**1. Two distributed transition rules.** CHEDY→QOK attraction (2.63x above chance) and AIIN→QOK repulsion (0.50x, blocked). Both hold across all manuscript sections, scribal hands, line lengths, and random split-halves. They operate at the individual token level: 77% of CHEDY tokens participate across 369 unique token pairs. This is a class-level grammatical constraint, not fixed phrases.

**2. AIIN density is a structural constant.** The AIIN family appears at 15.0% of tokens in both Currier A and Currier B pages (KS p=0.742). It does not self-cluster. It passes other families through but blocks QOK. This behavior is consistent with a function-word role.

**3. Bidirectional self-clustering symmetry.** Voynich clusters equally by word-beginning (1.52x) and word-ending (1.54x), with a prefix/suffix ratio of 0.99. Every tested natural language with positive clustering is suffix-dominant. No tested system shares Voynich's balanced profile.

| System | Prefix SC | Suffix SC | Ratio | Type |
|---|---|---|---|---|
| **Voynich** | **1.52x** | **1.54x** | **0.99** | **Symmetric-High** |
| Arabic | 1.92x | 2.66x | 0.72 | Suffix-Dominant |
| Estonian | 0.96x | 2.33x | 0.41 | Suffix-Dominant |
| Finnish | 1.01x | 1.51x | 0.67 | Suffix-Dominant |
| Turkish | 0.91x | 0.98x | 0.92 | Symmetric-Low |
| Gibberish | 0.92x | 0.97x | 0.96 | Symmetric-Low |

Full table with all 13 systems in [results/prefix_suffix_analysis.json](results/prefix_suffix_analysis.json).

## What Is NOT Being Claimed

- No language is identified. Structural comparison is not language identification.
- No text is decoded. No word meanings are assigned.
- The "Arabic match" reported in earlier analysis has been retired. Arabic is suffix-dominant (ratio 0.72); Voynich is symmetric (ratio 0.99). The earlier finding was partially an artifact of measuring only prefix families.
- Bidirectional symmetry does not prove the text is artificial. An untested natural language could have this property.

## Corrections From Earlier Versions

| Earlier claim | Current status | Reason |
|---|---|---|
| Arabic is the closest match | Retired | Arabic is suffix-dominant; Voynich is symmetric |
| Estonian SC = 1.35x, Finnish = 1.16x | Retired | False positives from 10K-sentence corpora |
| 15 languages compared | Corrected to 11 verified comparators + 3 pending + 1 control | Earlier session used undocumented downloads |
| Self-clustering = 1.44x | Reported as range: 0.93x–1.45x | Method-sensitive |

## Limitations

- **EVA-dependent.** Family definitions may not map to real character units in the original script.
- **Modern proxies.** Leipzig corpora are Wikipedia text, not medieval literature.
- **Ottoman Turkish tested with small corpus.** UD treebank (16,890 words) shows SYMM-LOW (prefix 0.70x, suffix 1.04x). Not a match, but a larger historical corpus is needed for confirmation.
- **FSG/Currier alphabets untested.** Cross-transcription validation is incomplete.
- **No decipherment.** Structure only, not semantics.
- **Method-sensitive.** Self-clustering ranges from 0.93x to 1.45x by method. Prefix/suffix families are auto-detected.

## Reproduction

```bash
pip install datasets scipy numpy pandas pyarrow

python scripts/00_validate_datasets.py   # Verify bundled data checksums
python scripts/01_core_analysis.py       # Transition rules, AIIN invariance
python scripts/02_cross_linguistic.py    # Cross-linguistic comparison
python scripts/03_stress_tests.py        # Robustness checks
```

Run all scripts from the project root. Raw data is bundled in this repository. `scripts/00_fetch_datasets.py` is provided to rebuild or refresh datasets from source if needed, but is not required for reproduction.

## Repository Contents

```
scripts/          5 analysis scripts (fetch, validate, core, cross-linguistic, stress)
data/raw/         Frozen datasets: Voynich parquet, 9 Leipzig tarballs, 2 Gutenberg texts, 3 pending
data/manifests/   Provenance records, checksums, source notes
results/          6 canonical output files
dashboard/        Interactive dashboard (voynich_dashboard.html — open in any browser)
docs/             Paper and release documentation
```

## What Remains Open

- Cross-transcription validation under FSG/Currier alphabets
- Ottoman Turkish comparison with larger historical corpus
- Constructed language and cipher controls (Enochian, Esperanto, Cardan grille)
- Whether any natural language has bidirectional clustering symmetry
- Whether EVA families correspond to paleographic character boundaries

## Data Sources

- [AncientLanguages/Voynich](https://huggingface.co/datasets/AncientLanguages/Voynich) (Zandbergen-Landini transliteration)
- [Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/) (Wikipedia 100K editions)
- [Project Gutenberg](https://www.gutenberg.org/) (#22120 Middle English, #10900 KJV)
- Full provenance: [data/manifests/source_notes.md](data/manifests/source_notes.md)

## License

Code: MIT. Voynich Manuscript: Public domain. Leipzig Corpora: CC-BY. Gutenberg: Public domain.

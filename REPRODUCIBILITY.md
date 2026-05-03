# Reproducibility Guide

A concise guide for reviewers who want to reproduce the analyses and verify the canonical values published in the paper, README, and dashboard.

## Scope

The default pipeline reproduces the core analyses and JSON result files included in the repository package: transition rules, AIIN invariance, the cross-linguistic comparator analysis, stress tests, the extended analyses (findings 1.4–1.10), the paradigm-null test, cascade-uncertainty intervals with FDR correction, the per-scribe decomposition, and the first-pass constructed-system control. The cross-transcription analysis ([scripts/05_cross_transcription.py](scripts/05_cross_transcription.py)) is run separately — see [Cross-Transcription Analysis](#cross-transcription-analysis) below.

This project does **not** claim semantic decipherment or translation of the Voynich Manuscript. It reports reproducible structural regularities and defines falsifiable constraints that future explanations should address.

## Environment

CI runs on Python 3.11 (`ubuntu-latest`). Install dependencies with:

```bash
pip install -r requirements.txt
```

`requirements.txt` lists the core pipeline dependencies (`datasets`, `scipy`, `numpy`, `pandas`, `pyarrow`). Optional Mandarin segmentation packages (`jieba`, `pypinyin`) are commented out and only needed if the Mandarin Leipzig corpus is re-segmented from scratch — the precomputed Mandarin output is already in [results/cross_linguistic_results.json](results/cross_linguistic_results.json) and [results/prefix_suffix_analysis.json](results/prefix_suffix_analysis.json).

## Default Pipeline

```bash
python run_all.py --skip-validate
```

The default pipeline (orchestrated by [run_all.py](run_all.py)) executes these scripts in order:

| # | Script | Output |
|---|---|---|
| 0 | [scripts/00_validate_datasets.py](scripts/00_validate_datasets.py) — manifest checksum validation (run separately, see below) | (no output file) |
| 1 | [scripts/01_core_analysis.py](scripts/01_core_analysis.py) — transition rules, AIIN invariance, self-clustering | [results/core_analysis_results.json](results/core_analysis_results.json) |
| 2 | [scripts/02_cross_linguistic.py](scripts/02_cross_linguistic.py) — cross-linguistic comparison | [results/cross_linguistic_results.json](results/cross_linguistic_results.json) |
| 3 | [scripts/03_stress_tests.py](scripts/03_stress_tests.py) — definitional and section robustness | [results/stress_test_results.json](results/stress_test_results.json) |
| 4 | [scripts/04_extended_analysis.py](scripts/04_extended_analysis.py) — findings 1.4–1.10 | [results/extended_analysis_results.json](results/extended_analysis_results.json) |
| 6 | [scripts/06_paradigm_null.py](scripts/06_paradigm_null.py) — character-trigram null for Finding 1.8 | [results/paradigm_null_results.json](results/paradigm_null_results.json) |
| 7 | [scripts/07_cascade_uncertainty.py](scripts/07_cascade_uncertainty.py) — Wilson 95% CIs, BH-FDR on cascade chains | [results/cascade_uncertainty_results.json](results/cascade_uncertainty_results.json) |
| 8 | [scripts/08_per_scribe_analysis.py](scripts/08_per_scribe_analysis.py) — per-hand decomposition | [results/per_scribe_results.json](results/per_scribe_results.json) |
| 9 | [scripts/09_constructed_control.py](scripts/09_constructed_control.py) — synthetic constructed-system control | [results/constructed_control_results.json](results/constructed_control_results.json) |

Use `python run_all.py` (without `--skip-validate`) to also run the dataset checksum step at the start. The `--skip-validate` flag is the right choice for a reviewer who has already cloned cleanly and just wants to time the analysis pipeline.

`scripts/05_cross_transcription.py` is **not** part of this default pipeline; see the next section.

## Validation and Tests

Validate frozen-dataset SHA-256 checksums against the manifest:

```bash
python scripts/00_validate_datasets.py
```

Run the canonical-value regression suite (33 tests):

```bash
pytest tests/test_canonical_values.py -v
```

These tests guard against silent drift in canonical reported values. If the pipeline ever changes a published number by more than the documented tolerance, a test fails. See [tests/test_canonical_values.py](tests/test_canonical_values.py) for the full list of pinned values, sources, and tolerances.

The continuous-integration workflow at [.github/workflows/ci.yml](.github/workflows/ci.yml) runs both validation and the full pipeline-plus-tests on every push and pull request.

## Cross-Transcription Analysis

[scripts/05_cross_transcription.py](scripts/05_cross_transcription.py) is intentionally separate from `run_all.py` because it consumes a different input than the rest of the pipeline: the LSI interlinear file `LSI_ivtff_0d.txt` (Landini & Zandbergen 1998), sourced from voynich.nu rather than from the AncientLanguages/Voynich Hugging Face dataset that the default pipeline depends on.

The LSI file is bundled at [data/raw/voynich/LSI_ivtff_0d.txt](data/raw/voynich/LSI_ivtff_0d.txt) (provenance recorded in [data/manifests/source_notes.md](data/manifests/source_notes.md) and [data/manifests/dataset_manifest.json](data/manifests/dataset_manifest.json)), and a precomputed output is committed at [results/cross_transcription_results.json](results/cross_transcription_results.json). To regenerate the analysis from the bundled file:

```bash
python scripts/05_cross_transcription.py
```

This separation keeps the default pipeline's reproducibility claim narrow and verifiable; it does not exclude the cross-transcription analysis from the repository or hide it from reviewers.

## Data Sources and Byte Stability

- Frozen-dataset SHA-256 checksums are recorded in [data/manifests/dataset_manifest.json](data/manifests/dataset_manifest.json) and validated by [scripts/00_validate_datasets.py](scripts/00_validate_datasets.py).
- [.gitattributes](.gitattributes) declares `data/raw/** -text binary` so that Git's autocrlf cannot rewrite line endings on Windows checkouts. This freezes byte content across platforms; without it, Linux CI and Windows checkouts compute different SHA-256s for the same nominal data.
- Provenance for every comparator corpus (Leipzig Wikipedia 100K downloads, Project Gutenberg #22120 Chaucer, #10900 KJV, the UD Ottoman Turkish DUDU treebank, and the LSI IVTFF transcription file) is documented in [data/manifests/source_notes.md](data/manifests/source_notes.md), including a dated note on the EOL byte-stability refresh.

## Expected Outputs

After a successful pipeline run, expect:

- [results/](results/) — 13 canonical JSON result files plus `validation_report.txt`.
- [docs/paper.pdf](docs/paper.pdf) — the published manuscript (canonical link kept stable for GitHub Pages).
- [docs/voynich-token-structure-analysis-2026-05.pdf](docs/voynich-token-structure-analysis-2026-05.pdf) — same PDF with a dated filename (byte-identical to `docs/paper.pdf`).
- [dashboard/](dashboard/) — interactive HTML dashboard rendering the headline numbers.
- [tests/](tests/) — the 33-test regression suite that guards canonical values.

## Known Limitations

- **No decipherment or translation is claimed.** Findings describe statistical regularities only.
- **Sophisticated constructed systems are not excluded.** The first-pass constructed control satisfies 5 of 7 MVE checklist items by direct design. A tuned generator targeting items 5 (bidirectional SYMM-HIGH) and 7 (≥71% hapax) simultaneously has not been tested.
- **The comparator set is broad but not exhaustive.** 16 natural-language comparators across 9 language families plus 1 shuffled-token control. Polysynthetic languages at corpus scale and historical shorthand systems are untested. See [data/manifests/source_notes.md](data/manifests/source_notes.md) for the full list.
- **The constructed-system space remains underexplored.** Items 5 and 7 of the checklist currently do the discriminative work; items 1–4 and 6 can be produced by a designed system with moderate effort.
- **Run-to-run drift may occur in non-canonical exploratory outputs** (e.g. small `mean_degree` shifts from token-parsing variation), but every canonical claim is pinned to a specific value with a stated tolerance in [tests/test_canonical_values.py](tests/test_canonical_values.py); CI fails if any pinned value drifts beyond tolerance.
- **Cross-transcription analysis is run manually** (see above); only its precomputed output is verified against the manifest.

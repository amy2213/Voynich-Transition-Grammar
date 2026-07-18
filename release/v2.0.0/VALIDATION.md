# Version 2.0.0 validation

Validation date: 2026-07-18

## Preprint and bundle

The five-file source ZIP was extracted into a fresh temporary directory and
compiled with:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The build succeeded with 8 A4 pages, zero final LaTeX warnings, zero undefined
references, and zero overfull or underfull boxes. Extracted text matches
`docs/paper.pdf` exactly. Rasterization at 96 DPI produced eight
pixel-identical page pairs.

The ZIP contains exactly:

```text
README.txt
figures/prefix_suffix_v2.pdf
main.bbl
main.tex
references.bib
```

Bundle SHA-256:

```text
93b598dff8fdae6f591b99e6e866225a0abc170a4fa32c2914e35bd502a74308
```

File-level hashes are recorded in `manifest.json` and `SHA256SUMS`.

## Metadata

- `VERSION`, `CITATION.cff`, README, paper availability statement, release
  notes, bundle paths, and release tests identify Version `2.0.0`.
- `CITATION.cff` validates against the official CFF 1.2.0 JSON Schema.
- Version 1 release notes are preserved under
  `docs/archive/pre-v2-publication/RELEASE_NOTES_v1.md` and are explicitly not
  current authority.
- No Version 2 DOI is asserted before Zenodo ingestion.

## Canonical repository run

`python run_all.py` completed all five stages. Dataset validation, core
within-line analysis, classifier-overlap generation, the 200-replicate
prefix/suffix estimator, and the full test report each passed with fresh
outputs. Pytest and direct execution each collected and passed 37 tests with
zero failures; pytest also recorded zero errors, skips, and warnings. The
machine-readable evidence is in `results/run_manifest.json` and
`results/test_report.json`.

## Scientific interpretation

Build, hash, and regression checks demonstrate internal consistency and
reproducibility of the declared pipeline. They do not prove independence of
transition events, identify a language, establish natural-language
uniqueness, or generalize beyond the declared transcription, frozen corpora,
and methods.

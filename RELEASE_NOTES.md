# v1.0 — Transition Grammar with Bidirectional Self-Clustering Analysis

First public release of the Voynich Manuscript transition grammar analysis.

## Highlights

Statistical analysis of sequential word-family constraints in the Voynich
Manuscript (Beinecke MS 408), with three strongest findings:

1. **Two distributed transition rules** — CHEDY→QOK attraction at 2.63x above
   chance, AIIN→QOK repulsion at 0.50x. Both hold across all sections, scribal
   hands, line lengths, and random split-halves. Distributed across 77% of
   individual CHEDY tokens and 369 unique token pairs — a class-level
   grammatical constraint, not fixed phrases.

2. **AIIN density invariance** — The AIIN family appears at exactly 15.0% in
   both Currier A and Currier B pages (KS p = 0.742). Consistent with a
   function-word role, though the unusually high type count (842 unique forms)
   complicates that interpretation.

3. **Bidirectional self-clustering symmetry** — Voynich clusters equally at
   word beginnings (1.52x) and endings (1.54x), ratio 0.99. Every tested
   natural language with positive clustering is suffix-dominant. No tested
   system shares Voynich's balanced profile.

## What this release is not

- Not a decipherment. No word meanings are assigned.
- Not a language identification. Structural comparison ≠ language ID.
- Not a proof the manuscript is artificial. Symmetry is unusual but not
  exclusive to constructed systems.

## What's included

- **5 analysis scripts** (`scripts/`): fetch, validate, core analysis,
  cross-linguistic comparison, stress tests
- **6 canonical result files** (`results/`): transition rules, cross-linguistic
  comparison, stress tests, corpus-size sensitivity, prefix/suffix analysis,
  validation report
- **Frozen datasets** (~228 MB): Voynich parquet + 9 Leipzig comparators +
  2 Gutenberg literary texts + 3 pending + 1 Ottoman Turkish treebank,
  all with SHA-256 checksums
- **Research paper** (`docs/paper.pdf`, built from `docs/main.tex`)
- **Durable findings document** (`docs/durable_findings.md`) documenting 10
  numbered findings, caveats, retired claims, and the "minimum viable
  explanation" checklist any Voynich theory must satisfy
- **Release documentation** (`docs/release_documentation.md`) with a claim
  ledger distinguishing supported, retired, and untested claims
- **Interactive dashboard** (`dashboard/voynich_dashboard.html`)

## Quick start

```bash
pip install datasets scipy numpy pandas pyarrow
python scripts/00_validate_datasets.py   # Verify bundled data checksums
python scripts/01_core_analysis.py       # Core findings
python scripts/02_cross_linguistic.py    # Comparison across 11+1 systems
python scripts/03_stress_tests.py        # Robustness checks
```

## Live dashboard

https://amy2213.github.io/Voynich-Transition-Grammar/

## How to cite

See `CITATION.cff` for citation metadata. GitHub will render a "Cite this
repository" button on the repo page.

## Known limitations

All explicitly documented in `README.md § Limitations` and
`docs/release_documentation.md § 5`:

- EVA-transcription-dependent family definitions (FSG/Currier not tested)
- Modern comparison corpora (Leipzig Wikipedia), not medieval texts
- Self-clustering values method-sensitive (range 0.93x–1.45x)
- Ottoman Turkish tested with small UD corpus (16,890 words); larger
  historical corpus needed
- No semantic or decipherment analysis

## Suggested first issues for contributors

1. Cross-transcription validation — define equivalent token families under
   FSG/Currier alphabets and test whether findings hold
2. Ottoman Turkish with a larger historical corpus
3. Constructed language and cipher controls (Enochian, Cardan grille,
   polyalphabetic substitution)

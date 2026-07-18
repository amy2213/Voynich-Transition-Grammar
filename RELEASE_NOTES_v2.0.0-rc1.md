# Version 2.0.0 release candidate 1

Date: 2026-07-18

Status: release candidate on `v2-audit-consolidation`; not a final release.

## Scientific scope

This candidate reports reproducible corpus measurements of Voynich Manuscript
token structure. It does not claim decipherment, translation, semantic
identification, proof of natural or encoded language, or exclusion of
constructed, hybrid, stenographic, cipher, or other historical mechanisms.

## Canonical results in this candidate

- Within-line transition counts under the shared prefix-first EVA classifier.
- Raw-substring and canonical-family decomposition of Currier A/B AIIN
  density.
- Boundary-preserving, exactly size-matched prefix/suffix comparison against
  14 eligible frozen comparators using 200 declared replicates.
- Primary prefix/suffix means excluding `OTHER`, with inclusion reported as a
  sensitivity condition.
- Continuous estimates as primary results and a declared 27-cell threshold
  sensitivity grid as secondary evidence.

The exact values are generated in `results/`. The current paper is
`docs/paper.pdf`; generated results override prose if a conflict is found.

## Method changes from the May preprint

- Sequence adjacency is confined to natural line or sentence units.
- Removed ambiguous tokens break adjacency under strict exclusion.
- Voynich uncertainty uses page-block resampling while retaining lines.
- Comparators are repeatedly sampled without replacement to exactly 31,608
  tokens when eligible.
- Affix-family discovery is identical for Voynich and comparators.
- `OTHER` is excluded from the primary mean and retained as sensitivity.
- Monte Carlo estimates use corrected empirical values and the declared test
  family receives Benjamini-Hochberg adjustment.
- Input hashes, code hashes, estimator version, commands, and seeds are
  recorded in generated output.

## Retractions and limitations

The earlier 1.52/1.54/0.99 prefix/suffix result, natural-language uniqueness,
canonical AIIN invariance, five-to-ninefold feature compounding, all-five
cascade survival, independent non-EVA validation, and one-system seven-
criterion adversarial claim are not current findings. Historical material is
preserved in `docs/archive/` and `results/archive/`.

Matrix-wide cluster-aware transition inference, independent paleographic
transcriptions, genre-matched historical corpora, and sufficiently broad
generative controls remain open work.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python run_all.py
python scripts/23_build_preprint_bundle.py --build
```

The first command sequence regenerates the canonical analytical outputs and
runs the full suite through both supported test entry points. The final
command creates and independently compiles the self-contained preprint source
bundle under `release/v2.0.0-rc1/`.

## Publication identifiers

No DOI has been assigned to Version 2.0.0-rc1. The DOI associated with the May
Version 1 preprint must not be cited as the identifier for this candidate.

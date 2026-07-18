# Version 2.0.0

Release date: 2026-07-18

## Scientific scope

Version 2 reports reproducible corpus measurements of Voynich Manuscript token
structure. It does not claim decipherment, translation, semantic
identification, proof of natural or encoded language, or exclusion of
constructed, hybrid, stenographic, cipher, or other historical mechanisms.

## Canonical results

- Under the canonical prefix-first classifier and strictly within Voynich
  lines, CHEDY→QOK occurs 615 times at 2.659 times its independence
  expectation and AIIN→QOK occurs 127 times at 0.444 times expectation.
- Raw `aiin`/`ain` substring density has similar observed Currier A/B means,
  without an equivalence test. Canonical AIIN-family density differs between
  the groups.
- The boundary-preserving prefix/suffix estimator repeatedly matches eligible
  comparators to exactly 31,608 tokens and applies identical affix discovery
  to Voynich and comparator samples.
- Across 200 replicates, Voynich has median prefix self-clustering 1.333,
  suffix self-clustering 1.458, ratio 0.918, and minimum-side score 1.333.
- Including `OTHER` changes the medians to 1.292, 1.363, 0.951, and 1.291.
- Voynich exceeds each of 14 eligible frozen comparators on the continuous
  minimum-side score under this estimator. This finite-set result does not
  establish natural-language uniqueness.
- Ottoman Turkish is ineligible at 16,890 preserved tokens and is not padded.

Generated results under `results/` are canonical and override prose if a
conflict is found.

## Changes from Version 1

- Natural line, page, sentence, document, sample, bootstrap-block, and
  removed-token boundaries are preserved.
- Strict ambiguity exclusion breaks adjacency at each removed position.
- Voynich uses page-block resampling while retaining separate lines.
- Comparators use repeated sequence-unit sampling without replacement.
- Affix discovery is symmetrical across Voynich and comparators.
- `OTHER` is excluded from the primary mean and included as sensitivity.
- Monte Carlo estimates are corrected and multiplicity adjustment follows the
  declared hypothesis family.
- Current scripts share canonical parsing, classification, boundary,
  transition, sampling, seed, and statistical utilities.
- Historical results, papers, and retractions remain in labeled archives.

## Retired claims

The earlier 1.52/1.54/0.99 prefix/suffix result, natural-language uniqueness,
canonical AIIN invariance, five-to-ninefold feature compounding, all-five
cascade survival, independent non-EVA validation, and one-system seven-
criterion adversarial claim are not Version 2 findings.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python run_all.py
python scripts/23_build_preprint_bundle.py --build
```

The canonical pipeline regenerates current analytical outputs and runs the
full suite through pytest and direct Python execution. The bundle command
creates and independently compiles the final preprint sources under
`release/v2.0.0/`.

## Archival identifiers

The Version 2 release DOI will be assigned by Zenodo after the corresponding
GitHub release is ingested. Version 1 Zenodo identifiers do not identify this
release.

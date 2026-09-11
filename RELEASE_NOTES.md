# Version 2.0.0

Release date: 2026-09-11

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

- Version 2 DOI: `10.5281/zenodo.22715079`
- Concept DOI for all versions: `10.5281/zenodo.19996904`
- GitHub release: `https://github.com/amy2213/Voynich-Transition-Grammar/releases/tag/v2.0.0`
- Frozen scientific commit: `039acf4873104d7c8b60a3a5ff946667a8e0193c`

Zenodo identifies the v2.0.0 record as software, links it to the GitHub
`v2.0.0` release, and records the MIT license. The archived software record is
part of the same Zenodo version family as the historical Version 1 preprint.

## Post-release documentation correction

The released paper states that both test entry points collected and passed 34
tests. The frozen machine-readable test report records 37 pytest tests passed
and 37 direct-execution tests passed, with zero failures, errors, skips, or
warnings. The machine-readable test report is authoritative for test count.
This is a documentation-only discrepancy and does not alter any scientific
result, dataset, estimator, or release hash.

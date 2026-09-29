# Version 3.0.0

Release date: 2026-09-29

## Post-release scientific status: REOPENED

A post-release audit found that the Version 3.0.0 complete-line permutation
null treats line-initial and line-final Voynich positions as exchangeable.
Interior-only diagnostics change the full-corpus Voynich prefix/suffix ratios
from 1.013/1.108 to **0.933/1.053**, and an analytic fixed-endpoint
full-corpus diagnostic gives approximately **0.912/1.048**.

The cross-corpus comparator headline is also sensitive to the automatic affix
discovery thresholds. Under widened 1%–30% coverage, Arabic's weaker edge is
**1.010**, rather than below neutral.

The frozen Version 3.0.0 files remain reproducible. The prefix-neutral and
universal-comparator interpretations are reopened and will be replaced by a
Version 3.1 position-aware analysis.

The suffix signal remains the strongest surviving observation. Symmetric
subtraction of exact-repeat observed and expected contributions leaves the
suffix ratio at approximately **1.110**.

See `docs/v3/post_release_defect_2026-09-29.md`.


## Scientific change

Version 3.0.0 replaces the reopened Version 2 prefix/suffix estimator. The
release incorporates the original Version 3 repairs plus two pre-freeze
external-review corrections:

- comparator tokenization now breaks sequences at excluded or split lexical
  items instead of joining their surviving neighbors;
- Voynich neutrality is assessed with a page-block bootstrap rather than the
  highly overlapping 90% line-deletion interval.

The exact ordering null remains the within-unit expectation `k(k-1)/n`.
Suffix nesting is side-aware, alphabetic one-character comparator words are
retained, and cross-system replicate indices are never paired for a p-value.

## Corrected Version 3 result

Full-corpus Voynich:

- prefix 1.013;
- suffix 1.108.

Voynich page-block robustness, 200 replicates:

- prefix **1.020 [0.978, 1.064]**;
- suffix **1.110 [1.074, 1.145]**;
- minimum **1.020 [0.978, 1.064]**.

The prefix/minimum interval crosses neutral. The suffix interval remains above
neutral in all 200 page-block replicates.

In the 28,447-token sequence-unit deletion-stability analysis, all 14
sufficiently large comparators have their entire minimum-side 95% replicate
interval below 1.0. The Voynich 1.013 [1.005, 1.025] line-deletion interval is
reported only as stability information.

At the smaller 14,380-token all-system target, Voynich minimum is
1.019 [0.985, 1.060]. Arabic and Georgian minimum-side intervals cross neutral;
13/15 comparator intervals remain entirely below 1.0.

## Exact-repeat robustness

Voynich has 249 exact adjacent repeated-token pairs versus 244.274 expected
under the within-unit shuffle expectation. Breaking every such pair lowers the
suffix ratio to 1.064, so exact repetition contributes but does not fully
explain the suffix effect.

## Scope

These are finite-corpus robustness summaries under the declared transcription,
corpora, boundary-safe tokenization, discovery rules, and estimator. They do
not establish natural-language uniqueness, language identity, decipherment,
syntax, semantics, or a generating mechanism.

## Evidence

Committed evidence:

- `results/prefix_suffix_v3_validation.json`
- `results/prefix_suffix_v3_validation_audit.md`
- `results/prefix_suffix_v3_validation.sha256`

The frozen Version 2 tag, paper, DOI record, hashes, and release assets are not
rewritten.

---

# Version 2.0.0

Release date: 2026-09-11

## Post-release scientific status

On 2026-09-29 the Version 2 prefix/suffix cross-corpus claim was reopened after
a verified estimator defect. The frozen outputs remain reproducible, but the
pooled source/destination marginal expectation can confound within-unit order
with between-unit composition. A suffix-nesting implementation defect and the
cross-system replicate sign-test framing were also verified.

The frozen `v2.0.0` release, hashes, paper, and Zenodo artifact are unchanged.
Current authority records the defect in
`docs/v2/post_release_defect_2026-09-29.md`.

Version 3.0.0 was subsequently released and is now frozen historical evidence. Its cross-corpus headline was reopened after a later line-position and affix-threshold audit; see `docs/v3/post_release_defect_2026-09-29.md`.

## Scientific scope

Version 2 reports reproducible corpus measurements of Voynich Manuscript token
structure. It does not claim decipherment, translation, semantic
identification, proof of natural or encoded language, or exclusion of
constructed, hybrid, stenographic, cipher, or other historical mechanisms.

## Frozen release results

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

# Manuscript and public-claim alignment report

Status: Phase 3 current-prose alignment after approval of the locked Phase 2 estimator.

## Files reviewed

- `docs/main.tex`, read in full
- root `README.md`
- current Version 2 governance documents under `docs/v2/`
- the previously active arXiv README, durable-findings record, revision notes,
  and release documentation, now preserved under
  `docs/archive/pre-v2-publication/`

## Material corrections

| Prior public statement | Decision | Current treatment |
|---|---|---|
| Prefix SC 1.52, suffix SC 1.54, ratio 0.99 | Retired | Replaced by matched boundary-aware medians 1.333, 1.458, and 0.918 |
| Voynich is uniquely `SYMM-HIGH` among natural languages | Retired as a broad claim | Restricted to higher continuous minimum-side score than 14 eligible frozen comparators under estimator 2.0.0 |
| Sixteen natural-language comparators plus shuffled control support the headline | Incorrect for Version 2 | Fourteen eligible comparators; Ottoman Turkish is ineligible; Mandarin and shuffled control are not in the Version 2 estimator |
| Comparator corpora are scored at unequal or capped sizes | Retired method | Every eligible replicate is exactly 31,608 tokens |
| Token bootstrap supplies uncertainty | Retired method | Voynich page-block bootstrap and comparator natural-unit subsampling preserve nested sequence boundaries |
| Voynich uses hand-selected prefixes while comparators use discovery | Retired method | Identical discovery is applied to every side of every system and replicate |
| `OTHER` is part of the headline mean | Retired method | Primary excludes `OTHER`; inclusion is a required sensitivity condition |
| AIIN family density is invariant across Currier A/B | Rejected | Raw substring means are descriptively similar without equivalence testing; canonical family density differs |
| All five cascades survive corrected inference | Rejected | July record says four of five; clustered inference remains open |
| Multi-feature agreement compounds five to nine times | Rejected | Corrected permutation comparison is approximately 1.53 to 4.27 descriptively |
| Alternative EVA recodings establish non-EVA paleographic validation | Incorrect | Independent paleographic alphabets remain untested |
| One constructed control tests all seven criteria simultaneously | Incorrect | Historical controls test different subsets; no joint seven-item demonstration exists |
| The repository is publication-ready or its audit is closed | Retired | Current readiness is limited to the canonical pipeline and aligned manuscript on the audit branch |

## Paper scope after alignment

The revised manuscript reports only the canonical within-line core results,
the AIIN decomposition, and the Version 2 prefix/suffix estimator. Historical
exploratory analyses are discussed only as retractions or open work. The paper
does not infer decipherment, translation, language identity, natural-language
proof, encoded-language proof, or exclusion of untested mechanisms.

## Archived artifacts

The former `paper.pdf`, Word draft, May PDF, arXiv README, durable-findings
document, release documentation, revision notes, and obsolete figures were
moved to `docs/archive/pre-v2-publication/`. No published history was deleted
or rewritten in place.

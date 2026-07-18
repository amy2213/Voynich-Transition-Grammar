# Verified audit issue table

Verification date: 18 July 2026. “Fixed” means the implementation defect was
repaired and directly tested. It does not mean the associated scientific claim
is established.

| # | Decision | Exact evidence | Phase 1 disposition |
|---:|---|---|---|
| 1 | Confirmed | Untouched July overlay on the full repository: pytest collected 33, passed 32, failed `TestCascadeUncertainty::test_all_cascades_survive_fdr`; standalone overlay also lacks the retired prefix filename. | Stale assertions removed or rewritten; both runners now execute the same suite. |
| 2 | Confirmed | The package placed `unittest.main()` before later classes at historical `tests/test_canonical_values.py:294`. It is now the final executable statement at `tests/test_canonical_values.py:410`. | Fixed and verified by equal direct/pytest counts. |
| 3 | Confirmed | Historical tests pinned `prefix_suffix_analysis.json`, 0.99 symmetry, multiplied marginals, five cascades, per-scribe buckets, and first-pass control outcomes. | Retired assertions removed; current tests label provisional estimator checks descriptively. |
| 4 | Confirmed | Historical `strict=True` returned `AMBIGUOUS`, then counted that label as part of adjacency. Explicit policies now begin at `scripts/_canonical.py:115`; strict breaking is implemented by `build_class_sequences()` at line 308. | Fixed. Unit test proves removal creates no neighbour adjacency. |
| 5 | Confirmed | Generated `results/classifier_overlap_report.json`: 1,423 overlapping instances, 160 types, 4.5020%; precedence disagreement is 1,171 instances, 105 types, 3.7048%. The old 4,269/3.59% statement was impossible. | Fixed by generated arithmetic; historical statements archived. |
| 6 | Confirmed | `scripts/10_prefix_suffix_analysis.py:251` flattens Voynich lines; line 214 bootstraps arbitrary token blocks and joins them. | Open Phase 2 blocker. Output remains provisional. |
| 7 | Confirmed | Comparator point estimates use first-N truncation at `scripts/10_prefix_suffix_analysis.py:401-402`; intervals use a different first-50K slice at lines 418-422. | Open Phase 2 blocker. |
| 8 | Confirmed | Local self-clustering iterates over `set(classes)` at `scripts/10_prefix_suffix_analysis.py:180`; `OTHER` is not excluded. | Open Phase 2 blocker. Shared replacement defaults to excluding `OTHER` at `scripts/_canonical.py:400`. |
| 9 | Confirmed | Core permutations formerly flattened lines. Matrix tests still use Fisher/chi-square at `scripts/13_matrix_fdr.py:117-119`, treating overlapping transitions as independent observations. | Core fixed with within-line permutation at `scripts/01_core_analysis.py:116-131`; matrix inference remains open. |
| 10 | Confirmed | Both contiguous-block scripts sampled block two after concatenating the remainder. Shared original-order sampler is now `scripts/_canonical.py:464`; scripts 19 and 20 call it at lines 141 and 109. | Code fixed and unit-tested; affected results must be regenerated and old causal wording remains retired. |
| 11 | Confirmed | `scripts/15_boundary_validation.py:109-128` defines synthetic/adversarial schemes and a hand-built `currier_like` collapse, not independent paleographic alphabets. | Renamed in governance as synthetic segmentation sensitivity; actual non-EVA validation remains untested. |
| 12 | Confirmed | `scripts/14_adversarial_control.py:236` checks only items 5 and 7; line 273 measures a flattened generated sequence, while lines 323-327 generalize to all seven. | Claim narrowed. Joint seven-criterion system is not demonstrated. |
| 13 | Confirmed | Current and obsolete JSON, stale tests, “audit closed” prose, and historical analyses coexisted at equal directory depth. | Canonical hierarchy documented; obsolete results and July closure documents archived without deletion. |
| 14 | Confirmed | Paper examples: invariant AIIN at `docs/main.tex:63`, 0.99 at line 68, all five cascades at line 75, old table at line 603, independent transcribers at lines 680-700, and all-seven language claim at lines 1130-1131. | Paper intentionally unchanged in Phase 1; every conflict is recorded in the claim ledger. Root README corrected. |


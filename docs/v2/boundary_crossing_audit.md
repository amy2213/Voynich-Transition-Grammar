# Sequence-boundary audit

Canonical adjacency may not cross lines, pages, sections, hands, comparator
sentences/documents, resample blocks, subsample boundaries, or removed-token
seams. Explicitly named boundary analyses may calculate cross-boundary pairs.

| Script | Sequence construction | Boundary status | Canonical status |
|---|---|---|---|
| `01_core_analysis.py` | Shared line sequences; within-line permutation, page SC over separate lines, line-local chains and pairs | Repaired | Canonical |
| `02_cross_linguistic.py` | Flat comparator and Voynich token lists | Crosses natural units | Provisional |
| `03_stress_tests.py` | Section/length/half token concatenation | Crosses line joins | Provisional |
| `04_extended_analysis.py` | Mixed: explicit within/cross-line analysis plus several flattened downstream analyses | Mixed | Historical/exploratory |
| `05_cross_transcription.py` | Primary metrics flatten transcriber lines; separate within/cross calculation exists | Primary output crosses lines | Provisional |
| `06_paradigm_null.py` | Type/edit-graph analysis; no headline adjacency estimator | Not applicable to most outputs | Retired-finding support |
| `07_cascade_uncertainty.py` | Consumes counts derived upstream; overlapping triples clustered by line/type | Inference unit unresolved | Provisional |
| `08_per_scribe_analysis.py` | Extends token lists across all lines for each hand | Crosses lines/pages | Provisional |
| `09_constructed_control.py` | Generates lines but several measurements flatten them | Mixed | Historical control |
| `10_prefix_suffix_analysis.py` | Shared immutable units; Voynich page-block bootstrap retains lines; comparator sampling retains sentences/documents; final fragments remain separate | Repaired and tested | Canonical Version 2 estimator |
| `11_multifeature_permutation.py` | Collects adjacent pairs within each line | Boundary-preserving pairs; cluster inference unresolved | Exploratory |
| `archive/audit-2026-07/12_symmhigh_sensitivity.py` | Uses the old flattened estimator | Preserved historical blocker | Archived; superseded by script 10 generated threshold grid |
| `13_matrix_fdr.py` | Counts within lines | Boundary-preserving counts; independent-transition p-values invalid | Provisional |
| `14_adversarial_control.py` | Generates lines, then measures `flat(lines)` | Crosses generated line boundaries | Provisional control |
| `15_boundary_validation.py` | Iterates within each Voynich line | Boundary-preserving | Synthetic sensitivity only |
| `16_genre_comparators.py` | Flattens works/documents and uses script-10 estimator | Crosses document units | Provisional |
| `17_section_transition_structure.py` | Within-line matrices; line bootstrap | Boundary-preserving; multiplicity/confounding remain | Exploratory |
| `17b_section_bootstrap.py` | Within-line ratios; absolute paths and low replicate count | Boundary-preserving but nonportable | Archived-quality scratch analysis |
| `18_quire_boundaries.py` | Within-line cell counts; page grouping null is not fully matched | Adjacency preserved; grouping null limited | Retired claim support |
| `19_section_effect_null.py` | Within-line counts and repaired original-order disjoint blocks | Repaired | Retired claim support |
| `20_language_effect_null.py` | Within-line counts and repaired original-order disjoint blocks | Repaired; confounding/multiplicity remain | Provisional |

The shared strict-exclusion policy also breaks a sequence at each removed
ambiguous token. It never joins the token’s former neighbours.

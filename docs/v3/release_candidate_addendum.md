# Version 3 release-candidate addendum

Status: corrected pre-freeze addendum; final exact-head validation pending  
Date: 2026-09-29

## Purpose

This addendum records the correction path from frozen Version 2 to the
corrected Version 3.0.0 release candidate. Version 2 remains unchanged for
historical reproducibility.

## Corrections relative to Version 2

Version 3 now incorporates six material safeguards:

1. exact within-unit composition-conditioned expectation `k(k-1)/n`;
2. side-aware suffix nesting;
3. one-character comparator-token retention;
4. no arbitrary cross-system replicate-index sign test;
5. boundary-safe comparator tokenization that breaks at excluded or split
   lexical items instead of joining their neighbors;
6. page-block Voynich robustness for the cluster-aware neutrality statement.

## Corrected validation result

Full-corpus Voynich:

- prefix 1.013;
- suffix 1.108;
- minimum 1.013.

Voynich page-block bootstrap, 200 replicates:

- prefix **1.020 [0.978, 1.064]**;
- suffix **1.110 [1.074, 1.145]**;
- minimum **1.020 [0.978, 1.064]**.

The prefix/minimum interval crosses neutral. The suffix interval remains above
neutral in all 200 page-block replicates.

The 28,447-token sequence-unit deletion-stability analysis retains all 14
large comparator minimum-side intervals below 1.0 after the seam correction.
The old Voynich 199/200 line-deletion statement is retained only as stability
information and is not headline uncertainty evidence.

At the 14,380-token all-system target, Voynich minimum is
1.019 [0.985, 1.060]. Arabic and Georgian comparator minimum-side intervals
also cross neutral at this smaller target; 13/15 remain entirely below 1.0.

## Exact-repeat robustness

Voynich contains 249 exact adjacent repeated-token pairs versus 244.274 expected
under the within-line shuffle expectation. Breaking every such pair as a
sequence boundary reduces the suffix ratio from 1.108 to 1.064.

The suffix signal therefore is not solely an exact-repetition artifact, although
exact repeats contribute to its magnitude.

## Interpretation

The corrected Version 3 observation is not that Voynich is strongly
self-clustered on both token edges.

The supported statement is:

- prefix ordering is near neutral under page-level resampling;
- suffix ordering is modestly self-clustering;
- all tested comparator full-corpus minimum-side point estimates are below 1.0;
- all 14 sufficiently large comparator minimum-side intervals are below 1.0
  in the 28,447-token deletion-stability analysis;
- smaller-target sensitivity weakens interval separation.

No language identity, natural-language uniqueness, decipherment, semantic,
syntactic, or generating-mechanism inference follows.

## Evidence

Corrected run: `36624694412`  
Corrected validation artifact SHA-256:
`132ab897cb68a2d1ffe76c204000436761190939b0a4ea6aaca3d7a766fd1585`

Committed JSON SHA-256:
`ad89a8c3c1f887ba6b767069962f5f70226e4ef3b6949a86f58dc1b7ce28a2a3`

Committed audit SHA-256:
`07ad39d8a4fccbb75d4dfce1821c9df3993f11a6e5029851d9a296bda23a62f3`

Canonical compatibility run `36624694574` passed the complete frozen Version 2
pipeline and suite. Its canonical evidence artifact SHA-256 is
`3febe255027419722a452576ea5b06c80fb4458637d777001d62fa171665f944`.

The frozen Version 2 tag, paper, DOI record, hashes, and release assets remain
unchanged.

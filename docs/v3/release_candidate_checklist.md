# Version 3 release-candidate checklist

Status: corrected evidence complete; final exact-head release gates pending  
Opened: 2026-09-29

## Scientific method

- [x] Version 2 pooled-marginal confound formally recorded.
- [x] Version 2 suffix-nesting defect formally recorded.
- [x] One-character comparator token asymmetry corrected.
- [x] Comparator seams across excluded/split lexical items corrected.
- [x] Numeric-gap seam regression test.
- [x] Foreign-script-gap seam regression test.
- [x] Split-orthographic-form seam regression test.
- [x] Punctuation-wrapped valid-token regression test.
- [x] Arbitrary cross-system replicate-index sign test removed.
- [x] Exact within-unit composition-conditioned expectation implemented.
- [x] Page-block Voynich robustness added.
- [x] 90% Voynich line interval demoted to deletion stability.
- [x] Exact adjacent-repeat robustness added.

## Corrected validation

- [x] Corrected Python compilation passes.
- [x] Corrected Version 3 regression controls pass.
- [x] Corrected 200-replicate deletion-stability analysis completed.
- [x] Corrected 200-replicate Voynich page bootstrap completed.
- [x] Corrected 200-replicate all-system sensitivity completed.
- [x] Corrected mechanical audit passes.
- [x] Voynich page-block prefix/minimum 1.020 [0.978, 1.064].
- [x] Voynich page-block suffix 1.110 [1.074, 1.145].
- [x] Large-comparator minimum intervals below 1.0: 14/14.
- [x] Small-target Arabic and Georgian interval crossings disclosed.
- [x] Exact repeats: 249 observed, 244.274 expected, suffix-after-break 1.064.
- [x] No cross-system p-value generated.

## Evidence

- [x] Corrected JSON committed:
  `results/prefix_suffix_v3_validation.json`.
- [x] Corrected audit committed:
  `results/prefix_suffix_v3_validation_audit.md`.
- [x] Corrected evidence hashes committed.
- [x] Corrected validation artifact SHA-256 recorded.
- [x] Frozen input provenance retained.
- [x] 20-replicate smoke note explicitly marked superseded.
- [x] Pre-correction 200-replicate interpretation archived/superseded.

## Claim governance

- [x] Version 2 affix claim remains reopened/retired.
- [x] Corrected Version 3 claim ledger wording updated.
- [x] Prefix-above-neutral headline removed.
- [x] Page-block interval governs Voynich neutrality wording.
- [x] Exact-repeat wording uses independently reproduced numbers.
- [x] Finite-corpus and non-classifier scope explicit.
- [x] CHEDY->QOK / AIIN->QOK kept separate.

## Final release gates

- [ ] Final exact-head Version 3 validation passes after all claim/document
      updates.
- [ ] Final exact-head canonical compatibility passes after all claim/document
      updates.
- [ ] Final release evidence package rebuilt from that exact head.
- [ ] Release PR #10 marked ready only after the three gates above pass.
- [ ] `v3.0.0` tag created only by the guarded publish workflow.
- [ ] Version-specific archival DOI/version record verified after the final tag.
- [ ] Version 2 Zenodo description updated with a correction notice linking to
      the final Version 3 release.

## Frozen Version 2 protection

- [x] `v2.0.0` tag unchanged.
- [x] Version 2 GitHub release unchanged.
- [x] Version 2 Zenodo artifact unchanged.
- [x] Frozen Version 2 hashes remain historical evidence.

# Voynich Transition Grammar Project State

PROJECT: Voynich Transition Grammar
CURRENT VERSION: 3.0.0
CURRENT BRANCH: main
LAST VERIFIED SCIENTIFIC COMMIT: 039acf4873104d7c8b60a3a5ff946667a8e0193c
FROZEN RELEASE TAG: v2.0.0 -> 039acf4873104d7c8b60a3a5ff946667a8e0193c
CURRENT PHASE: corrected Version 3.0.0 evidence complete; final exact-head validation pending
AUTHORITATIVE ARTIFACT: Version 3.0.0 GitHub release/tag after final publish workflow succeeds; Version 2.0.0 remains frozen historical evidence with its Zenodo record

## Working
- Version 3 composition-controlled affix-order estimator passed its 200-replicate validation and mechanical audit on 2026-09-29.
- The 28,447-token sequence-unit deletion-stability analysis retains 14/14 large comparator minimum-side intervals below 1.0. The Voynich 90% line interval is stability-only, not cluster-aware uncertainty.
- Corrected Voynich page-block robustness: prefix/minimum 1.020 [0.978, 1.064], suffix 1.110 [1.074, 1.145]. Prefix/minimum crosses neutral; suffix remains above neutral.
- All 14 main comparators have their entire minimum-side 95% replicate interval below 1.0.
- The all-system 14,380-token sensitivity gives Voynich minimum 1.019 [0.985, 1.060]; Arabic and Georgian comparator minimum intervals also cross neutral at this smaller target.
- Version 3 reports no cross-system paired p-value; replicate indices have no linguistic pairing.
- Version 3 validation PR #6 merged to `main` at `67a2eb1b3cb86b75e509de94db685eba607799e4` after exact-head validation and ordinary canonical CI both passed.
- Corrected pre-freeze validation artifact SHA-256: `132ab897cb68a2d1ffe76c204000436761190939b0a4ea6aaca3d7a766fd1585`; committed JSON SHA-256: `ad89a8c3c1f887ba6b767069962f5f70226e4ef3b6949a86f58dc1b7ce28a2a3`.
- Final-head canonical evidence artifact SHA-256: `5c5db28982eac41a67644bd7732f40e85a56f91dafb39103b6a38799a564ad8c`.
- Verified release-candidate evidence ZIP SHA-256: `b6d496e05a8203bbddd1490f56de8ccacdd2e63d94e2d9763db6d8362a0b9875`.
- Durable release-candidate evidence is preserved in the ChatGPT Library at `/Voynich Transition Grammar/Voynich-v3-release-candidate-evidence.zip`.
- Version 2 scientific/code baseline is finalized and frozen at `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Canonical pipeline passed at that scientific commit.
- Finalization evidence records 37 pytest tests and 37 direct-execution tests passing.
- Public GitHub release `v2.0.0` was published on 2026-09-11.
- The public tag resolves exactly to the reviewed scientific commit.
- Release assets include the final arXiv source bundle, paper PDF, SHA256SUMS, `manifest.json`, and `VALIDATION.md`.
- Published ZIP and paper digests match the locked release checksums.
- Zenodo Version 2 is live as an open software record.
- Version DOI: `10.5281/zenodo.22715079`.
- Concept DOI: `10.5281/zenodo.19996904`.
- Zenodo shows version `v2.0.0`, creator Amy Laird with ORCID indicator, MIT license, and an external GitHub release relationship to `amy2213/Voynich-Transition-Grammar` release `v2.0.0`.
- Repository About text and GitHub release metadata were reconciled to bounded Version 2 language and the September 11, 2026 public release date.
- Clean canonical GitHub Actions run #53 completed successfully on documentation/control HEAD `ef66de6f624dd1baf3d16620c1a26eb5c0aab2d4`.
- That run preserved 37/37 pytest passes and 37/37 direct-execution passes with zero failures, errors, or skips.
- GitHub Actions artifact `canonical-run-evidence` digest: `sha256:5f5e6d75e31ebdcbdf99e42e160a1499e97897fb4da3f76e33bc451fdec3f365`.
- Final canonical-run evidence is durably preserved in Google Drive as `Voynich-v2.0.0-final-canonical-run-evidence.zip` (Drive file ID `1Cp-IM0cISpKPd5cnneSDMkxgIvZ3vLPC`).
- Durable release evidence is preserved in Google Drive as `Voynich-v2.0.0-release-evidence.zip` (Drive file ID `1XF6Vhd0Ybs7W_Ll-2F1YejKjYlRDuvZj`).
- The preserved release archive contains the source bundle, paper PDF, SHA256SUMS, manifest, validation record, release notes, and frozen tag target.
- `CITATION.cff`, current release notes, README, and the public dashboard point to Version 2 archival identifiers and scope.
- Version 1 preprint releases remain historical and must not be confused with Version 2.

## Known issues
- Verified 2026-09-29: the Version 2 prefix/suffix estimator pools source/destination marginals across natural units, so its headline self-clustering comparison can confound within-unit order with between-unit composition. The v2 cross-corpus claim is reopened; frozen artifacts remain unchanged.
- Verified 2026-09-29: Version 2 suffix discovery applies `startswith` nesting logic to suffixes, permitting nested candidates such as `dy/edy` and `in/iin`.
- Verified 2026-09-29: the Version 2 cross-system `p = 0.00995` sign-test framing pairs independently generated replicate distributions by index and is not retained as inferential evidence.
- Verified 2026-09-29: comparator tokenization dropped one-character words while canonical Voynich tokenization retained them. Version 3 retains one-character comparator words.
- The frozen released paper says both test entry points passed 34 tests, while the frozen machine-readable `results/test_report.json` records 37 pytest and 37 direct-execution tests passed. The machine-readable test report is authoritative. This is a documentation-only discrepancy and does not alter any scientific result, release tag, dataset, estimator, or artifact hash.
- The original May 2026 public dashboard contained retired claims. The live dashboard source on `main` has been replaced with a Version 2 authority page; the old content remains recoverable through repository history.

## Blockers
- None for Version 2 archival release.
- External-review corrections are implemented and independently validated: boundary-safe comparator tokenization, page-block Voynich robustness, and exact-repeat diagnostics. Corrected 200-replicate validation and frozen Version 2 compatibility both pass. Final claim/document updates and exact-head release validation remain.


## Final audit result
- DAT-40 final public release integrity audit: PASS on 2026-09-11.
- GitHub repository description: reconciled to bounded Version 2 scope.
- GitHub v2.0.0 release body: reconciled to public release date `2026-09-11`, Version DOI `10.5281/zenodo.22715079`, concept DOI `10.5281/zenodo.19996904`, frozen scientific commit, and the documented 34-vs-37 test-count discrepancy.
- Scientific baseline canonical pipeline: green on `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Final clean canonical rerun: green on documentation/control HEAD `ef66de6f624dd1baf3d16620c1a26eb5c0aab2d4`.
- Source bundle SHA-256: `93b598dff8fdae6f591b99e6e866225a0abc170a4fa32c2914e35bd502a74308`.
- Release paper SHA-256: `7b5f6497dd400589a0efa84fc746780ff457f6850626a7339a2e48a9261568ed`.
- Durable release evidence archive SHA-256: `69734d2024b8cfad5b83dca7915a8d5ef7be507937900f10f220b707a6c6d558`.
- Final canonical-run artifact SHA-256: `5f5e6d75e31ebdcbdf99e42e160a1499e97897fb4da3f76e33bc451fdec3f365`.
- Documentation/control commits after the frozen scientific tag do not replace the verified scientific commit in provenance records.

## Next action
Run final exact-head Version 3 validation and canonical compatibility after this claim/document update, rebuild the release evidence package, then mark PR #10 ready. Do not modify frozen Version 2 release assets.

## Source-of-truth rules
- Notion: portfolio state and release decisions
- Linear: archival-release gates and executable work
- GitHub: source, tests, CI, tags, releases
- Zenodo: public archival identifiers and version family
- Google Drive / ChatGPT Library: durable paper, bundle, hashes, and handoff artifacts

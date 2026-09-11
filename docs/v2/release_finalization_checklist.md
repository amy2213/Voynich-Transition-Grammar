# Version 2.0.0 finalization checklist

## Completed repository gates

- [x] Version 2 audit consolidation merged through reviewed PR #3.
- [x] Canonical pipeline passed locally and on GitHub Actions.
- [x] Pytest and direct execution each collected and passed 37 tests.
- [x] Current paper and README contain no promoted retired claims.
- [x] `CITATION.cff` passed the official CFF 1.2.0 schema.
- [x] Superseded root release notes were archived rather than overwritten
  without history.
- [x] Version, citation URLs, README, paper availability statement, tests, and
  release bundle were advanced from `2.0.0-rc1` to `2.0.0`.
- [x] Final preprint bundle compiled independently.
- [x] Final bundle inventory, hashes, build log, and manifest were generated.
- [x] Final Version 2 release evidence was preserved in the portfolio Drive
  layer and independently rechecked after download.

## GitHub and Zenodo gates

- [x] Merge the finalization PR to `main` after CI passes.
- [x] Create GitHub release tag `v2.0.0` from the reviewed scientific commit
  `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- [x] Attach the final source bundle, paper PDF, checksums, manifest, and
  validation record to the GitHub release.
- [x] Verify the published release assets against the locked release checksums.
- [ ] Confirm the repository is enabled in the Zenodo GitHub integration.
- [ ] Wait for Zenodo ingestion and record the version DOI and concept DOI.
- [ ] Add the assigned DOI to current citation and release metadata in a
  follow-up commit without rewriting the tagged release.
- [ ] Verify the Zenodo record title, creator, ORCID, version, license, files,
  related GitHub URL, and scientific scope before public handoff.
- [ ] Run the final public release integrity audit after DOI metadata is live.

## Current release evidence

- GitHub release: `v2.0.0`, published 2026-09-11.
- Frozen release tag target: `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Source bundle SHA-256:
  `93b598dff8fdae6f591b99e6e866225a0abc170a4fa32c2914e35bd502a74308`.
- Release paper SHA-256:
  `7b5f6497dd400589a0efa84fc746780ff457f6850626a7339a2e48a9261568ed`.
- Durable portfolio evidence archive:
  `Voynich-v2.0.0-release-evidence.zip`, Drive file ID
  `1XF6Vhd0Ybs7W_Ll-2F1YejKjYlRDuvZj`.
- Durable evidence archive SHA-256:
  `69734d2024b8cfad5b83dca7915a8d5ef7be507937900f10f220b707a6c6d558`.
- No Version 2 Zenodo DOI is recorded until Zenodo ingestion is independently
  confirmed.

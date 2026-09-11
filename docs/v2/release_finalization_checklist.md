# Version 2.0.0 finalization checklist

## Completed repository gates

- [x] Version 2 audit consolidation merged through reviewed PR #3.
- [x] Canonical pipeline passed locally and on GitHub Actions.
- [x] Pytest and direct execution each collected and passed 37 tests.
- [x] Current README contains no promoted retired claims.
- [x] `CITATION.cff` passed the official CFF 1.2.0 schema before release and has
  now been updated on `main` with the assigned Version 2 DOI.
- [x] Superseded root release notes were archived rather than overwritten
  without history.
- [x] Version, citation URLs, README, tests, and release bundle were advanced
  from `2.0.0-rc1` to `2.0.0`.
- [x] Final preprint bundle compiled independently.
- [x] Final bundle inventory, hashes, build log, and manifest were generated.
- [x] Final Version 2 release evidence was preserved in the portfolio Drive
  layer and independently rechecked after download.
- [x] Legacy public dashboard content containing retired May 2026 claims was
  replaced on `main` by a Version 2 authority page.

## GitHub and Zenodo gates

- [x] Merge the finalization PR to `main` after CI passes.
- [x] Create GitHub release tag `v2.0.0` from the reviewed scientific commit
  `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- [x] Attach the final source bundle, paper PDF, checksums, manifest, and
  validation record to the GitHub release.
- [x] Verify the published release assets against the locked release checksums.
- [x] Confirm Version 2 is live through the Zenodo GitHub integration.
- [x] Record the Version 2 DOI and concept DOI.
- [x] Add the assigned DOI to current citation and release metadata in a
  follow-up commit without rewriting the tagged release.
- [x] Verify the Zenodo record title, creator/ORCID indicator, version, MIT
  license, software type, external GitHub release relationship, and scientific
  scope from the live Version 2 record.
- [ ] Run and close the final public release integrity audit.

## Current release evidence

- GitHub release: `v2.0.0`, published 2026-09-11.
- Frozen release tag target: `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Version 2 DOI: `10.5281/zenodo.22715079`.
- Concept DOI: `10.5281/zenodo.19996904`.
- Zenodo resource type: Software.
- Zenodo access: Open.
- Zenodo license: MIT License.
- Zenodo external resource: GitHub repository release `v2.0.0`.
- Source bundle SHA-256:
  `93b598dff8fdae6f591b99e6e866225a0abc170a4fa32c2914e35bd502a74308`.
- Release paper SHA-256:
  `7b5f6497dd400589a0efa84fc746780ff457f6850626a7339a2e48a9261568ed`.
- Durable portfolio evidence archive:
  `Voynich-v2.0.0-release-evidence.zip`, Drive file ID
  `1XF6Vhd0Ybs7W_Ll-2F1YejKjYlRDuvZj`.
- Durable evidence archive SHA-256:
  `69734d2024b8cfad5b83dca7915a8d5ef7be507937900f10f220b707a6c6d558`.

## Recorded non-scientific discrepancy

The frozen release paper states that both test entry points passed 34 tests.
The frozen machine-readable `results/test_report.json` records 37 pytest tests
and 37 direct-execution tests passed, with zero failures. The machine-readable
report is authoritative for test count. This discrepancy is recorded rather
than silently rewriting the frozen release and does not affect scientific
results or artifact hashes.

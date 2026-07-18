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

## GitHub and Zenodo gates

- [ ] Merge the finalization PR to `main` after CI passes.
- [ ] Confirm the repository is enabled in the Zenodo GitHub integration.
- [ ] Create GitHub release tag `v2.0.0` from the reviewed `main` commit.
- [ ] Attach the final source bundle and paper PDF to the GitHub release.
- [ ] Wait for Zenodo ingestion and record the version DOI and concept DOI.
- [ ] Add the assigned DOI to current citation and release metadata in a
  follow-up commit without rewriting the tagged release.
- [ ] Verify the Zenodo record title, creator, ORCID, version, license, files,
  related GitHub URL, and scientific scope before public handoff.

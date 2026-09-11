# Voynich Transition Grammar Project State

PROJECT: Voynich Transition Grammar
CURRENT VERSION: 2.0.0
CURRENT BRANCH: main
LAST VERIFIED SCIENTIFIC COMMIT: 039acf4873104d7c8b60a3a5ff946667a8e0193c
FROZEN RELEASE TAG: v2.0.0 -> 039acf4873104d7c8b60a3a5ff946667a8e0193c
CURRENT PHASE: Version 2 archival release, Zenodo/DOI gate
AUTHORITATIVE ARTIFACT: GitHub v2.0.0 release and frozen scientific tag, with durable release evidence preserved in the portfolio Drive folder

## Working
- Version 2 scientific/code baseline is finalized and frozen at `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Canonical pipeline passed at that scientific commit.
- Finalization evidence records 37 pytest tests and 37 direct-execution tests passing.
- Public GitHub release `v2.0.0` was published on 2026-09-11.
- The public tag resolves exactly to the reviewed scientific commit.
- Release assets include the final arXiv source bundle, paper PDF, SHA256SUMS,
  `manifest.json`, and `VALIDATION.md`.
- Published ZIP and paper digests match the locked release checksums.
- Durable release evidence is preserved in Google Drive as
  `Voynich-v2.0.0-release-evidence.zip` (Drive file ID
  `1XF6Vhd0Ybs7W_Ll-2F1YejKjYlRDuvZj`).
- The preserved evidence archive contains the source bundle, paper PDF,
  SHA256SUMS, manifest, validation record, release notes, and frozen tag target.
- Version 1 preprint releases remain historical and must not be confused with Version 2.

## Known issues
- Zenodo Version 2 ingestion and DOI metadata are not yet confirmed.
- No Version 2 DOI may be asserted until the Zenodo record is live and verified.
- Final public release integrity audit remains blocked until Zenodo metadata is available.

## Blockers
- Archival release cannot be called complete until Zenodo Version 2 ingestion,
  DOI metadata verification, and the final public integrity audit are complete.

## Last test and release results
- Scientific baseline canonical pipeline: green on `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- 37 pytest tests passed.
- 37 direct-execution tests passed.
- GitHub release publisher workflow completed successfully on 2026-09-11.
- GitHub `v2.0.0` tag target independently re-read as `039acf4873104d7c8b60a3a5ff946667a8e0193c`.
- Source bundle SHA-256: `93b598dff8fdae6f591b99e6e866225a0abc170a4fa32c2914e35bd502a74308`.
- Release paper SHA-256: `7b5f6497dd400589a0efa84fc746780ff457f6850626a7339a2e48a9261568ed`.
- Durable evidence archive SHA-256: `69734d2024b8cfad5b83dca7915a8d5ef7be507937900f10f220b707a6c6d558`.
- The downloaded evidence archive was independently unpacked and its expected contents and inner source/paper hashes were rechecked before portfolio preservation.
- Documentation/control commits after the frozen scientific tag are not fresh scientific QA passes and must not replace the verified scientific commit in provenance records.

## Next action
Complete Linear DAT-39: confirm Zenodo ingestion of the exact GitHub `v2.0.0` release, record and verify the Version 2 DOI metadata, and add the assigned DOI in a follow-up metadata commit without rewriting the frozen release. Then complete DAT-40 final public release integrity audit.

## Source-of-truth rules
- Notion: portfolio state and release decisions
- Linear: archival-release gates and executable work
- GitHub: source, tests, CI, tags, releases
- Google Drive / ChatGPT Library: durable paper, bundle, hashes, and handoff artifacts

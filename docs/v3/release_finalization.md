# Version 3.0.0 release finalization

Status: approved for public release  
Approval date: 2026-09-29  
Release tag: `v3.0.0`

## Release boundary

Version 3.0.0 is a software, validation-evidence, and scientific-addendum
release. It does not rewrite the frozen Version 2 paper or Version 2 release
assets.

The release is created only after the exact merge commit passes:

1. Python source compilation;
2. Version 3 regression controls;
3. the complete 200-replicate Version 3 validation;
4. the Version 3 mechanical audit;
5. the declared numerical fingerprint check;
6. the complete frozen Version 2 canonical pipeline and test suite;
7. verification that `v2.0.0` still resolves to
   `039acf4873104d7c8b60a3a5ff946667a8e0193c`.

## Release assets

The publishing workflow packages:

- final Version 3 validation JSON;
- generated Version 3 audit report;
- Version 3 addendum;
- Version 3 interpretation;
- Version 3 provenance manifest;
- Version 2 post-release defect record;
- citation metadata;
- release notes;
- release validation record;
- file-level SHA-256 sums;
- a combined Version 3 evidence ZIP.

## Publication

The merge that adds `.release/v3.0.0-ready` triggers
`.github/workflows/publish-v3.0.0.yml`. The workflow creates the GitHub
`v3.0.0` tag and release only after every gate above succeeds.

The Zenodo concept DOI remains `10.5281/zenodo.19996904`. The
version-specific Version 3 DOI is recorded after archival ingestion and is not
invented in advance.

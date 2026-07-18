# Version 2 release-candidate checklist

Candidate: `2.0.0-rc1`

This checklist separates repository readiness from external publication.
Checking a repository item does not authorize merging, tagging, publishing a
GitHub release, minting a DOI, or submitting to a preprint service.

## Repository evidence

- [x] Version identifier is explicit and consistent.
- [x] Citation metadata names the current paper and does not reuse the May
  Version 1 release DOI.
- [x] `CITATION.cff` passes the official CFF 1.2.0 JSON Schema.
- [x] MIT software license is present.
- [x] Current paper source and rendered PDF are tracked.
- [x] Superseded publication artifacts are labeled and archived.
- [x] Canonical claim ledger records retained, narrowed, provisional, and
  retired analyses.
- [x] Full pipeline and both supported test entry points pass.
- [x] Machine-readable run and test evidence is tracked.

## Preprint bundle

- [x] Bundle contains only `main.tex`, `main.bbl`, `references.bib`, the
  required figure, and an explanatory README.
- [x] Bundle has no dependency on paths outside its source directory.
- [x] Bundle compiles independently with `latexmk` and `pdflatex`.
- [x] Produced PDF is byte-compared to `docs/paper.pdf` only as a diagnostic;
  visual and textual equivalence, not byte identity, is required.
- [x] SHA-256 checksums and a machine-readable release manifest are generated.
- [x] Generated ZIP contents and paths are tested.

## Scientific checks

- [x] Headline numerical claims are tested against generated canonical JSON.
- [x] Retired positive phrases are absent from current public claims.
- [x] Scope limitations are explicit in README, paper, and release notes.
- [x] `OTHER` inclusion is presented as sensitivity, not the primary mean.
- [x] Ottoman Turkish is reported as ineligible, not silently padded.
- [x] Comparator conclusion is limited to the frozen eligible set and method.

## External actions requiring separate approval

- [ ] Review author name, affiliation, email, ORCID, title, and abstract.
- [ ] Decide whether `2.0.0-rc1` should become final `2.0.0`.
- [ ] Merge the audited branch to `main`.
- [ ] Create and push a signed or annotated Git tag.
- [ ] Create a public GitHub release and upload release assets.
- [ ] Mint or update a DOI and then update `CITATION.cff`.
- [ ] Submit the source bundle to arXiv or another preprint service.

# Version 3 release-candidate provenance

Status: release-candidate evidence manifest  
Prepared: 2026-09-29  
Project: Voynich Transition Grammar

## Commit lineage

- Frozen Version 2 scientific tag: `v2.0.0`
- Frozen Version 2 scientific commit: `039acf4873104d7c8b60a3a5ff946667a8e0193c`
- Version 3 validation PR final head: `b8833f6b8714232bae2ceeebffbd6ee070432863`
- Version 3 validation PR: #6, `Validate Version 3 composition-controlled affix ordering`
- Version 3 validation merge commit on `main`: `67a2eb1b3cb86b75e509de94db685eba607799e4`

The validated estimator code did not change between the first successful
200-replicate audited validation at methodological head
`0e7daa64b544a22c8bbaccee6859186257c8a146` and PR final head
`b8833f6b8714232bae2ceeebffbd6ee070432863`. Commits after the methodological
head changed release-candidate documentation and workflow trigger metadata only.
The full 200-replicate validation was nevertheless rerun on the exact PR final
head and passed again.

## Final-head workflow evidence

### Version 3 scientific validation

- Workflow run: #7
- Run ID: `36614286293`
- Head SHA: `b8833f6b8714232bae2ceeebffbd6ee070432863`
- Result: success
- 200-replicate main matched analysis: success
- 200-replicate all-system small-target analysis: success
- Mechanical validation audit: success
- Artifact: `v3-validation-200-replicates`
- Artifact ID: `11054779129`
- Artifact SHA-256: `1b71a5a24d29452b588eb9de4fd48e05396f091d0968da13f523b775906d6720`
- Artifact contents:
  - `prefix_suffix_v3_validation.json`
  - `prefix_suffix_v3_validation_audit.md`

### Ordinary canonical repository CI

- Workflow run: #66
- Run ID: `36614286343`
- Head SHA: `b8833f6b8714232bae2ceeebffbd6ee070432863`
- Result: success
- Python compilation: success
- Version 3 regression controls: success
- Version 3 smoke analysis: success
- Full frozen Version 2 canonical pipeline and full suite: success
- Artifact: `canonical-run-evidence`
- Artifact ID: `11055321097`
- Artifact SHA-256: `5c5db28982eac41a67644bd7732f40e85a56f91dafb39103b6a38799a564ad8c`
- V3 smoke artifact: `v3-candidate-evidence`
- V3 smoke artifact ID: `11053674187`
- V3 smoke artifact SHA-256: `ce47c292e1dbb18f390f420ceec598da1c391b62487dacebdba77da67b495c5c`

## Version 3 validation parameters

- Estimator: `3.0.0-dev`
- Master seed: `20260929`
- Replicates per matched profile: 200
- Main matched target: 28,447 tokens
- Main matched systems: Voynich plus 14 sufficiently large comparators
- All-system small target: 14,380 tokens
- All-system systems: Voynich plus all 15 comparators, including Ottoman Turkish
- Cross-system replicate pairing: none
- Cross-system p-values: none

## Frozen input SHA-256 values

These hashes were emitted directly by the exact-head
`prefix_suffix_v3_validation.json` provenance block.

| Input | SHA-256 |
|---|---|
| `data/raw/cross_linguistic/arabic/ara_wikipedia_2021_100K.tar.gz` | `63248254c627e95409edc26e5be681372f8bdcde58bed33812f21bbf84527902` |
| `data/raw/cross_linguistic/estonian/ekk_wikipedia_2021_100K.tar.gz` | `c242c04a96099f547e9e3cfb8e880cd70cbcefd7bcc1ae340b831671807d0734` |
| `data/raw/cross_linguistic/finnish/fin_wikipedia_2021_100K.tar.gz` | `126263932396a53f89b32c1b881f6003a1420ffef126cedbb7c3419716b0ed10` |
| `data/raw/cross_linguistic/georgian/kat_wikipedia_2021_100K.tar.gz` | `9ae8e02b617a70d8667b2965a1f8d7acef6c43e433fd7c8d603431cd059f1e08` |
| `data/raw/cross_linguistic/hebrew/heb_wikipedia_2021_100K.tar.gz` | `ceeb63560a31278ba80d1380180c09012e003176dffb5b31ff886d40545706b2` |
| `data/raw/cross_linguistic/hungarian/hun_wikipedia_2021_100K.tar.gz` | `821d5f4b2fe2b667b3b025e7d61a32a2ee57c90c23c829b4f83c8806b3fd5997` |
| `data/raw/cross_linguistic/italian/ita_wikipedia_2021_100K.tar.gz` | `4fc8d1cf4133a5325020a3ba1c0b9211543719ad967eba6da5ce6a9ad4ce5ad6` |
| `data/raw/cross_linguistic/kjv_english/king_james_bible_10900.txt` | `954b7510414aaf3f9e2671ef457aae09e7ef0ac4f92e4117c76f8698d49b91e2` |
| `data/raw/cross_linguistic/latin/lat_wikipedia_2021_100K.tar.gz` | `a642cdd34384bea05c003664a30a54d4032978bcc73893a44d2d67ba9cc98844` |
| `data/raw/cross_linguistic/middle_english/chaucer_canterbury_tales_22120.txt` | `223770e4727bb8040fba39b32952cf8fdb33bb2ed17150c3d0820f6f17fbb37e` |
| `data/raw/cross_linguistic/north_azerbaijani/aze_wikipedia_2021_100K.tar.gz` | `e2da9da69013a73812a2a66d93de2b864e273c3f65c457a5d9e2cc445c2f8ee1` |
| `data/raw/cross_linguistic/ottoman_turkish/ota_dudu_test.conllu` | `d7d98be243d6640ccbd0b7c29419e8ea07bb212629b08eb9a0294d29addb5d80` |
| `data/raw/cross_linguistic/ottoman_turkish/ota_dudu_train.conllu` | `52ee97deb37c240bb142ec27fe19394470f3da2305837990394301ce4177ff66` |
| `data/raw/cross_linguistic/swahili/swa_wikipedia_2021_100K.tar.gz` | `05e41f4c58a27732bc223cac37155ee53b0b2e47c1815585428928456d7be1d5` |
| `data/raw/cross_linguistic/tagalog/tgl_wikipedia_2021_100K.tar.gz` | `6882246e886096936a501a7d181af803c16ea9cf1b06e687e55790add1407244` |
| `data/raw/cross_linguistic/turkish/tur_wikipedia_2021_100K.tar.gz` | `732122ae3d9bec3b9a9781d773825301705c1e84cd1f14e242a50855bb49e56c` |
| `data/raw/voynich/AncientLanguages_Voynich_snapshot/train.parquet` | `24c7bf7d0a999455825e75fefe5993faf8c3b7b9415923ff6b27c51eb297d759` |

## Validated numerical fingerprint

Exact-head validation reproduced the release-candidate values:

- Full-corpus Voynich: prefix 1.013, suffix 1.108, minimum 1.013.
- Main matched Voynich: prefix 1.013 [1.005, 1.025], suffix
  1.108 [1.099, 1.116], minimum 1.013 [1.005, 1.025].
- Main matched Voynich minimum at or above 1.0 in 199/200 replicates.
- Main matched comparator minimum-side intervals below 1.0: 14/14.
- All-system small-target Voynich: minimum 1.019 [0.985, 1.060].
- All-system small-target Voynich minimum at or above 1.0 in 170/200
  replicates.
- All-system comparator minimum-side intervals below 1.0: 15/15.

These are finite-corpus replicate summaries under the declared estimator and
sampling procedures. They are not population confidence intervals, a
natural-language classifier, a decipherment, or a language-identification
result.

## Release boundary

This manifest establishes release-candidate provenance only. It does not create
a Version 3 tag, change citation metadata, update a DOI record, or approve a
public Version 3 release. Those actions remain behind the explicit release
decision gate.

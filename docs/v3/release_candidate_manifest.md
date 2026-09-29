# Version 3 release-candidate provenance manifest

Status: corrected release candidate; final exact-head freeze pending  
Prepared: 2026-09-29

## Repository provenance

- Frozen Version 2 tag: `v2.0.0`
- Frozen Version 2 scientific commit:
  `039acf4873104d7c8b60a3a5ff946667a8e0193c`
- Version 2 DOI: `10.5281/zenodo.22715079`
- Version-family concept DOI: `10.5281/zenodo.19996904`
- Corrected Version 3 scientific-code/evidence run head:
  `cdbdc78f9887446b3b602349e22a4cfc30afc0f2`
- Corrected evidence commit:
  `0404fd32165123b8dd087ca64c0872747ab13675`
- Release PR: #10, intentionally draft until final exact-head validation

The corrected pre-freeze review added boundary-safe comparator tokenization,
Voynich page-block robustness, explicit line-deletion demotion, and
exact-repeat robustness. No Version 2 artifact changed.

## Final validation runs

### Corrected ordinary canonical compatibility

- Workflow: Canonical pipeline and tests
- Run ID: `36624694574`
- Head SHA: `cdbdc78f9887446b3b602349e22a4cfc30afc0f2`
- Result: success
- Version 3 seam/page regression controls: success
- Version 3 corrected smoke analysis: success
- Complete frozen Version 2 canonical pipeline and suite: success
- Canonical evidence artifact SHA-256:
  `3febe255027419722a452576ea5b06c80fb4458637d777001d62fa171665f944`

### Corrected dedicated Version 3 validation

- Workflow: Version 3 scientific validation
- Run ID: `36624694412`
- Head SHA: `cdbdc78f9887446b3b602349e22a4cfc30afc0f2`
- Result: success
- 200-replicate sequence-unit deletion stability: success
- 200-replicate Voynich page-block bootstrap: success
- 200-replicate all-system small-target sensitivity: success
- Mechanical audit: success
- Artifact ID: `11060002732`
- Artifact SHA-256:
  `132ab897cb68a2d1ffe76c204000436761190939b0a4ea6aaca3d7a766fd1585`
- Committed JSON SHA-256:
  `ad89a8c3c1f887ba6b767069962f5f70226e4ef3b6949a86f58dc1b7ce28a2a3`
- Committed audit SHA-256:
  `07ad39d8a4fccbb75d4dfce1821c9df3993f11a6e5029851d9a296bda23a62f3`

## Validation profiles

### Voynich page-block robustness

Target: 28,447 tokens; 200 page-block bootstrap replicates.

- prefix 1.020 [0.978, 1.064]
- suffix 1.110 [1.074, 1.145]
- minimum 1.020 [0.978, 1.064]
- prefix/minimum fraction >= 1.0: 0.770
- suffix fraction >= 1.0: 1.000

This is the cluster-aware Voynich robustness summary.

### Sequence-unit deletion stability

Target: 28,447 tokens; 200 without-replacement replicates.

- Voynich prefix 1.013 [1.005, 1.025]
- Voynich suffix 1.108 [1.099, 1.116]
- comparator minimum-side intervals entirely below 1.0: 14/14

The Voynich interval here is deletion stability only, not the cluster-aware
neutrality statement.

### All-system small-target sensitivity

Target: 14,380 tokens; all 16 systems.

- Voynich minimum 1.019 [0.985, 1.060]
- comparator minimum-side medians below 1.0: 15/15
- comparator minimum-side intervals entirely below 1.0: 13/15
- Arabic and Georgian minimum-side intervals cross neutral.

### Exact-repeat robustness

- observed exact adjacent repeats: 249
- within-unit shuffle expectation: 244.274
- suffix ratio after breaking each exact repeat pair: 1.064

## Frozen input SHA-256 values

No raw dataset file changed in the Version 3 validation PR. The estimator reads
the same frozen repository inputs, with the addition that Ottoman Turkish is
included in the all-system sensitivity rather than being excluded for size.

| Input | SHA-256 |
|---|---|
| `data/raw/voynich/AncientLanguages_Voynich_snapshot/train.parquet` | `24c7bf7d0a999455825e75fefe5993faf8c3b7b9415923ff6b27c51eb297d759` |
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

The generated Version 3 JSON records input hashes again at runtime. The table
above is the durable release-candidate reference for the frozen source files.

## Scientific authority

The current corrected Version 3 evidence supports a bounded finite-corpus
structural claim: Voynich suffix ordering remains modestly self-clustering under
page-level resampling, while prefix ordering is near neutral. The large
comparator set retains minimum-side anti-clustering in the declared
28,447-token deletion-stability analysis.

This does not establish natural-language uniqueness, language identity,
decipherment, semantics, syntax, or a generating mechanism.

No Version 3 tag or version-specific archival DOI exists until the final
exact-head release gates pass.

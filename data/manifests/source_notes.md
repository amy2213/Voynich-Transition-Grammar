# Dataset Source Notes

## Core Source

**AncientLanguages/Voynich** is the core dataset for all Voynich analysis. It is a Hugging Face dataset containing ~31,000 rows across 8 scholarly transliterations of the Voynich Manuscript. The underlying transliteration data comes from https://www.voynich.nu/data/. Our analysis uses only the Zandbergen-Landini transliteration in EVA (extended) alphabet.

## Historical/Literary Text Comparators

These are actual historical texts, not modern proxies:

- **Middle English (Chaucer):** Canterbury Tales from Project Gutenberg #22120. Labeled as Middle English by Gutenberg.
- **KJV English:** King James Bible from Project Gutenberg #10900. Early modern English (1611).

## Modern Proxy Comparators (Leipzig Corpora)

These are modern Wikipedia corpora from the Leipzig Corpora Collection. They are proxies for their respective languages, NOT historical literary equivalents. They should never be described as medieval or historical texts.

All Leipzig corpora use the Wikipedia 2021 100K edition when available:

| Language | File | Status | Notes |
|---|---|---|---|
| Turkish | tur_wikipedia_2021_100K | Verified | Modern Turkish, not Ottoman |
| Hungarian | hun_wikipedia_2021_100K | Verified | |
| Finnish | fin_wikipedia_2021_100K | Verified | |
| Hebrew | heb_wikipedia_2021_100K | Verified | Modern Hebrew, not Biblical |
| Arabic | ara_wikipedia_2021_100K | Verified | Modern Standard Arabic |
| Latin | lat_wikipedia_2021_100K | Verified | Wikipedia Latin, NOT historical Latin literature |
| North Azerbaijani | aze_wikipedia_2021_100K | Verified | |
| Italian | ita_wikipedia_2021_100K | Verified | Modern Italian, not medieval |
| Estonian | ekk_wikipedia_2021_100K | Verified | ISO 639-3 code 'ekk' |

## Pending / Unverified

These datasets were downloaded but require additional verification:

| Language | Status | Notes |
|---|---|---|
| Uzbek | Pending | Downloaded but not independently verified |
| Kazakh | Pending | Downloaded but not independently verified |
| Mongolian | Pending | Downloaded but not independently verified |

## Not Included / Not Verified

The following comparators were used during the research session but are NOT frozen in this repository:

| Language | Reason |
|---|---|
| Old French (Roman de la Rose) | Source was Project Gutenberg download during session, not frozen |
| Medieval Italian (Dante) | Source was Project Gutenberg download during session, not frozen |
| Latin (Caesar's Gallic Wars) | Source was CLTK GitHub during session, not frozen |

These would need a separate sourcing pass to include properly.

## Important Disclaimers

1. **Leipzig proxy corpora must not be described as historical literary equivalents.** Leipzig Latin is Wikipedia Latin, not Cicero. Leipzig Arabic is Modern Standard Arabic, not Classical Arabic.

2. **Ottoman Turkish is not tested.** All Turkish data is modern. 15th-century Ottoman Turkish had heavy Arabic/Persian loanword influence that could produce different structural metrics.

3. **Historical Latin, Old French, and historical Italian need a separate sourcing pass** using pinned literary sources (Project Gutenberg or CLTK) with proper provenance tracking.

## Useful Links

- Leipzig main downloads: https://wortschatz.uni-leipzig.de/en/download
- SAW Leipzig repository: https://repo.data.saw-leipzig.de/en
- SAW resources overview: https://repo.data.saw-leipzig.de/index.php/resources/en
- Voynich.nu data: https://www.voynich.nu/data/
- HuggingFace dataset: https://huggingface.co/datasets/AncientLanguages/Voynich

## Ottoman Turkish (UD Treebank)

**Ottoman Turkish (DUDU)** is a Universal Dependencies treebank containing 1,782 sentences from 14th–20th century texts in romanized Ottoman Turkish transcription alphabet. Downloaded from https://github.com/UniversalDependencies/UD_Ottoman_Turkish-DUDU. 16,890 words. Result: SYMM-LOW (prefix 0.70x, suffix 1.04x, ratio 0.67). Not a match for Voynich's symmetric-high profile. Small corpus — a larger historical Ottoman corpus would strengthen this result.

## Additional Comparators (Added April 2026)

### Swahili (Bantu)
- **Source:** Leipzig Corpora Collection, `swa_wikipedia_2021_100K`
- **URL:** https://downloads.wortschatz-leipzig.de/corpora/swa_wikipedia_2021_100K.tar.gz
- **License:** CC-BY
- **Tokens:** 1,593,683
- **Purpose:** Test whether rich bidirectional morphology (prefix subject/class agreement + suffix tense/aspect markers) produces SYMM-HIGH. Result: SYMM-LOW (prefix 0.79x, suffix 0.96x, ratio 0.82).
- **Citation:** D. Goldhahn, T. Eckart & U. Quasthoff: Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages. In: *Proceedings of LREC 2012*.

### Georgian (Kartvelian)
- **Source:** Leipzig Corpora Collection, `kat_wikipedia_2021_100K`
- **URL:** https://downloads.wortschatz-leipzig.de/corpora/kat_wikipedia_2021_100K.tar.gz
- **License:** CC-BY
- **Tokens:** 1,102,327
- **Purpose:** Test whether polypersonal agreement (prefix + suffix verb slots) produces SYMM-HIGH. Result: SYMM-LOW (prefix 0.98x, suffix 0.86x, ratio 1.14).
- **Citation:** Leipzig Corpora Collection (Goldhahn et al. 2012).

### Tagalog (Austronesian)
- **Source:** Leipzig Corpora Collection, `tgl_wikipedia_2021_100K`
- **URL:** https://downloads.wortschatz-leipzig.de/corpora/tgl_wikipedia_2021_100K.tar.gz
- **License:** CC-BY
- **Tokens:** 1,924,215
- **Purpose:** Test whether infixation + prefix/suffix morphology produces SYMM-HIGH. Result: SYMM-LOW (prefix 0.44x, suffix 0.41x, ratio 1.08).
- **Citation:** Leipzig Corpora Collection (Goldhahn et al. 2012).

### Mandarin Chinese (Sinitic)
- **Source:** Leipzig Corpora Collection, `cmn_wikipedia_2021_100K`
- **URL:** https://downloads.wortschatz-leipzig.de/corpora/cmn_wikipedia_2021_100K.tar.gz
- **License:** CC-BY
- **Tokens:** 327,791 (after jieba segmentation and Pinyin romanization of 20K sentences)
- **Purpose:** Test whether isolating morphology (no affixes) produces any self-clustering. Result: SYMM-LOW (prefix 0.82x, suffix 0.78x, ratio 1.04). Establishes the morphologically minimal floor.
- **Processing:** Chinese text segmented with jieba, converted to Pinyin with pypinyin. Each word-segmented unit treated as one token.
- **Citation:** Leipzig Corpora Collection (Goldhahn et al. 2012). Jieba: https://github.com/fxsjy/jieba. pypinyin: https://github.com/mozillazg/python-pinyin.

### LSI Interlinear File (Cross-Transcription Source)
- **Source:** voynich.nu (René Zandbergen), beta data directory
- **URL:** http://www.voynich.nu/data/beta/LSI_ivtff_0d.txt
- **License:** Public domain (Voynich Manuscript text)
- **Format:** IVTFF (Intermediate Voynich MS Transliteration File Format)
- **Contents:** Interlinear transcriptions by multiple scholars: Currier (C), First Study Group/Friedman (F), Takahashi (H), Grove (V), Tiltman (T), Latham (L), Kluge (K), Stolfi (U), and others. All mapped to EVA alphabet by J. Stolfi.
- **Purpose:** Cross-transcription stability validation. Tests whether bidirectional symmetry and transition rules are artifacts of ZL tokenization decisions.
- **Result:** All 4 major transcribers (C, F, H, V) independently produce SYMM-HIGH.
- **Citation:** Landini, G. & Zandbergen, R. (1998). INTERLN.EVT, European Voynich Manuscript Transcription project. Edited by J. Stolfi, release 1.6e6. Available at voynich.nu.

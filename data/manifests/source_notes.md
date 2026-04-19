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

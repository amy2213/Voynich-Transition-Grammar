#!/usr/bin/env python3
"""Version 3 composition-controlled prefix/suffix order estimator.

This is a new analysis path. It does not modify or overwrite the frozen
Version 2 release artifacts.
"""

import argparse
import hashlib
import json
import re
import sys
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from _canonical import (
    SequenceUnit,
    composition_controlled_affix_scores,
    load_corpus,
    sample_units_to_target,
    sequence_units,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
ESTIMATOR_VERSION = "3.0.0-dev"
DEFAULT_SEED = 20260929
DEFAULT_REPLICATES = 100
DISCOVERY = {
    "n_families": 5,
    "min_len": 2,
    "max_len": 3,
    "min_coverage": 0.02,
    "max_coverage": 0.20,
    "candidate_pool": 80,
    "min_n": 10,
}

LATIN = r"[a-z]+"
LEIPZIG = [
    ("Arabic", "arabic", "ara_wikipedia_2021_100K.tar.gz", r"[\u0621-\u064a]+", "Semitic"),
    ("Latin", "latin", "lat_wikipedia_2021_100K.tar.gz", LATIN, "Indo-European"),
    ("Estonian", "estonian", "ekk_wikipedia_2021_100K.tar.gz", r"[a-zõäöüšž]+", "Uralic"),
    ("Hebrew", "hebrew", "heb_wikipedia_2021_100K.tar.gz", r"[\u05d0-\u05ea]+", "Semitic"),
    ("Finnish", "finnish", "fin_wikipedia_2021_100K.tar.gz", r"[a-zäöå]+", "Uralic"),
    ("Hungarian", "hungarian", "hun_wikipedia_2021_100K.tar.gz", r"[a-záéíóöőúüű]+", "Uralic"),
    ("Turkish", "turkish", "tur_wikipedia_2021_100K.tar.gz", r"[a-zçğıöşü]+", "Turkic"),
    ("Italian", "italian", "ita_wikipedia_2021_100K.tar.gz", r"[a-zàèéìòù]+", "Indo-European"),
    ("North Azerbaijani", "north_azerbaijani", "aze_wikipedia_2021_100K.tar.gz", r"[a-zçəğıöşü]+", "Turkic"),
    ("Swahili", "swahili", "swa_wikipedia_2021_100K.tar.gz", LATIN, "Bantu"),
    ("Georgian", "georgian", "kat_wikipedia_2021_100K.tar.gz", r"[\u10d0-\u10f0]+", "Kartvelian"),
    ("Tagalog", "tagalog", "tgl_wikipedia_2021_100K.tar.gz", LATIN, "Austronesian"),
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenize(text, pattern):
    """Comparator tokenizer: retain alphabetic words including length 1."""
    return tuple(re.findall(pattern, text.lower()))


def load_leipzig(label, folder, archive, pattern):
    path = RAW / "cross_linguistic" / folder / archive
    units = []
    with tarfile.open(path, "r:gz") as bundle:
        member = next(item for item in bundle.getmembers()
                      if item.name.endswith("-sentences.txt"))
        handle = bundle.extractfile(member)
        if handle is None:
            raise RuntimeError(f"could not read {member.name}")
        for index, raw_line in enumerate(handle):
            line = raw_line.decode("utf-8", errors="ignore").rstrip("\n")
            sentence = line.split("\t", 1)[1] if "\t" in line else line
            tokens = tokenize(sentence, pattern)
            if tokens:
                units.append(SequenceUnit(
                    unit_id=f"{folder}:{index}", tokens=tokens,
                    boundary_type="sentence", document=archive))
    return units, [path]


def strip_gutenberg(text):
    start = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", text, re.I)
    if start:
        text = text[start.end():]
    end = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", text, re.I)
    if end:
        text = text[:end.start()]
    return text


def load_gutenberg(folder, filename):
    path = RAW / "cross_linguistic" / folder / filename
    text = strip_gutenberg(path.read_text(encoding="utf-8", errors="ignore"))
    units = []
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+|\n\s*\n", text)):
        tokens = tokenize(sentence, LATIN)
        if tokens:
            units.append(SequenceUnit(
                unit_id=f"{folder}:{index}", tokens=tokens,
                boundary_type="sentence", document=filename))
    return units, [path]


def load_conllu(folder, filenames):
    paths = [RAW / "cross_linguistic" / folder / name for name in filenames]
    units, sentence = [], []
    sentence_index = 0
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() + [""]:
            if not line.strip():
                if sentence:
                    units.append(SequenceUnit(
                        unit_id=f"{path.stem}:{sentence_index}",
                        tokens=tuple(sentence), boundary_type="sentence",
                        document=path.name))
                    sentence_index += 1
                    sentence = []
                continue
            if line.startswith("#") or "\t" not in line:
                continue
            fields = line.split("\t")
            if fields[0].isdigit():
                word = fields[1].lower()
                if word.isalpha():
                    sentence.append(word)
    return units, paths


def corpus_inventory():
    corpora = {}
    for label, folder, archive, pattern, family in LEIPZIG:
        units, paths = load_leipzig(label, folder, archive, pattern)
        corpora[label] = {
            "family": family, "units": units, "paths": paths,
            "source_type": "Leipzig sentence records",
        }
    for label, folder, filename in (
        ("Middle English", "middle_english", "chaucer_canterbury_tales_22120.txt"),
        ("KJV English", "kjv_english", "king_james_bible_10900.txt"),
    ):
        units, paths = load_gutenberg(folder, filename)
        corpora[label] = {
            "family": "Indo-European", "units": units, "paths": paths,
            "source_type": "Gutenberg sentence segments",
        }
    units, paths = load_conllu(
        "ottoman_turkish", ("ota_dudu_train.conllu", "ota_dudu_test.conllu"))
    corpora["Ottoman Turkish"] = {
        "family": "Turkic", "units": units, "paths": paths,
        "source_type": "CoNLL-U sentences",
    }
    return corpora


def compact_score(units):
    sequences = [unit.tokens for unit in units]
    score = composition_controlled_affix_scores(
        sequences, include_other=False, **DISCOVERY)
    return {
        "prefix_order_ratio": score["prefix"]["score"],
        "suffix_order_ratio": score["suffix"]["score"],
        "ratio": score["ratio"],
        "minimum_order_ratio": score["minimum"],
        "prefix_affixes": score["prefix"]["affixes"],
        "suffix_affixes": score["suffix"]["affixes"],
        "prefix_class_n": score["prefix"]["included_class_n"],
        "suffix_class_n": score["suffix"]["included_class_n"],
    }


def summarize(replicates, key):
    values = np.asarray([r[key] for r in replicates if r[key] is not None], dtype=float)
    return {
        "median": float(np.percentile(values, 50)),
        "ci95": [float(np.percentile(values, 2.5)),
                 float(np.percentile(values, 97.5))],
        "replicate_n": int(values.size),
    }


def system_summary(units, target_tokens, seeds):
    full = compact_score(units)
    reps = [
        compact_score(sample_units_to_target(
            units, target_tokens, np.random.default_rng(seed)))
        for seed in seeds
    ]
    return {
        "available_tokens": sum(len(unit.tokens) for unit in units),
        "natural_units": len(units),
        "full_corpus": full,
        "matched_subsample": {
            key: summarize(reps, key)
            for key in (
                "prefix_order_ratio",
                "suffix_order_ratio",
                "ratio",
                "minimum_order_ratio",
            )
        },
        "modal_prefix_affixes": list(
            Counter(tuple(r["prefix_affixes"]) for r in reps).most_common(1)[0][0]),
        "modal_suffix_affixes": list(
            Counter(tuple(r["suffix_affixes"]) for r in reps).most_common(1)[0][0]),
        "included_class_n_range": {
            "prefix": [min(r["prefix_class_n"] for r in reps),
                       max(r["prefix_class_n"] for r in reps)],
            "suffix": [min(r["suffix_class_n"] for r in reps),
                       max(r["suffix_class_n"] for r in reps)],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default="results/prefix_suffix_v3.json")
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")

    systems = {
        "VOYNICH": {
            "family": "Target system",
            "units": sequence_units(load_corpus()),
            "source_type": "Voynich lines",
            "paths": [Path(__import__("_canonical").PARQUET_PATH)],
        }
    }
    systems.update(corpus_inventory())

    available = {
        name: sum(len(unit.tokens) for unit in record["units"])
        for name, record in systems.items()
    }
    smallest = min(available.values())
    target_tokens = max(1000, int(smallest * 0.90))
    rng = np.random.default_rng(args.seed)
    seed_schedule = {
        name: rng.integers(0, 2**63 - 1, args.replicates).tolist()
        for name in sorted(systems)
    }

    summaries = {}
    input_paths = []
    for name in sorted(systems):
        record = systems[name]
        print(f"{name}: {available[name]} tokens, {len(record['units'])} units", flush=True)
        summaries[name] = {
            "family": record["family"],
            "boundary_unit": record["source_type"],
            **system_summary(record["units"], target_tokens, seed_schedule[name]),
        }
        input_paths.extend(record["paths"])

    payload = {
        "schema_version": "3.0-dev",
        "estimator_version": ESTIMATOR_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "research candidate; not a released scientific claim",
        "scope_warning": (
            "This estimator measures affix-class ordering relative to an exact "
            "within-unit permutation expectation. It does not establish "
            "decipherment, language identity, or mechanism."
        ),
        "method": {
            "full_corpus_primary": True,
            "matched_subsample_replicates": args.replicates,
            "matched_target_rule": "90% of the smallest available system token count",
            "matched_target_tokens": target_tokens,
            "sampling": "natural sequence units without replacement; final unit is one contiguous fragment",
            "ordering_null": "exact expected self-transitions under independent permutation within each natural sequence unit",
            "cross_system_p_values": "none",
            "comparator_min_token_length": 1,
            "suffix_nesting": "side-aware endswith logic",
            "discovery": DISCOVERY,
        },
        "systems": summaries,
        "provenance": {
            "master_seed": args.seed,
            "seed_schedule": seed_schedule,
            "input_sha256": {
                str(path.relative_to(ROOT)): sha256(path)
                for path in sorted(set(input_paths))
            },
        },
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    print("\nComposition-controlled order ratios (full corpus)")
    print("System\tPrefix\tSuffix\tMinimum")
    for name, record in summaries.items():
        full = record["full_corpus"]
        print(
            f"{name}\t{full['prefix_order_ratio']:.3f}\t"
            f"{full['suffix_order_ratio']:.3f}\t"
            f"{full['minimum_order_ratio']:.3f}"
        )
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(main())

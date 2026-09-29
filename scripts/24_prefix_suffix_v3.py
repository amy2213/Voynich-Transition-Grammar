#!/usr/bin/env python3
"""Version 3 composition-controlled prefix/suffix order estimator.

Version 3 isolates order from natural-unit composition by scoring observed
self-transitions against the exact expectation under independent permutation
within each line or sentence. It does not modify frozen Version 2 artifacts.

Validation reports three layers:
  1. full-corpus composition-controlled descriptive estimates;
  2. a main size-matched sensitivity excluding undersized Ottoman Turkish,
     targeted to 90% of the Voynich token count;
  3. an all-system small-target sensitivity including Ottoman Turkish,
     targeted to 90% of the smallest available corpus.

Replicate indices are never treated as matched linguistic observations and no
cross-system p-value is manufactured from them.
"""

import argparse
import hashlib
import json
import re
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
ESTIMATOR_VERSION = "3.0.0-dev"
DEFAULT_SEED = 20260929
DEFAULT_REPLICATES = 100
MAIN_MATCH_FRACTION = 0.90
ALL_SYSTEM_MATCH_FRACTION = 0.90
UNDERSIZED_SYSTEM = "Ottoman Turkish"

DISCOVERY = {
    "n_families": 5,
    "min_len": 2,
    "max_len": 3,
    "min_coverage": 0.02,
    "max_coverage": 0.20,
    "candidate_pool": 80,
    "min_n": 10,
    "nesting_mode": "side_aware",
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
                    unit_id=f"{folder}:{index}",
                    tokens=tokens,
                    boundary_type="sentence",
                    document=archive,
                ))
    return units, [path]


def strip_gutenberg(text):
    start = re.search(
        r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*",
        text,
        re.I,
    )
    if start:
        text = text[start.end():]
    end = re.search(
        r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*",
        text,
        re.I,
    )
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
                unit_id=f"{folder}:{index}",
                tokens=tokens,
                boundary_type="sentence",
                document=filename,
            ))
    return units, [path]


def load_conllu(folder, filenames):
    paths = [RAW / "cross_linguistic" / folder / name for name in filenames]
    units = []
    sentence = []
    sentence_index = 0
    for path in paths:
        lines = path.read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines() + [""]
        for line in lines:
            if not line.strip():
                if sentence:
                    units.append(SequenceUnit(
                        unit_id=f"{path.stem}:{sentence_index}",
                        tokens=tuple(sentence),
                        boundary_type="sentence",
                        document=path.name,
                    ))
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
            "family": family,
            "units": units,
            "paths": paths,
            "source_type": "Leipzig sentence records",
        }

    for label, folder, filename in (
        ("Middle English", "middle_english", "chaucer_canterbury_tales_22120.txt"),
        ("KJV English", "kjv_english", "king_james_bible_10900.txt"),
    ):
        units, paths = load_gutenberg(folder, filename)
        corpora[label] = {
            "family": "Indo-European",
            "units": units,
            "paths": paths,
            "source_type": "Gutenberg sentence segments",
        }

    units, paths = load_conllu(
        "ottoman_turkish",
        ("ota_dudu_train.conllu", "ota_dudu_test.conllu"),
    )
    corpora[UNDERSIZED_SYSTEM] = {
        "family": "Turkic",
        "units": units,
        "paths": paths,
        "source_type": "CoNLL-U sentences",
    }
    return corpora


def compact_score(units):
    sequences = [unit.tokens for unit in units]
    score = composition_controlled_affix_scores(
        sequences,
        include_other=False,
        **DISCOVERY,
    )
    return {
        "prefix_order_ratio": score["prefix"]["score"],
        "suffix_order_ratio": score["suffix"]["score"],
        "minimum_order_ratio": score["minimum"],
        "prefix_to_suffix_ratio": score["ratio"],
        "prefix_unweighted_mean_class_ratio": (
            score["prefix"]["unweighted_mean_class_ratio"]
        ),
        "suffix_unweighted_mean_class_ratio": (
            score["suffix"]["unweighted_mean_class_ratio"]
        ),
        "prefix_affixes": score["prefix"]["affixes"],
        "suffix_affixes": score["suffix"]["affixes"],
        "prefix_class_n": score["prefix"]["included_class_n"],
        "suffix_class_n": score["suffix"]["included_class_n"],
    }


def summarize_values(replicates, key, neutral=None):
    values = np.asarray(
        [record[key] for record in replicates if record[key] is not None],
        dtype=float,
    )
    if values.size == 0:
        return {
            "median": None,
            "ci95": [None, None],
            "replicate_n": 0,
        }

    summary = {
        "median": float(np.percentile(values, 50)),
        "ci95": [
            float(np.percentile(values, 2.5)),
            float(np.percentile(values, 97.5)),
        ],
        "q05_q95": [
            float(np.percentile(values, 5)),
            float(np.percentile(values, 95)),
        ],
        "replicate_n": int(values.size),
    }
    if neutral is not None:
        summary["neutral_value"] = float(neutral)
        summary["fraction_below_neutral"] = float(np.mean(values < neutral))
        summary["fraction_at_or_above_neutral"] = float(
            np.mean(values >= neutral)
        )
    return summary


def summarize_replicates(replicates):
    return {
        "prefix_order_ratio": summarize_values(
            replicates, "prefix_order_ratio", neutral=1.0
        ),
        "suffix_order_ratio": summarize_values(
            replicates, "suffix_order_ratio", neutral=1.0
        ),
        "minimum_order_ratio": summarize_values(
            replicates, "minimum_order_ratio", neutral=1.0
        ),
        "prefix_to_suffix_ratio": summarize_values(
            replicates, "prefix_to_suffix_ratio", neutral=1.0
        ),
        "prefix_unweighted_mean_class_ratio": summarize_values(
            replicates,
            "prefix_unweighted_mean_class_ratio",
            neutral=1.0,
        ),
        "suffix_unweighted_mean_class_ratio": summarize_values(
            replicates,
            "suffix_unweighted_mean_class_ratio",
            neutral=1.0,
        ),
        "modal_prefix_affixes": list(
            Counter(
                tuple(record["prefix_affixes"])
                for record in replicates
            ).most_common(1)[0][0]
        ),
        "modal_suffix_affixes": list(
            Counter(
                tuple(record["suffix_affixes"])
                for record in replicates
            ).most_common(1)[0][0]
        ),
        "included_class_n_range": {
            "prefix": [
                min(record["prefix_class_n"] for record in replicates),
                max(record["prefix_class_n"] for record in replicates),
            ],
            "suffix": [
                min(record["suffix_class_n"] for record in replicates),
                max(record["suffix_class_n"] for record in replicates),
            ],
        },
    }


def build_seed_schedule(system_names, profile_name, master_seed, replicates):
    profile_offset = int.from_bytes(
        hashlib.sha256(profile_name.encode("utf-8")).digest()[:8],
        "big",
    )
    rng = np.random.default_rng(
        np.uint64(master_seed) ^ np.uint64(profile_offset)
    )
    return {
        name: rng.integers(0, 2**63 - 1, replicates).tolist()
        for name in sorted(system_names)
    }


def run_matched_profile(
        systems,
        system_names,
        target_tokens,
        replicates,
        master_seed,
        profile_name):
    seed_schedule = build_seed_schedule(
        system_names,
        profile_name,
        master_seed,
        replicates,
    )
    results = {}

    for name in sorted(system_names):
        units = systems[name]["units"]
        available = sum(len(unit.tokens) for unit in units)
        if available < target_tokens:
            raise ValueError(
                f"{profile_name}: {name} has {available} tokens, "
                f"below target {target_tokens}"
            )

        sampled = []
        for index, seed in enumerate(seed_schedule[name], start=1):
            sample = sample_units_to_target(
                units,
                target_tokens,
                np.random.default_rng(seed),
            )
            sampled.append(compact_score(sample))
            if index % 25 == 0 or index == replicates:
                print(
                    f"  {profile_name}: {name} {index}/{replicates}",
                    flush=True,
                )

        results[name] = {
            "available_tokens": available,
            "summary": summarize_replicates(sampled),
            "replicates": sampled,
        }

    return {
        "profile": profile_name,
        "target_tokens": target_tokens,
        "replicate_n": replicates,
        "systems": results,
        "seed_schedule": seed_schedule,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replicates",
        type=int,
        default=DEFAULT_REPLICATES,
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--out",
        default="results/prefix_suffix_v3.json",
    )
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

    full_corpus = {}
    input_paths = []
    for name in sorted(systems):
        record = systems[name]
        print(
            f"{name}: {available[name]} tokens, "
            f"{len(record['units'])} units",
            flush=True,
        )
        full_corpus[name] = {
            "family": record["family"],
            "boundary_unit": record["source_type"],
            "available_tokens": available[name],
            "natural_units": len(record["units"]),
            "score": compact_score(record["units"]),
        }
        input_paths.extend(record["paths"])

    main_systems = [
        name for name in sorted(systems)
        if name != UNDERSIZED_SYSTEM
    ]
    main_target = int(
        available["VOYNICH"] * MAIN_MATCH_FRACTION
    )
    all_system_target = int(
        min(available.values()) * ALL_SYSTEM_MATCH_FRACTION
    )

    print(
        f"\nMain matched sensitivity: {main_target} tokens, "
        f"{len(main_systems)} systems, Ottoman Turkish excluded",
        flush=True,
    )
    main_matched = run_matched_profile(
        systems=systems,
        system_names=main_systems,
        target_tokens=main_target,
        replicates=args.replicates,
        master_seed=args.seed,
        profile_name="main_matched_excluding_undersized_ottoman",
    )

    print(
        f"\nAll-system small-target sensitivity: "
        f"{all_system_target} tokens, {len(systems)} systems",
        flush=True,
    )
    all_system_small = run_matched_profile(
        systems=systems,
        system_names=sorted(systems),
        target_tokens=all_system_target,
        replicates=args.replicates,
        master_seed=args.seed,
        profile_name="all_system_small_target",
    )

    payload = {
        "schema_version": "3.1-dev",
        "estimator_version": ESTIMATOR_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "validation candidate; not a released scientific claim",
        "scope_warning": (
            "This estimator measures affix-class ordering relative to an "
            "exact within-unit permutation expectation. It does not establish "
            "natural-language uniqueness, decipherment, language identity, "
            "or a generating mechanism."
        ),
        "method": {
            "full_corpus_primary": True,
            "matched_subsample_replicates": args.replicates,
            "main_matched": {
                "systems": main_systems,
                "excluded_system": UNDERSIZED_SYSTEM,
                "target_rule": (
                    f"{MAIN_MATCH_FRACTION:.0%} of canonical Voynich token count"
                ),
                "target_tokens": main_target,
            },
            "all_system_small_target": {
                "systems": sorted(systems),
                "target_rule": (
                    f"{ALL_SYSTEM_MATCH_FRACTION:.0%} of the smallest "
                    "available system token count"
                ),
                "target_tokens": all_system_target,
            },
            "sampling": (
                "natural sequence units without replacement; final unit is "
                "one contiguous fragment"
            ),
            "ordering_null": (
                "exact expected self-transitions under independent "
                "permutation within each natural sequence unit"
            ),
            "cross_system_p_values": "none",
            "replicate_pairing": "none; indices have no cross-system meaning",
            "comparator_min_token_length": 1,
            "suffix_nesting": "side-aware endswith logic",
            "primary_side_score": (
                "aggregate observed self-transitions divided by aggregate "
                "composition-conditioned expectation over supported classes"
            ),
            "unweighted_class_mean": "reported as sensitivity only",
            "discovery": DISCOVERY,
        },
        "full_corpus": full_corpus,
        "matched_analyses": {
            "main": main_matched,
            "all_system_small_target": all_system_small,
        },
        "provenance": {
            "master_seed": args.seed,
            "input_sha256": {
                str(path.relative_to(ROOT)): sha256(path)
                for path in sorted(set(input_paths))
            },
        },
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\nComposition-controlled order ratios (full corpus)")
    print("System\tPrefix\tSuffix\tMinimum")
    for name, record in full_corpus.items():
        score = record["score"]
        print(
            f"{name}\t{score['prefix_order_ratio']:.3f}\t"
            f"{score['suffix_order_ratio']:.3f}\t"
            f"{score['minimum_order_ratio']:.3f}"
        )

    print("\nMain matched sensitivity medians")
    print("System\tPrefix\tSuffix\tMinimum\tMin>=1")
    for name, record in main_matched["systems"].items():
        summary = record["summary"]
        minimum = summary["minimum_order_ratio"]
        print(
            f"{name}\t"
            f"{summary['prefix_order_ratio']['median']:.3f}\t"
            f"{summary['suffix_order_ratio']['median']:.3f}\t"
            f"{minimum['median']:.3f}\t"
            f"{minimum['fraction_at_or_above_neutral']:.3f}"
        )

    print(
        f"\nWrote {out.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())

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
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from _canonical import (
    SequenceUnit,
    bootstrap_groups_to_target,
    composition_controlled_affix_scores,
    load_corpus,
    sample_units_to_target,
    sequence_units,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ESTIMATOR_VERSION = "3.0.0"
DEFAULT_SEED = 20260929
DEFAULT_REPLICATES = 200
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


def _punctuation_only(text):
    """True when every character is Unicode punctuation."""
    return all(
        unicodedata.category(char).startswith("P")
        for char in text
    )


def tokenize_segments(text, pattern):
    """Tokenize without manufacturing adjacency across excluded material.

    Input is inspected one whitespace item at a time. An item is accepted only
    when it contains exactly one target-alphabet run and every character
    outside that run is punctuation. Items that contain no target word, contain
    digits or foreign-script material outside the run, or split into multiple
    target-alphabet runs terminate the current sequence. Their neighbors
    therefore never become adjacent.
    """
    segments = []
    current = []
    diagnostics = Counter()

    for raw in text.split():
        item = raw.lower()
        matches = list(re.finditer(pattern, item))
        token = None

        if len(matches) == 1:
            match = matches[0]
            remainder = item[:match.start()] + item[match.end():]
            if not remainder or _punctuation_only(remainder):
                token = match.group(0)
        elif len(matches) > 1:
            diagnostics["split_items"] += 1

        if token is not None:
            current.append(token)
            diagnostics["retained_items"] += 1
            continue

        diagnostics["break_items"] += 1
        if not matches:
            diagnostics["no_target_run_items"] += 1
        elif len(matches) == 1:
            diagnostics["mixed_content_items"] += 1

        if current:
            segments.append(tuple(current))
            current = []

    if current:
        segments.append(tuple(current))

    return tuple(segments), dict(diagnostics)


def load_leipzig(label, folder, archive, pattern):
    path = RAW / "cross_linguistic" / folder / archive
    units = []
    diagnostics = Counter()
    with tarfile.open(path, "r:gz") as bundle:
        member = next(item for item in bundle.getmembers()
                      if item.name.endswith("-sentences.txt"))
        handle = bundle.extractfile(member)
        if handle is None:
            raise RuntimeError(f"could not read {member.name}")
        for index, raw_line in enumerate(handle):
            line = raw_line.decode("utf-8", errors="ignore").rstrip("\n")
            sentence = line.split("\t", 1)[1] if "\t" in line else line
            segments, diag = tokenize_segments(sentence, pattern)
            diagnostics.update(diag)
            for segment_index, tokens in enumerate(segments):
                if tokens:
                    units.append(SequenceUnit(
                        unit_id=f"{folder}:{index}:segment-{segment_index}",
                        tokens=tokens,
                        boundary_type="sentence_fragment",
                        document=archive,
                    ))
    return units, [path], dict(diagnostics)


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
    diagnostics = Counter()
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+|\n\s*\n", text)):
        segments, diag = tokenize_segments(sentence, LATIN)
        diagnostics.update(diag)
        for segment_index, tokens in enumerate(segments):
            if tokens:
                units.append(SequenceUnit(
                    unit_id=f"{folder}:{index}:segment-{segment_index}",
                    tokens=tokens,
                    boundary_type="sentence_fragment",
                    document=filename,
                ))
    return units, [path], dict(diagnostics)


def load_conllu(folder, filenames):
    paths = [RAW / "cross_linguistic" / folder / name for name in filenames]
    units = []
    diagnostics = Counter()
    sentence_index = 0
    segment_index = 0
    current = []

    def flush(document):
        nonlocal current, segment_index
        if current:
            units.append(SequenceUnit(
                unit_id=f"{document}:{sentence_index}:segment-{segment_index}",
                tokens=tuple(current),
                boundary_type="sentence_fragment",
                document=document,
            ))
            current = []
            segment_index += 1

    for path in paths:
        lines = path.read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines() + [""]
        for line in lines:
            if not line.strip():
                flush(path.name)
                sentence_index += 1
                segment_index = 0
                continue
            if line.startswith("#") or "\t" not in line:
                continue
            fields = line.split("\t")
            if fields[0].isdigit():
                word = fields[1].lower()
                if word.isalpha():
                    current.append(word)
                    diagnostics["retained_items"] += 1
                else:
                    diagnostics["break_items"] += 1
                    diagnostics["mixed_content_items"] += 1
                    flush(path.name)
        flush(path.name)
    return units, paths, dict(diagnostics)


def corpus_inventory():
    corpora = {}
    for label, folder, archive, pattern, family in LEIPZIG:
        units, paths, diagnostics = load_leipzig(
            label, folder, archive, pattern
        )
        corpora[label] = {
            "family": family,
            "units": units,
            "paths": paths,
            "source_type": "Leipzig boundary-safe sentence fragments",
            "tokenization_diagnostics": diagnostics,
        }

    for label, folder, filename in (
        ("Middle English", "middle_english", "chaucer_canterbury_tales_22120.txt"),
        ("KJV English", "kjv_english", "king_james_bible_10900.txt"),
    ):
        units, paths, diagnostics = load_gutenberg(folder, filename)
        corpora[label] = {
            "family": "Indo-European",
            "units": units,
            "paths": paths,
            "source_type": "Gutenberg boundary-safe sentence fragments",
            "tokenization_diagnostics": diagnostics,
        }

    units, paths, diagnostics = load_conllu(
        "ottoman_turkish",
        ("ota_dudu_train.conllu", "ota_dudu_test.conllu"),
    )
    corpora[UNDERSIZED_SYSTEM] = {
        "family": "Turkic",
        "units": units,
        "paths": paths,
        "source_type": "CoNLL-U boundary-safe sentence fragments",
        "tokenization_diagnostics": diagnostics,
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


def run_voynich_page_bootstrap(
        units, target_tokens, replicates, master_seed):
    """Page-block bootstrap for cluster-aware Voynich robustness."""
    schedule = build_seed_schedule(
        ["VOYNICH"],
        "voynich_page_block_bootstrap",
        master_seed,
        replicates,
    )["VOYNICH"]
    sampled = []
    for index, seed in enumerate(schedule, start=1):
        sample = bootstrap_groups_to_target(
            units,
            "page",
            target_tokens,
            np.random.default_rng(seed),
        )
        sampled.append(compact_score(sample))
        if index % 25 == 0 or index == replicates:
            print(
                f"  voynich_page_block_bootstrap: {index}/{replicates}",
                flush=True,
            )
    return {
        "profile": "voynich_page_block_bootstrap",
        "target_tokens": target_tokens,
        "replicate_n": replicates,
        "group_attribute": "page",
        "sampling": "page blocks with replacement; line boundaries preserved",
        "summary": summarize_replicates(sampled),
        "replicates": sampled,
        "seed_schedule": schedule,
    }


def exact_repeat_robustness(units):
    """Measure exact adjacent repeats and a break-at-repeat sensitivity."""
    observed = 0
    expected = 0.0
    broken = []

    for unit in units:
        tokens = unit.tokens
        observed += sum(
            left == right
            for left, right in zip(tokens, tokens[1:])
        )
        n = len(tokens)
        if n:
            counts = Counter(tokens)
            expected += sum(
                k * (k - 1) / n
                for k in counts.values()
            )

        if not tokens:
            continue
        segment = [tokens[0]]
        segment_index = 0
        for left, right in zip(tokens, tokens[1:]):
            if left == right:
                broken.append(SequenceUnit(
                    unit_id=(
                        f"{unit.unit_id}:repeat-break-{segment_index}"
                    ),
                    tokens=tuple(segment),
                    boundary_type=f"{unit.boundary_type}_repeat_fragment",
                    page=unit.page,
                    section=unit.section,
                    hand=unit.hand,
                    currier=unit.currier,
                    document=unit.document,
                ))
                segment_index += 1
                segment = [right]
            else:
                segment.append(right)
        if segment:
            broken.append(SequenceUnit(
                unit_id=f"{unit.unit_id}:repeat-break-{segment_index}",
                tokens=tuple(segment),
                boundary_type=f"{unit.boundary_type}_repeat_fragment",
                page=unit.page,
                section=unit.section,
                hand=unit.hand,
                currier=unit.currier,
                document=unit.document,
            ))

    return {
        "observed_exact_adjacent_repeats": int(observed),
        "expected_exact_adjacent_repeats_under_within_unit_shuffle": (
            float(expected)
        ),
        "original_score": compact_score(units),
        "score_after_breaking_at_exact_repeat_pairs": compact_score(broken),
        "interpretation": (
            "Breaking every exact adjacent repeated-token pair is a harsh "
            "robustness check. It removes those adjacencies while preserving "
            "all tokens in separate sequence fragments."
        ),
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
            "tokenization_diagnostics": {
                "break_items": 0,
                "policy": "preserved cleaned parquet whitespace tokens",
            },
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
            "tokenization_diagnostics": record.get(
                "tokenization_diagnostics", {}
            ),
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
        f"\nVoynich page-block robustness: {main_target} tokens, "
        f"{args.replicates} bootstrap replicates",
        flush=True,
    )
    voynich_page_bootstrap = run_voynich_page_bootstrap(
        systems["VOYNICH"]["units"],
        main_target,
        args.replicates,
        args.seed,
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
        "schema_version": "3.1",
        "estimator_version": ESTIMATOR_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "validated descriptive scientific result; finite-corpus scope",
        "scope_warning": (
            "This estimator measures affix-class ordering relative to an "
            "exact within-unit permutation expectation. It does not establish "
            "natural-language uniqueness, decipherment, language identity, "
            "or a generating mechanism."
        ),
        "method": {
            "full_corpus_primary": True,
            "matched_subsample_replicates": args.replicates,
            "line_deletion_stability": {
                "systems": main_systems,
                "excluded_system": UNDERSIZED_SYSTEM,
                "target_rule": (
                    f"{MAIN_MATCH_FRACTION:.0%} of canonical Voynich token count"
                ),
                "target_tokens": main_target,
                "interpretation": (
                    "without-replacement line/sentence deletion stability; "
                    "not the cluster-aware uncertainty summary for Voynich"
                ),
            },
            "voynich_page_block_robustness": {
                "target_tokens": main_target,
                "group_attribute": "page",
                "interpretation": (
                    "cluster-aware Voynich robustness summary; page blocks "
                    "sampled with replacement while preserving line units"
                ),
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
            "comparator_boundary_policy": (
                "excluded or split whitespace items break sequences; "
                "surviving neighbors are never joined across dropped material"
            ),
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
            "line_deletion_stability": main_matched,
            "all_system_small_target": all_system_small,
        },
        "voynich_cluster_robustness": {
            "page_block_bootstrap": voynich_page_bootstrap,
        },
        "voynich_exact_repeat_robustness": exact_repeat_robustness(
            systems["VOYNICH"]["units"]
        ),
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

    def print_matched_table(title, profile):
        print(f"\n{title}")
        print(
            "System\tPrefix median [95%]\tSuffix median [95%]\t"
            "Minimum median [95%]\tMin>=1"
        )
        for name, record in profile["systems"].items():
            summary = record["summary"]
            prefix = summary["prefix_order_ratio"]
            suffix = summary["suffix_order_ratio"]
            minimum = summary["minimum_order_ratio"]
            print(
                f"{name}\t"
                f"{prefix['median']:.3f} "
                f"[{prefix['ci95'][0]:.3f},{prefix['ci95'][1]:.3f}]\t"
                f"{suffix['median']:.3f} "
                f"[{suffix['ci95'][0]:.3f},{suffix['ci95'][1]:.3f}]\t"
                f"{minimum['median']:.3f} "
                f"[{minimum['ci95'][0]:.3f},{minimum['ci95'][1]:.3f}]\t"
                f"{minimum['fraction_at_or_above_neutral']:.3f}"
            )

    print_matched_table(
        "Line-deletion stability sensitivity",
        main_matched,
    )
    print_matched_table(
        "All-system small-target sensitivity",
        all_system_small,
    )

    print("\nVoynich page-block robustness")
    page = voynich_page_bootstrap["summary"]
    for metric in (
        "prefix_order_ratio",
        "suffix_order_ratio",
        "minimum_order_ratio",
    ):
        value = page[metric]
        print(
            f"{metric}\t{value['median']:.3f}\t"
            f"[{value['ci95'][0]:.3f},{value['ci95'][1]:.3f}]\t"
            f"fraction>=1={value['fraction_at_or_above_neutral']:.3f}"
        )

    repeats = exact_repeat_robustness(systems["VOYNICH"]["units"])
    print("\nVoynich exact-repeat robustness")
    print(
        "observed=",
        repeats["observed_exact_adjacent_repeats"],
        "expected=",
        f"{repeats['expected_exact_adjacent_repeats_under_within_unit_shuffle']:.3f}",
        "suffix_after_break=",
        f"{repeats['score_after_breaking_at_exact_repeat_pairs']['suffix_order_ratio']:.3f}",
    )

    print("\nVoynich discovered-family diagnostics")
    for profile_name, profile in (
        ("line_deletion_stability", main_matched),
        ("all_system_small_target", all_system_small),
    ):
        voy = profile["systems"]["VOYNICH"]["summary"]
        print(
            f"{profile_name}\tprefix={voy['modal_prefix_affixes']}\t"
            f"suffix={voy['modal_suffix_affixes']}\t"
            f"prefix_class_n={voy['included_class_n_range']['prefix']}\t"
            f"suffix_class_n={voy['included_class_n_range']['suffix']}"
        )

    print(
        f"\nWrote {out.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())

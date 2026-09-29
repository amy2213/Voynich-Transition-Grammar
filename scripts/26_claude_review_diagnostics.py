#!/usr/bin/env python3
"""Independent pre-freeze diagnostics for the external Version 3 review.

This script does not alter the Version 3 estimator. It tests three review
claims against the frozen repository inputs:

1. whether 90% line subsampling understates Voynich cluster-level variation
   relative to a page-block bootstrap;
2. whether comparator regex tokenization manufactures adjacency across
   whitespace items that are dropped or split;
3. whether the Voynich suffix effect is driven by exact adjacent word repeats.

The output is diagnostic evidence only.
"""

from __future__ import annotations

import importlib.util
import json
import re
import tarfile
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from _canonical import (
    PARQUET_PATH,
    SequenceUnit,
    bootstrap_groups_to_target,
    get_section,
    sample_units_to_target,
    sequence_units,
    load_corpus,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SEED = 20260929
REPLICATES = 200


def load_v3():
    path = ROOT / "scripts" / "24_prefix_suffix_v3.py"
    spec = importlib.util.spec_from_file_location("v3diag", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V3 = load_v3()


def summarize(records):
    return V3.summarize_replicates(records)


def score(units):
    return V3.compact_score(units)


def parent_unit_id(unit_id):
    return unit_id.split(":fragment-", 1)[0]


def matched_voynich_diagnostics(voynich_units, main_system_names):
    target = int(sum(len(u.tokens) for u in voynich_units) * 0.90)
    schedule = V3.build_seed_schedule(
        main_system_names,
        "main_matched_excluding_undersized_ottoman",
        SEED,
        REPLICATES,
    )["VOYNICH"]

    line_records = []
    line_sources = []
    page_records = []

    for seed in schedule:
        rng = np.random.default_rng(seed)
        sample = sample_units_to_target(voynich_units, target, rng)
        line_records.append(score(sample))
        line_sources.append({parent_unit_id(u.unit_id) for u in sample})

        rng = np.random.default_rng(seed)
        page_sample = bootstrap_groups_to_target(
            voynich_units, "page", target, rng
        )
        page_records.append(score(page_sample))

    pairwise_overlap = []
    for i in range(len(line_sources)):
        for j in range(i + 1, len(line_sources)):
            a, b = line_sources[i], line_sources[j]
            denom = min(len(a), len(b))
            if denom:
                pairwise_overlap.append(len(a & b) / denom)

    return {
        "target_tokens": target,
        "line_without_replacement": summarize(line_records),
        "page_block_bootstrap": summarize(page_records),
        "line_sample_source_line_fraction": {
            "median": float(np.median([
                len(s) / len(voynich_units) for s in line_sources
            ])),
            "mean_pairwise_source_line_overlap_fraction": (
                float(np.mean(pairwise_overlap))
            ),
        },
    }


def exact_repeat_diagnostics(voynich_units):
    observed = 0
    expected = 0.0
    for unit in voynich_units:
        toks = unit.tokens
        observed += sum(a == b for a, b in zip(toks, toks[1:]))
        n = len(toks)
        if n:
            counts = Counter(toks)
            expected += sum(k * (k - 1) / n for k in counts.values())

    split_units = []
    break_n = 0
    for unit in voynich_units:
        if not unit.tokens:
            continue
        current = [unit.tokens[0]]
        segment = 0
        for previous, token in zip(unit.tokens, unit.tokens[1:]):
            if token == previous:
                split_units.append(SequenceUnit(
                    unit_id=f"{unit.unit_id}:repeat-break-{segment}",
                    tokens=tuple(current),
                    boundary_type="line_repeat_fragment",
                    page=unit.page,
                    section=unit.section,
                    hand=unit.hand,
                    currier=unit.currier,
                    document=unit.document,
                ))
                segment += 1
                break_n += 1
                current = [token]
            else:
                current.append(token)
        if current:
            split_units.append(SequenceUnit(
                unit_id=f"{unit.unit_id}:repeat-break-{segment}",
                tokens=tuple(current),
                boundary_type="line_repeat_fragment",
                page=unit.page,
                section=unit.section,
                hand=unit.hand,
                currier=unit.currier,
                document=unit.document,
            ))

    return {
        "observed_exact_adjacent_repeats": int(observed),
        "expected_exact_adjacent_repeats_under_within_line_shuffle": float(expected),
        "repeat_pair_breaks": break_n,
        "original_score": score(voynich_units),
        "score_after_breaking_at_exact_repeat_pairs": score(split_units),
    }


def punctuation_only(text):
    return all(unicodedata.category(ch).startswith("P") for ch in text)


def conservative_segments(text, pattern):
    """Return token segments without crossing dropped/split whitespace items.

    A whitespace item is accepted only when it contains exactly one target-
    alphabet run and every character outside that run is punctuation. An item
    with no run, digits/foreign letters outside the run, or multiple runs
    (e.g. l'arte or foo-bar) breaks the sequence and is not converted into
    artificial neighboring tokens.
    """
    segments = []
    current = []
    break_items = 0
    multi_run_items = 0
    dropped_items = 0

    for raw in text.split():
        item = raw.lower()
        matches = list(re.finditer(pattern, item))
        accepted = False
        token = None
        if len(matches) == 1:
            m = matches[0]
            remainder = item[:m.start()] + item[m.end():]
            if not remainder or punctuation_only(remainder):
                accepted = True
                token = m.group(0)
        elif len(matches) > 1:
            multi_run_items += 1

        if accepted:
            current.append(token)
        else:
            dropped_items += 1
            if current:
                segments.append(tuple(current))
                current = []
            break_items += 1

    if current:
        segments.append(tuple(current))
    return segments, {
        "break_items": break_items,
        "multi_run_items": multi_run_items,
        "dropped_items": dropped_items,
    }


def load_leipzig_conservative(folder, archive, pattern):
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
            segments, diag = conservative_segments(sentence, pattern)
            diagnostics.update(diag)
            for segment_index, tokens in enumerate(segments):
                if tokens:
                    units.append(SequenceUnit(
                        unit_id=f"{folder}:{index}:segment-{segment_index}",
                        tokens=tokens,
                        boundary_type="sentence_fragment",
                        document=archive,
                    ))
    return units, dict(diagnostics)


def load_gutenberg_conservative(folder, filename):
    path = RAW / "cross_linguistic" / folder / filename
    text = V3.strip_gutenberg(path.read_text(
        encoding="utf-8", errors="ignore"
    ))
    units = []
    diagnostics = Counter()
    for index, sentence in enumerate(
        re.split(r"(?<=[.!?])\s+|\n\s*\n", text)
    ):
        segments, diag = conservative_segments(sentence, V3.LATIN)
        diagnostics.update(diag)
        for segment_index, tokens in enumerate(segments):
            if tokens:
                units.append(SequenceUnit(
                    unit_id=f"{folder}:{index}:segment-{segment_index}",
                    tokens=tokens,
                    boundary_type="sentence_fragment",
                    document=filename,
                ))
    return units, dict(diagnostics)


def load_conllu_conservative(folder, filenames):
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
                else:
                    diagnostics["dropped_items"] += 1
                    diagnostics["break_items"] += 1
                    flush(path.name)
        flush(path.name)
    return units, dict(diagnostics)


def conservative_comparator_inventory():
    corpora = {}
    for label, folder, archive, pattern, family in V3.LEIPZIG:
        units, diag = load_leipzig_conservative(folder, archive, pattern)
        corpora[label] = {
            "units": units,
            "diagnostics": diag,
            "family": family,
        }

    for label, folder, filename in (
        ("Middle English", "middle_english", "chaucer_canterbury_tales_22120.txt"),
        ("KJV English", "kjv_english", "king_james_bible_10900.txt"),
    ):
        units, diag = load_gutenberg_conservative(folder, filename)
        corpora[label] = {
            "units": units,
            "diagnostics": diag,
            "family": "Indo-European",
        }

    units, diag = load_conllu_conservative(
        "ottoman_turkish",
        ("ota_dudu_train.conllu", "ota_dudu_test.conllu"),
    )
    corpora["Ottoman Turkish"] = {
        "units": units,
        "diagnostics": diag,
        "family": "Turkic",
    }
    return corpora


def comparator_seam_diagnostics():
    current = V3.corpus_inventory()
    conservative = conservative_comparator_inventory()
    out = {}
    for name in sorted(current):
        current_units = current[name]["units"]
        strict_units = conservative[name]["units"]
        out[name] = {
            "current_tokens": sum(len(u.tokens) for u in current_units),
            "conservative_tokens": sum(len(u.tokens) for u in strict_units),
            "conservative_break_diagnostics": conservative[name]["diagnostics"],
            "current_score": score(current_units),
            "conservative_break_score": score(strict_units),
        }
    return out


def voynich_omitted_item_break_diagnostics():
    df = pd.read_parquet(PARQUET_PATH)
    zl = df[df["source_name"] == "Zandbergen-Landini"].copy()
    units = []
    dropped = 0
    line_count = 0

    for _, row in zl.iterrows():
        line_count += 1
        current = []
        segment = 0

        def flush():
            nonlocal current, segment
            if current:
                units.append(SequenceUnit(
                    unit_id=f"{row['page']}:{line_count}:segment-{segment}",
                    tokens=tuple(current),
                    boundary_type="line_fragment",
                    page=str(row["page"]),
                    section=get_section(row["page"]),
                    hand=str(row.get("H", "?")),
                    currier=str(row.get("L", "?")),
                ))
                current = []
                segment += 1

        text = row["text"]
        if not isinstance(text, str):
            continue
        for token in text.strip().split():
            accepted = (
                not token.startswith("%")
                and not token.startswith("{")
                and token not in {"-", "=", "!"}
            )
            if accepted:
                current.append(token)
            else:
                dropped += 1
                flush()
        flush()

    current_units = sequence_units(load_corpus())
    return {
        "dropped_whitespace_items_that_break": dropped,
        "current_tokens": sum(len(u.tokens) for u in current_units),
        "break_safe_tokens": sum(len(u.tokens) for u in units),
        "current_score": score(current_units),
        "break_safe_score": score(units),
    }


def main():
    voy_units = sequence_units(load_corpus())
    current_comparators = V3.corpus_inventory()
    system_names = sorted(["VOYNICH", *current_comparators.keys()])
    main_system_names = [
        name for name in system_names if name != V3.UNDERSIZED_SYSTEM
    ]

    payload = {
        "schema_version": "1.0",
        "purpose": "independent diagnostics for external pre-freeze review",
        "seed": SEED,
        "replicates": REPLICATES,
        "voynich_matched_resampling": matched_voynich_diagnostics(
            voy_units, main_system_names
        ),
        "voynich_exact_repeats": exact_repeat_diagnostics(voy_units),
        "comparator_seam_sensitivity": comparator_seam_diagnostics(),
        "voynich_omitted_item_break_sensitivity": (
            voynich_omitted_item_break_diagnostics()
        ),
    }

    out = ROOT / "results" / "claude_review_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=== VOYNICH RESAMPLING ===")
    res = payload["voynich_matched_resampling"]
    for label in ("line_without_replacement", "page_block_bootstrap"):
        s = res[label]
        print(
            label,
            "prefix", s["prefix_order_ratio"],
            "suffix", s["suffix_order_ratio"],
            "minimum", s["minimum_order_ratio"],
        )
    print("line overlap", res["line_sample_source_line_fraction"])

    print("\n=== EXACT REPEATS ===")
    print(json.dumps(payload["voynich_exact_repeats"], indent=2))

    print("\n=== COMPARATOR SEAM SENSITIVITY ===")
    for name, record in payload["comparator_seam_sensitivity"].items():
        cur = record["current_score"]
        safe = record["conservative_break_score"]
        print(
            name,
            f"prefix {cur['prefix_order_ratio']:.3f}->{safe['prefix_order_ratio']:.3f}",
            f"suffix {cur['suffix_order_ratio']:.3f}->{safe['suffix_order_ratio']:.3f}",
            record["conservative_break_diagnostics"],
        )

    print("\n=== VOYNICH DROPPED-ITEM BREAK SENSITIVITY ===")
    print(json.dumps(
        payload["voynich_omitted_item_break_sensitivity"], indent=2
    ))
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(main())

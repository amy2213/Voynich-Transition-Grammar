#!/usr/bin/env python3
"""Independent diagnostics for the proposed Version 3.1 correction.

Runs against the frozen v3.0.0 code/data baseline and tests:
1. line-edge sensitivity by trimming first/last tokens;
2. a position-aware null that holds first/last token classes fixed and
   permutes only the interior;
3. affix-discovery threshold sensitivity;
4. exact-repeat removal with observed and expected contributions both removed.

This script is diagnostic only. It does not modify v3.0.0 artifacts.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

import numpy as np

from _canonical import (
    SequenceUnit,
    assign_affix_sequences,
    bootstrap_groups_to_target,
    composition_controlled_affix_scores,
    composition_controlled_self_clustering_details,
    discover_affixes,
    load_corpus,
    sequence_units,
)

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260929
REPLICATES = 200


def load_v3():
    path = ROOT / "scripts" / "24_prefix_suffix_v3.py"
    spec = importlib.util.spec_from_file_location("v3_release", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V3 = load_v3()
BASE_DISCOVERY = dict(V3.DISCOVERY)


def clone_unit(unit, tokens, suffix):
    return SequenceUnit(
        unit_id=f"{unit.unit_id}:{suffix}",
        tokens=tuple(tokens),
        boundary_type=f"{unit.boundary_type}_{suffix}",
        page=unit.page,
        section=unit.section,
        hand=unit.hand,
        currier=unit.currier,
        document=unit.document,
    )


def trim_edges(units):
    trimmed = []
    removed = 0
    for unit in units:
        tokens = tuple(unit.tokens)
        if len(tokens) <= 2:
            removed += len(tokens)
            continue
        removed += 2
        trimmed.append(clone_unit(unit, tokens[1:-1], "interior"))
    return trimmed, removed


def score_units(units, discovery=None):
    sequences = [unit.tokens for unit in units]
    cfg = dict(BASE_DISCOVERY if discovery is None else discovery)
    score = composition_controlled_affix_scores(
        sequences, include_other=False, **cfg
    )
    return {
        "prefix": score["prefix"]["score"],
        "suffix": score["suffix"]["score"],
        "minimum": score["minimum"],
        "prefix_affixes": score["prefix"]["affixes"],
        "suffix_affixes": score["suffix"]["affixes"],
        "prefix_class_n": score["prefix"]["included_class_n"],
        "suffix_class_n": score["suffix"]["included_class_n"],
    }


def summarize(values):
    arr = np.asarray(values, dtype=float)
    return {
        "median": float(np.percentile(arr, 50)),
        "ci95": [
            float(np.percentile(arr, 2.5)),
            float(np.percentile(arr, 97.5)),
        ],
        "fraction_below_1": float(np.mean(arr < 1.0)),
        "fraction_at_or_above_1": float(np.mean(arr >= 1.0)),
        "n": int(arr.size),
    }


def bootstrap_scores(units, target, scorer, profile):
    rng = np.random.default_rng(
        np.uint64(SEED)
        ^ np.uint64(int.from_bytes(
            __import__("hashlib").sha256(profile.encode()).digest()[:8],
            "big",
        ))
    )
    seeds = rng.integers(0, 2**63 - 1, REPLICATES).tolist()
    records = []
    for i, seed in enumerate(seeds, 1):
        sample = bootstrap_groups_to_target(
            units, "page", target, np.random.default_rng(seed)
        )
        records.append(scorer(sample))
        if i % 25 == 0 or i == REPLICATES:
            print(f"{profile}: {i}/{REPLICATES}", flush=True)
    return {
        "target_tokens": target,
        "replicates": REPLICATES,
        "prefix": summarize([r["prefix"] for r in records]),
        "suffix": summarize([r["suffix"] for r in records]),
        "minimum": summarize([r["minimum"] for r in records]),
        "seed_schedule": seeds,
    }


def position_aware_details(class_sequences, min_n=10, include_other=False):
    """Exact expected self-transitions with line endpoints held fixed.

    For n >= 3, first and last classes are fixed. The m=n-2 interior classes
    are uniformly permuted. For class c with k interior occurrences:

      E(interior c->c) = k(k-1)/m
      E(first c -> interior c) = I(first=c) k/m
      E(interior c -> last c) = I(last=c) k/m

    For n=2 the sole edge is fully fixed, so expectation equals observation.
    """
    observed = Counter()
    expected = Counter()
    src = Counter()
    dst = Counter()
    total = Counter()

    for classes in class_sequences:
        classes = tuple(classes)
        n = len(classes)
        if not n:
            continue
        total.update(classes)
        if n >= 2:
            src.update(classes[:-1])
            dst.update(classes[1:])
            for a, b in zip(classes, classes[1:]):
                if a == b:
                    observed[a] += 1

        if n == 1:
            continue
        if n == 2:
            if classes[0] == classes[1]:
                expected[classes[0]] += 1.0
            continue

        interior = classes[1:-1]
        m = len(interior)
        counts = Counter(interior)
        labels = set(classes)
        first = classes[0]
        last = classes[-1]
        for label in labels:
            k = counts[label]
            exp = (k * (k - 1) / m) if m else 0.0
            if m and first == label:
                exp += k / m
            if m and last == label:
                exp += k / m
            expected[label] += exp

    candidates = set(total)
    if not include_other:
        candidates.discard("OTHER")

    included_obs = 0.0
    included_exp = 0.0
    details = {}
    for label in sorted(total):
        exp = expected[label]
        supported = (
            label in candidates
            and src[label] > min_n
            and dst[label] > min_n
            and exp > 1
        )
        ratio = observed[label] / exp if exp else None
        details[label] = {
            "observed": observed[label],
            "expected_position_aware": exp,
            "source_n": src[label],
            "destination_n": dst[label],
            "token_n": total[label],
            "ratio": ratio,
            "included": supported,
        }
        if supported:
            included_obs += observed[label]
            included_exp += exp

    return {
        "score": (
            included_obs / included_exp
            if included_exp > 0 else None
        ),
        "included_observed": included_obs,
        "included_expected": included_exp,
        "classes": details,
        "null": (
            "first and last classes fixed; interior classes uniformly permuted"
        ),
    }


def position_aware_score(units, discovery=None):
    sequences = [unit.tokens for unit in units]
    cfg = dict(BASE_DISCOVERY if discovery is None else discovery)
    min_n = cfg.pop("min_n", 10)
    out = {}
    for side in ("prefix", "suffix"):
        affixes = discover_affixes(sequences, side, **cfg)
        labels = assign_affix_sequences(sequences, affixes, side)
        details = position_aware_details(
            labels, min_n=min_n, include_other=False
        )
        out[side] = {
            "affixes": affixes,
            **details,
        }
    p = out["prefix"]["score"]
    s = out["suffix"]["score"]
    return {
        "prefix": p,
        "suffix": s,
        "minimum": min(p, s) if None not in (p, s) else None,
        "prefix_affixes": out["prefix"]["affixes"],
        "suffix_affixes": out["suffix"]["affixes"],
    }


def classify_token(token, affixes, side):
    for affix in affixes:
        if side == "prefix":
            if token.startswith(affix):
                return affix
        else:
            if token.endswith(affix):
                return affix
    return "OTHER"


def repeat_symmetric_adjustment(units, side):
    sequences = [unit.tokens for unit in units]
    cfg = dict(BASE_DISCOVERY)
    min_n = cfg.pop("min_n", 10)
    affixes = discover_affixes(sequences, side, **cfg)
    labels = assign_affix_sequences(sequences, affixes, side)
    base = composition_controlled_self_clustering_details(
        labels, min_n=min_n, include_other=False
    )

    exact_obs = Counter()
    exact_exp = Counter()

    for unit, class_seq in zip(units, labels):
        tokens = tuple(unit.tokens)
        n = len(tokens)
        if not n:
            continue
        for i in range(n - 1):
            if tokens[i] == tokens[i + 1]:
                exact_obs[class_seq[i]] += 1

        counts = Counter(tokens)
        for token, k in counts.items():
            label = classify_token(token, affixes, side)
            exact_exp[label] += k * (k - 1) / n

    adjusted_obs = 0.0
    adjusted_exp = 0.0
    included = {}
    for label, record in base["classes"].items():
        if not record["included_in_mean"]:
            continue
        obs = record["observed"] - exact_obs[label]
        exp = (
            record["expected_within_unit_shuffle"]
            - exact_exp[label]
        )
        included[label] = {
            "base_observed": record["observed"],
            "base_expected": record["expected_within_unit_shuffle"],
            "exact_repeat_observed": exact_obs[label],
            "exact_repeat_expected": exact_exp[label],
            "adjusted_observed": obs,
            "adjusted_expected": exp,
        }
        adjusted_obs += obs
        adjusted_exp += exp

    return {
        "side": side,
        "affixes": affixes,
        "base_score": base["score"],
        "included_exact_repeat_observed": float(
            sum(exact_obs[label] for label in included)
        ),
        "included_exact_repeat_expected": float(
            sum(exact_exp[label] for label in included)
        ),
        "adjusted_score": (
            adjusted_obs / adjusted_exp
            if adjusted_exp > 0 else None
        ),
        "classes": included,
    }


def discovery_settings():
    out = {}
    for n in (3, 5, 8):
        for max_len in (3, 4):
            for low, high, cov_name in (
                (0.02, 0.20, "basecov"),
                (0.01, 0.30, "widecov"),
            ):
                name = f"n{n}_len2-{max_len}_{cov_name}"
                out[name] = {
                    "n_families": n,
                    "min_len": 2,
                    "max_len": max_len,
                    "min_coverage": low,
                    "max_coverage": high,
                    "candidate_pool": 80,
                    "min_n": 10,
                    "nesting_mode": "side_aware",
                }
    return out


def main():
    voy = sequence_units(load_corpus())
    comps = V3.corpus_inventory()
    systems = {"VOYNICH": {"units": voy}, **comps}

    interior_voy, removed = trim_edges(voy)
    interior_target = int(
        sum(len(u.tokens) for u in interior_voy) * 0.90
    )

    print("Running interior-only Voynich page bootstrap", flush=True)
    interior_boot = bootstrap_scores(
        interior_voy,
        interior_target,
        score_units,
        "voynich_interior_only_page_bootstrap",
    )

    main_target = int(sum(len(u.tokens) for u in voy) * 0.90)
    print("Running position-aware Voynich page bootstrap", flush=True)
    position_boot = bootstrap_scores(
        voy,
        main_target,
        position_aware_score,
        "voynich_position_aware_page_bootstrap",
    )

    print("Scoring line-edge trim sensitivity", flush=True)
    edge_trim = {}
    for name in ("VOYNICH", "Arabic", "Georgian", "Swahili"):
        units = systems[name]["units"]
        trimmed, removed_n = trim_edges(units)
        edge_trim[name] = {
            "all_tokens": score_units(units),
            "interior_only": score_units(trimmed),
            "original_token_n": sum(len(u.tokens) for u in units),
            "interior_token_n": sum(len(u.tokens) for u in trimmed),
            "removed_token_n": removed_n,
        }

    print("Scoring discovery sensitivity", flush=True)
    settings = discovery_settings()
    critical = {}
    for name in ("VOYNICH", "Arabic", "Georgian", "Swahili"):
        records = {}
        for setting_name, cfg in settings.items():
            records[setting_name] = score_units(
                systems[name]["units"], cfg
            )
        critical[name] = records

    # Wider-coverage sensitivity for every system, because this is the
    # specific threshold choice implicated by the review.
    wide_cfg = dict(BASE_DISCOVERY)
    wide_cfg["min_coverage"] = 0.01
    wide_cfg["max_coverage"] = 0.30
    all_system_wide = {}
    for name in sorted(systems):
        all_system_wide[name] = {
            "baseline": score_units(systems[name]["units"]),
            "wide_1_30": score_units(systems[name]["units"], wide_cfg),
        }
        print(f"  discovery all-system: {name}", flush=True)

    ranges = {}
    for name, records in critical.items():
        prefixes = [r["prefix"] for r in records.values()]
        suffixes = [r["suffix"] for r in records.values()]
        minima = [r["minimum"] for r in records.values()]
        ranges[name] = {
            "prefix_range": [min(prefixes), max(prefixes)],
            "suffix_range": [min(suffixes), max(suffixes)],
            "minimum_range": [min(minima), max(minima)],
        }

    print("Scoring position-aware full corpus", flush=True)
    position_full = {}
    for name in sorted(systems):
        position_full[name] = position_aware_score(
            systems[name]["units"]
        )

    repeats = {
        "prefix": repeat_symmetric_adjustment(voy, "prefix"),
        "suffix": repeat_symmetric_adjustment(voy, "suffix"),
    }

    payload = {
        "schema_version": "v3.1-diagnostic-1",
        "frozen_source_release": "v3.0.0",
        "frozen_source_commit": (
            "b93e87468347c154cbe9c84cb12ebbbdc9823821"
        ),
        "seed": SEED,
        "replicates": REPLICATES,
        "interior_only_voynich": {
            "removed_first_last_tokens": removed,
            "interior_target_tokens": interior_target,
            "full_corpus_interior_score": score_units(interior_voy),
            "page_bootstrap": interior_boot,
        },
        "position_aware_voynich": {
            "target_tokens": main_target,
            "full_corpus": position_aware_score(voy),
            "page_bootstrap": position_boot,
        },
        "line_edge_trim_sensitivity": edge_trim,
        "discovery_sensitivity": {
            "settings": settings,
            "critical_systems": critical,
            "critical_ranges": ranges,
            "all_system_baseline_vs_wide_1_30": all_system_wide,
        },
        "position_aware_full_corpus_all_systems": position_full,
        "repeat_symmetric_adjustment": repeats,
    }

    out = ROOT / "results" / "v31_position_threshold_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\n=== INTERIOR-ONLY VOYNICH PAGE BOOTSTRAP ===")
    print(json.dumps(interior_boot, indent=2))
    print("\n=== POSITION-AWARE VOYNICH PAGE BOOTSTRAP ===")
    print(json.dumps(position_boot, indent=2))
    print("\n=== EDGE TRIM ===")
    print(json.dumps(edge_trim, indent=2))
    print("\n=== DISCOVERY RANGES ===")
    print(json.dumps(ranges, indent=2))
    print("\n=== ALL SYSTEM BASE VS WIDE 1-30 ===")
    print(json.dumps(all_system_wide, indent=2))
    print("\n=== REPEAT SYMMETRIC ADJUSTMENT ===")
    print(json.dumps(repeats, indent=2))
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(main())

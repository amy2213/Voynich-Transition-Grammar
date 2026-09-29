#!/usr/bin/env python3
"""Fast subset of the v3.1 pre-freeze diagnostics."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "v31diag",
    ROOT / "scripts" / "28_v31_position_threshold_diagnostics.py",
)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def main():
    voy = diag.sequence_units(diag.load_corpus())
    comps = diag.V3.corpus_inventory()
    systems = {"VOYNICH": {"units": voy}, **comps}

    edge_trim = {}
    for name in ("VOYNICH", "Arabic", "Georgian", "Swahili"):
        units = systems[name]["units"]
        trimmed, removed = diag.trim_edges(units)
        edge_trim[name] = {
            "all_tokens": diag.score_units(units),
            "interior_only": diag.score_units(trimmed),
            "removed_token_n": removed,
        }

    settings = diag.discovery_settings()
    critical = {}
    for name in ("VOYNICH", "Arabic", "Georgian", "Swahili"):
        records = {}
        for setting_name, cfg in settings.items():
            records[setting_name] = diag.score_units(
                systems[name]["units"], cfg
            )
        critical[name] = records

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

    wide_cfg = dict(diag.BASE_DISCOVERY)
    wide_cfg["min_coverage"] = 0.01
    wide_cfg["max_coverage"] = 0.30
    wide = {}
    for name in sorted(systems):
        wide[name] = {
            "baseline": diag.score_units(systems[name]["units"]),
            "wide_1_30": diag.score_units(systems[name]["units"], wide_cfg),
        }

    repeats = {
        "prefix": diag.repeat_symmetric_adjustment(voy, "prefix"),
        "suffix": diag.repeat_symmetric_adjustment(voy, "suffix"),
    }

    position_full = {
        name: diag.position_aware_score(record["units"])
        for name, record in sorted(systems.items())
    }

    payload = {
        "edge_trim": edge_trim,
        "discovery_ranges": ranges,
        "critical_discovery": critical,
        "baseline_vs_wide_1_30": wide,
        "repeat_symmetric_adjustment": repeats,
        "position_aware_full_corpus": position_full,
    }
    out = ROOT / "results" / "v31_quick_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

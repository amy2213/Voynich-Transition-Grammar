#!/usr/bin/env python3
"""Minimal diagnostic for the specific external-review claims."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "v31diag_min",
    ROOT / "scripts" / "28_v31_position_threshold_diagnostics.py",
)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def main():
    voy = diag.sequence_units(diag.load_corpus())
    comps = diag.V3.corpus_inventory()
    systems = {
        "VOYNICH": voy,
        "Arabic": comps["Arabic"]["units"],
        "Georgian": comps["Georgian"]["units"],
        "Swahili": comps["Swahili"]["units"],
    }

    trim = {}
    for name, units in systems.items():
        interior, removed = diag.trim_edges(units)
        trim[name] = {
            "all": diag.score_units(units),
            "interior": diag.score_units(interior),
            "removed": removed,
        }

    base = dict(diag.BASE_DISCOVERY)
    settings = {
        "baseline": base,
        "n3": {**base, "n_families": 3},
        "n8": {**base, "n_families": 8},
        "len2_4": {**base, "max_len": 4},
        "wide_1_30": {
            **base,
            "min_coverage": 0.01,
            "max_coverage": 0.30,
        },
        "n3_len2_4_wide": {
            **base,
            "n_families": 3,
            "max_len": 4,
            "min_coverage": 0.01,
            "max_coverage": 0.30,
        },
        "n8_len2_4_wide": {
            **base,
            "n_families": 8,
            "max_len": 4,
            "min_coverage": 0.01,
            "max_coverage": 0.30,
        },
    }

    discovery = {}
    for name in ("VOYNICH", "Arabic"):
        discovery[name] = {
            setting: diag.score_units(systems[name], cfg)
            for setting, cfg in settings.items()
        }

    repeats = {
        "prefix": diag.repeat_symmetric_adjustment(voy, "prefix"),
        "suffix": diag.repeat_symmetric_adjustment(voy, "suffix"),
    }

    payload = {
        "edge_trim": trim,
        "settings": settings,
        "discovery": discovery,
        "repeat_symmetric_adjustment": repeats,
        "position_aware_full_voynich": diag.position_aware_score(voy),
    }
    out = ROOT / "results" / "v31_minimal_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Targeted v3.1 defect checks without loading the full comparator inventory."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "v31diag_target",
    ROOT / "scripts" / "28_v31_position_threshold_diagnostics.py",
)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def load_named_leipzig(wanted):
    out = {}
    for label, folder, archive, pattern, family in diag.V3.LEIPZIG:
        if label not in wanted:
            continue
        units, _, diagnostics = diag.V3.load_leipzig(
            label, folder, archive, pattern
        )
        out[label] = {
            "units": units,
            "diagnostics": diagnostics,
        }
    return out


def main():
    voy = diag.sequence_units(diag.load_corpus())
    comps = load_named_leipzig({"Arabic", "Georgian", "Swahili"})
    systems = {
        "VOYNICH": voy,
        **{name: rec["units"] for name, rec in comps.items()},
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
    discovery = {
        name: {
            setting: diag.score_units(units, cfg)
            for setting, cfg in settings.items()
        }
        for name, units in {
            "VOYNICH": voy,
            "Arabic": comps["Arabic"]["units"],
        }.items()
    }

    payload = {
        "edge_trim": trim,
        "discovery": discovery,
        "repeat_symmetric_adjustment": {
            "prefix": diag.repeat_symmetric_adjustment(voy, "prefix"),
            "suffix": diag.repeat_symmetric_adjustment(voy, "suffix"),
        },
        "position_aware_full_voynich": diag.position_aware_score(voy),
        "comparator_tokenization_diagnostics": {
            name: rec["diagnostics"] for name, rec in comps.items()
        },
    }
    out = ROOT / "results" / "v31_targeted_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

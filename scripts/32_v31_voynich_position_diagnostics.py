#!/usr/bin/env python3
"""Voynich-only 200-replicate position diagnostics for v3.1."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "v31diag_voy",
    ROOT / "scripts" / "28_v31_position_threshold_diagnostics.py",
)
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def main():
    voy = diag.sequence_units(diag.load_corpus())
    full_tokens = sum(len(u.tokens) for u in voy)
    target = int(full_tokens * 0.90)

    interior, removed = diag.trim_edges(voy)
    interior_tokens = sum(len(u.tokens) for u in interior)
    interior_target = int(interior_tokens * 0.90)

    print("Interior-only page bootstrap", flush=True)
    interior_boot = diag.bootstrap_scores(
        interior,
        interior_target,
        diag.score_units,
        "voynich_interior_only_page_bootstrap",
    )

    print("Position-aware page bootstrap", flush=True)
    position_boot = diag.bootstrap_scores(
        voy,
        target,
        diag.position_aware_score,
        "voynich_position_aware_page_bootstrap",
    )

    payload = {
        "source_release": "v3.0.0",
        "source_commit": "b93e87468347c154cbe9c84cb12ebbbdc9823821",
        "replicates": diag.REPLICATES,
        "original_token_n": full_tokens,
        "interior_token_n": interior_tokens,
        "removed_edge_token_n": removed,
        "interior_only": {
            "full_corpus": diag.score_units(interior),
            "page_bootstrap": interior_boot,
        },
        "position_aware": {
            "full_corpus": diag.position_aware_score(voy),
            "page_bootstrap": position_boot,
        },
    }

    out = ROOT / "results" / "v31_voynich_position_diagnostics.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

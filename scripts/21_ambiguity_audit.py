#!/usr/bin/env python3
"""Generate exact classifier-overlap and precedence-disagreement counts."""

import hashlib
import json
from pathlib import Path

from _canonical import (
    PARQUET_PATH,
    classifier_disagreement_report,
    flat_tokens,
    load_corpus,
    overlap_report,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "classifier_overlap_report.json"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    tokens = flat_tokens(load_corpus())
    report = {
        "schema_version": "1.0",
        "description": "Generated ambiguity and classifier-precedence audit",
        "corpus_tokens": len(tokens),
        "overlap": overlap_report(tokens),
        "precedence_disagreement": classifier_disagreement_report(tokens),
        "policies": {
            "canonical": "canonical_precedence",
            "strict_exclusion": "drop_and_break_sequence",
            "sensitivity": ["substring_precedence", "ambiguous_as_class"],
        },
        "provenance": {
            "script": "scripts/21_ambiguity_audit.py",
            "input": str(Path(PARQUET_PATH).relative_to(ROOT)),
            "input_sha256": sha256(PARQUET_PATH),
        },
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

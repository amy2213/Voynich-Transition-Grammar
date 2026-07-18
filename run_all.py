#!/usr/bin/env python3
"""Run the current Version 2 canonical pipeline.

The prefix/suffix comparison and other July exploratory analyses are excluded
until their open methodological blockers are repaired. See the claim ledger.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

CANONICAL_PIPELINE = [
    {
        "id": "validate_datasets",
        "command": ["scripts/00_validate_datasets.py"],
        "output": None,
    },
    {
        "id": "core_within_line",
        "command": ["scripts/01_core_analysis.py"],
        "output": "results/core_analysis_results.json",
    },
    {
        "id": "classifier_overlap",
        "command": ["scripts/21_ambiguity_audit.py"],
        "output": "results/classifier_overlap_report.json",
    },
    {
        "id": "full_test_report",
        "command": ["scripts/22_generate_test_report.py"],
        "output": "results/test_report.json",
    },
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def run_step(step, dry_run=False):
    command = [sys.executable, *step["command"]]
    output = ROOT / step["output"] if step["output"] else None
    started_ns = time.time_ns()
    started = time.monotonic()
    if dry_run:
        return {
            "id": step["id"], "command": " ".join(["python", *step["command"]]),
            "status": "dry_run", "exit_code": None,
        }
    result = subprocess.run(command, cwd=ROOT)
    record = {
        "id": step["id"],
        "command": " ".join(["python", *step["command"]]),
        "exit_code": result.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "status": "passed" if result.returncode == 0 else "failed",
    }
    if output:
        fresh = output.exists() and output.stat().st_mtime_ns >= started_ns
        record["output"] = str(output.relative_to(ROOT))
        record["output_fresh"] = fresh
        if fresh:
            record["output_sha256"] = sha256(output)
        else:
            record["status"] = "failed"
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    steps = [
        step for step in CANONICAL_PIPELINE
        if not (args.skip_validate and step["id"] == "validate_datasets")
    ]
    manifest = {
        "schema_version": "1.0",
        "pipeline": "v2_phase1_canonical",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_revision": git_revision(),
        "python": sys.version.split()[0],
        "input_hashes": {
            "voynich_parquet": sha256(
                ROOT / "data/raw/voynich/AncientLanguages_Voynich_snapshot/train.parquet"
            ),
            "dataset_manifest": sha256(ROOT / "data/manifests/dataset_manifest.json"),
        },
        "steps": [],
    }
    for step in steps:
        print(f"\n[{step['id']}] python {' '.join(step['command'])}", flush=True)
        record = run_step(step, args.dry_run)
        manifest["steps"].append(record)
        if record["status"] == "failed":
            break
    manifest["complete"] = bool(manifest["steps"]) and all(
        step["status"] in ("passed", "dry_run") for step in manifest["steps"]
    ) and len(manifest["steps"]) == len(steps)
    if not args.dry_run:
        RESULTS.mkdir(exist_ok=True)
        (RESULTS / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if manifest["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

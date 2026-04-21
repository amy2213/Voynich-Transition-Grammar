#!/usr/bin/env python3
"""
00_validate_datasets.py — Verify all datasets against the manifest.

Run from project root:
    python scripts/00_validate_datasets.py

Checks:
  - All manifest entries have local files
  - Checksums match
  - No proxy datasets mislabeled as historical
  - Reports verified, pending, and missing datasets
"""

import os
import sys
import json
import hashlib
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "data", "manifests", "dataset_manifest.json")

def sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    print("=" * 60)
    print("VOYNICH PROJECT: DATASET VALIDATION REPORT")
    print("=" * 60)

    if not os.path.exists(MANIFEST_PATH):
        print(f"\nERROR: Manifest not found at {MANIFEST_PATH}")
        print("Run scripts/00_fetch_datasets.py first.")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    verified = []
    proxy = []
    pending = []
    missing = []
    checksum_fail = []
    mislabeled = []

    for entry in manifest:
        did = entry["dataset_id"]
        lang = entry["language"]
        local_path = os.path.join(PROJECT_ROOT, entry["local_path"], entry["file_name"])

        # Check file exists
        if not os.path.exists(local_path):
            missing.append(entry)
            continue

        # Check checksum
        actual_sha = sha256(local_path)
        expected_sha = entry.get("checksum_sha256", "")
        if expected_sha and actual_sha != expected_sha:
            checksum_fail.append((entry, actual_sha))
            continue

        # Check for mislabeled proxies
        if entry["proxy_status"] == "yes" and entry["historical_or_modern"] == "historical":
            mislabeled.append(entry)

        # Categorize
        if "pending" in entry["local_path"]:
            pending.append(entry)
        elif entry["proxy_status"] == "yes":
            proxy.append(entry)
        else:
            verified.append(entry)

    # Report
    print(f"\n--- VERIFIED DATASETS ({len(verified)}) ---")
    for e in verified:
        print(f"  ✓ {e['language']:<20} {e['file_name']}")

    print(f"\n--- PROXY DATASETS ({len(proxy)}) ---")
    for e in proxy:
        print(f"  ~ {e['language']:<20} {e['file_name']}  [modern proxy, NOT historical]")

    print(f"\n--- PENDING VERIFICATION ({len(pending)}) ---")
    for e in pending:
        print(f"  ? {e['language']:<20} {e['file_name']}")

    print(f"\n--- MISSING FILES ({len(missing)}) ---")
    for e in missing:
        path = os.path.join(PROJECT_ROOT, e["local_path"], e["file_name"])
        print(f"  ✗ {e['language']:<20} expected at: {path}")

    print(f"\n--- CHECKSUM FAILURES ({len(checksum_fail)}) ---")
    for e, actual in checksum_fail:
        print(f"  ✗ {e['language']:<20} expected: {e['checksum_sha256'][:16]}... got: {actual[:16]}...")

    print(f"\n--- MISLABELED PROXIES ({len(mislabeled)}) ---")
    for e in mislabeled:
        print(f"  ! {e['language']:<20} marked historical but proxy_status=yes")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Verified:          {len(verified)}")
    print(f"  Proxy (verified):  {len(proxy)}")
    print(f"  Pending:           {len(pending)}")
    print(f"  Missing:           {len(missing)}")
    print(f"  Checksum failures: {len(checksum_fail)}")
    print(f"  Mislabeled:        {len(mislabeled)}")
    total_ok = len(verified) + len(proxy)
    print(f"  Total usable:      {total_ok}")

    # Languages NOT in manifest that were claimed
    claimed_not_present = []
    for lang in ["Old French", "Medieval Italian", "Latin (Caesar)"]:
        if not any(e["language"] == lang for e in manifest):
            claimed_not_present.append(lang)
    if claimed_not_present:
        print(f"\n--- CLAIMED BUT NOT IN MANIFEST ---")
        for lang in claimed_not_present:
            print(f"  ! {lang} — referenced in earlier analysis but no frozen dataset")

    if checksum_fail or mislabeled:
        print(f"\n⚠ VALIDATION ISSUES FOUND. Review above.")
        return 1
    if missing:
        print(f"\n⚠ {len(missing)} dataset(s) missing. Run scripts/00_fetch_datasets.py to download.")
        print(f"  This is expected in CI or lightweight clones where data is not bundled.")
        return 0  # Not fatal — missing data is expected in some contexts
    else:
        print(f"\n✓ All datasets validated successfully.")
        return 0

if __name__ == "__main__":
    sys.exit(main())

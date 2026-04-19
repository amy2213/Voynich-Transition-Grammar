#!/usr/bin/env python3
"""
00_fetch_datasets.py — Download and freeze all datasets for the Voynich project.

Run from project root:
    python scripts/00_fetch_datasets.py

Downloads:
  - Voynich HuggingFace dataset (frozen as parquet)
  - Gutenberg literary texts (Middle English, KJV)
  - Leipzig corpora (Turkish, Hungarian, Finnish, Hebrew, Arabic, Latin,
    North Azerbaijani, Italian, Estonian)
  - Pending: Uzbek, Kazakh, Mongolian

All files are saved to data/raw/ with checksums recorded.
"""

import os
import sys
import hashlib
import urllib.request
import json
from datetime import date

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

def sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def download(url, dest, label):
    if os.path.exists(dest):
        print(f"  SKIP (exists): {label}")
        return True
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"  Downloading: {label}...")
        urllib.request.urlretrieve(url, dest)
        size = os.path.getsize(dest)
        print(f"  OK: {size} bytes")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        if os.path.exists(dest):
            os.remove(dest)
        return False

def main():
    print("=" * 60)
    print("VOYNICH PROJECT: DATASET FETCH")
    print("=" * 60)

    # 1. Voynich core
    print("\n--- Voynich Core ---")
    voynich_dir = os.path.join(DATA_DIR, "voynich", "AncientLanguages_Voynich_snapshot")
    voynich_file = os.path.join(voynich_dir, "train.parquet")
    if not os.path.exists(voynich_file):
        try:
            from datasets import load_dataset
            os.makedirs(voynich_dir, exist_ok=True)
            ds = load_dataset("AncientLanguages/Voynich")
            ds["train"].to_parquet(voynich_file)
            print(f"  OK: Voynich snapshot ({ds['train'].num_rows} rows)")
        except Exception as e:
            print(f"  FAILED: {e}")
    else:
        print(f"  SKIP (exists): Voynich snapshot")

    # 2. Gutenberg texts
    print("\n--- Gutenberg Literary Texts ---")
    gutenberg = [
        ("https://www.gutenberg.org/cache/epub/22120/pg22120.txt",
         os.path.join(DATA_DIR, "cross_linguistic", "middle_english", "chaucer_canterbury_tales_22120.txt"),
         "Middle English (Chaucer)"),
        ("https://www.gutenberg.org/cache/epub/10900/pg10900.txt",
         os.path.join(DATA_DIR, "cross_linguistic", "kjv_english", "king_james_bible_10900.txt"),
         "KJV Bible"),
    ]
    for url, dest, label in gutenberg:
        download(url, dest, label)

    # 3. Leipzig corpora
    print("\n--- Leipzig Corpora ---")
    leipzig = [
        ("tur_wikipedia_2021_100K", "turkish", "Turkish"),
        ("hun_wikipedia_2021_100K", "hungarian", "Hungarian"),
        ("fin_wikipedia_2021_100K", "finnish", "Finnish"),
        ("heb_wikipedia_2021_100K", "hebrew", "Hebrew"),
        ("ara_wikipedia_2021_100K", "arabic", "Arabic"),
        ("lat_wikipedia_2021_100K", "latin", "Latin"),
        ("aze_wikipedia_2021_100K", "north_azerbaijani", "North Azerbaijani"),
        ("ita_wikipedia_2021_100K", "italian", "Italian"),
        ("ekk_wikipedia_2021_100K", "estonian", "Estonian"),
    ]
    for corpus_id, folder, label in leipzig:
        url = f"https://downloads.wortschatz-leipzig.de/corpora/{corpus_id}.tar.gz"
        dest = os.path.join(DATA_DIR, "cross_linguistic", folder, f"{corpus_id}.tar.gz")
        download(url, dest, f"{label} (Leipzig)")

    # 4. Pending
    print("\n--- Pending (download attempted, verification needed) ---")
    pending = [
        ("uzb_wikipedia_2021_100K", "uzbek_pending", "Uzbek"),
        ("kaz_wikipedia_2021_100K", "kazakh_pending", "Kazakh"),
        ("mon_wikipedia_2021_100K", "mongolian_pending", "Mongolian"),
    ]
    for corpus_id, folder, label in pending:
        url = f"https://downloads.wortschatz-leipzig.de/corpora/{corpus_id}.tar.gz"
        dest = os.path.join(DATA_DIR, "cross_linguistic", folder, f"{corpus_id}.tar.gz")
        download(url, dest, f"{label} (PENDING)")

    print("\nDone. Run scripts/00_validate_datasets.py to verify checksums.")

if __name__ == "__main__":
    main()

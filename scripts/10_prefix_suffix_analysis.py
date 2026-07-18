#!/usr/bin/env python3
"""Canonical Version 2 matched, boundary-aware prefix/suffix estimator."""

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from _canonical import (
    SequenceUnit,
    affix_clustering_sensitivity_scores,
    bootstrap_groups_to_target,
    load_corpus,
    sample_units_to_target,
    sequence_units,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
ESTIMATOR_VERSION = "2.0.0"
DEFAULT_SEED = 20260718
DEFAULT_REPLICATES = 200
DISCOVERY = {
    "n_families": 5,
    "min_len": 2,
    "max_len": 3,
    "min_coverage": 0.02,
    "max_coverage": 0.20,
    "candidate_pool": 80,
    "min_n": 10,
}
ELEVATION_THRESHOLDS = (1.05, 1.10, 1.15)
RATIO_LOWERS = (0.75, 0.80, 0.85)
RATIO_UPPERS = (1.20, 1.25, 1.30)

LATIN = r"[a-z]+"
LEIPZIG = [
    ("Arabic", "arabic", "ara_wikipedia_2021_100K.tar.gz", r"[\u0621-\u064a]+", "Semitic"),
    ("Latin", "latin", "lat_wikipedia_2021_100K.tar.gz", LATIN, "Indo-European"),
    ("Estonian", "estonian", "ekk_wikipedia_2021_100K.tar.gz", r"[a-zõäöüšž]+", "Uralic"),
    ("Hebrew", "hebrew", "heb_wikipedia_2021_100K.tar.gz", r"[\u05d0-\u05ea]+", "Semitic"),
    ("Finnish", "finnish", "fin_wikipedia_2021_100K.tar.gz", r"[a-zäöå]+", "Uralic"),
    ("Hungarian", "hungarian", "hun_wikipedia_2021_100K.tar.gz", r"[a-záéíóöőúüű]+", "Uralic"),
    ("Turkish", "turkish", "tur_wikipedia_2021_100K.tar.gz", r"[a-zçğıöşü]+", "Turkic"),
    ("Italian", "italian", "ita_wikipedia_2021_100K.tar.gz", r"[a-zàèéìòù]+", "Indo-European"),
    ("North Azerbaijani", "north_azerbaijani", "aze_wikipedia_2021_100K.tar.gz", r"[a-zçəğıöşü]+", "Turkic"),
    ("Swahili", "swahili", "swa_wikipedia_2021_100K.tar.gz", LATIN, "Bantu"),
    ("Georgian", "georgian", "kat_wikipedia_2021_100K.tar.gz", r"[\u10d0-\u10f0]+", "Kartvelian"),
    ("Tagalog", "tagalog", "tgl_wikipedia_2021_100K.tar.gz", LATIN, "Austronesian"),
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


def display_path(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def tokenize(text, pattern):
    return tuple(word for word in re.findall(pattern, text.lower()) if len(word) >= 2)


def load_leipzig(label, folder, archive, pattern):
    path = RAW / "cross_linguistic" / folder / archive
    units = []
    with tarfile.open(path, "r:gz") as bundle:
        member = next(item for item in bundle.getmembers()
                      if item.name.endswith("-sentences.txt"))
        handle = bundle.extractfile(member)
        if handle is None:
            raise RuntimeError(f"could not read {member.name}")
        for index, raw_line in enumerate(handle):
            line = raw_line.decode("utf-8", errors="ignore").rstrip("\n")
            sentence = line.split("\t", 1)[1] if "\t" in line else line
            tokens = tokenize(sentence, pattern)
            if tokens:
                units.append(SequenceUnit(
                    unit_id=f"{folder}:{index}", tokens=tokens,
                    boundary_type="sentence", document=archive,
                ))
    return units, [path]


def strip_gutenberg(text):
    start = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", text, re.I)
    if start:
        text = text[start.end():]
    end = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", text, re.I)
    if end:
        text = text[:end.start()]
    return text


def load_gutenberg(folder, filename):
    path = RAW / "cross_linguistic" / folder / filename
    text = strip_gutenberg(path.read_text(encoding="utf-8", errors="ignore"))
    units = []
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+|\n\s*\n", text)):
        tokens = tokenize(sentence, LATIN)
        if tokens:
            units.append(SequenceUnit(
                unit_id=f"{folder}:{index}", tokens=tokens,
                boundary_type="sentence", document=filename,
            ))
    return units, [path]


def load_conllu(folder, filenames):
    paths = [RAW / "cross_linguistic" / folder / name for name in filenames]
    units = []
    sentence = []
    sentence_index = 0
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() + [""]:
            if not line.strip():
                if sentence:
                    units.append(SequenceUnit(
                        unit_id=f"{path.stem}:{sentence_index}",
                        tokens=tuple(sentence), boundary_type="sentence",
                        document=path.name,
                    ))
                    sentence_index += 1
                    sentence = []
                continue
            if line.startswith("#") or "\t" not in line:
                continue
            fields = line.split("\t")
            if fields[0].isdigit():
                word = fields[1].lower()
                if len(word) >= 2:
                    sentence.append(word)
    return units, paths


def corpus_inventory():
    corpora = {}
    for label, folder, archive, pattern, family in LEIPZIG:
        units, paths = load_leipzig(label, folder, archive, pattern)
        corpora[label] = {"family": family, "units": units, "paths": paths,
                          "source_type": "Leipzig sentence records"}
    for label, folder, filename in (
        ("Middle English", "middle_english", "chaucer_canterbury_tales_22120.txt"),
        ("KJV English", "kjv_english", "king_james_bible_10900.txt"),
    ):
        units, paths = load_gutenberg(folder, filename)
        corpora[label] = {"family": "Indo-European", "units": units,
                          "paths": paths, "source_type": "Gutenberg sentence segments"}
    units, paths = load_conllu(
        "ottoman_turkish", ("ota_dudu_train.conllu", "ota_dudu_test.conllu"))
    corpora["Ottoman Turkish"] = {
        "family": "Turkic", "units": units, "paths": paths,
        "source_type": "CoNLL-U sentences",
    }
    return corpora


def compact_score(units):
    sequences = [unit.tokens for unit in units]
    estimates = affix_clustering_sensitivity_scores(sequences, **DISCOVERY)
    primary = estimates["primary_excludes_other"]
    sensitivity = estimates["sensitivity_includes_other"]
    return {
        "prefix_sc": primary["prefix"]["score"],
        "suffix_sc": primary["suffix"]["score"],
        "ratio": primary["ratio"],
        "minimum_sc": primary["minimum"],
        "prefix_affixes": primary["prefix"]["affixes"],
        "suffix_affixes": primary["suffix"]["affixes"],
        "transition_n": primary["prefix"]["transition_n"],
        "include_other": {
            "prefix_sc": sensitivity["prefix"]["score"],
            "suffix_sc": sensitivity["suffix"]["score"],
            "ratio": sensitivity["ratio"],
            "minimum_sc": sensitivity["minimum"],
        },
    }


def percentile(values, q):
    return float(np.percentile(np.asarray(values, dtype=float), q))


def summarize(replicates, key, nested=None):
    values = [record[nested][key] if nested else record[key] for record in replicates]
    values = [value for value in values if value is not None]
    return {
        "median": percentile(values, 50),
        "ci95": [percentile(values, 2.5), percentile(values, 97.5)],
        "replicate_n": len(values),
    }


def bucket(prefix, suffix, elevation=1.10, lower=0.80, upper=1.25):
    if prefix is None or suffix is None or suffix == 0:
        return "UNDEFINED"
    ratio = prefix / suffix
    if prefix > elevation and suffix > elevation:
        if lower <= ratio <= upper:
            return "SYMM-HIGH"
        return "PREFIX-DOM" if ratio > upper else "SUFFIX-DOM"
    if prefix > elevation:
        return "PREFIX-DOM"
    if suffix > elevation:
        return "SUFFIX-DOM"
    return "SYMM-LOW"


def threshold_grid(replicates):
    cells = []
    for elevation in ELEVATION_THRESHOLDS:
        for lower in RATIO_LOWERS:
            for upper in RATIO_UPPERS:
                counts = Counter(bucket(r["prefix_sc"], r["suffix_sc"],
                                        elevation, lower, upper)
                                 for r in replicates)
                cells.append({
                    "elevation": elevation, "ratio_lower": lower,
                    "ratio_upper": upper,
                    "bucket_counts": dict(sorted(counts.items())),
                    "symm_high_probability": counts["SYMM-HIGH"] / len(replicates),
                })
    return cells


def sign_pvalue(differences):
    n = len(differences)
    nonpositive = sum(value <= 0 for value in differences)
    nonnegative = sum(value >= 0 for value in differences)
    return min(1.0, 2 * min((nonpositive + 1) / (n + 1),
                            (nonnegative + 1) / (n + 1)))


def bh_adjust(records):
    ordered = sorted(enumerate(records), key=lambda item: item[1]["p_empirical"])
    adjusted = [None] * len(records)
    running = 1.0
    m = len(records)
    for reverse_index in range(m - 1, -1, -1):
        original_index, record = ordered[reverse_index]
        rank = reverse_index + 1
        running = min(running, record["p_empirical"] * m / rank)
        adjusted[original_index] = min(1.0, running)
    for record, value in zip(records, adjusted):
        record["p_bh_comparator_family"] = value


def system_summary(replicates):
    return {
        "primary_excludes_other": {
            key: summarize(replicates, key)
            for key in ("prefix_sc", "suffix_sc", "ratio", "minimum_sc")
        },
        "sensitivity_includes_other": {
            key: summarize(replicates, key, "include_other")
            for key in ("prefix_sc", "suffix_sc", "ratio", "minimum_sc")
        },
        "modal_prefix_affixes": Counter(tuple(r["prefix_affixes"]) for r in replicates).most_common(1)[0][0],
        "modal_suffix_affixes": Counter(tuple(r["suffix_affixes"]) for r in replicates).most_common(1)[0][0],
        "threshold_sensitivity": threshold_grid(replicates),
        "replicates": replicates,
    }


def write_csv(path, systems):
    fields = ["system", "status", "family", "available_tokens", "natural_units",
              "prefix_median", "prefix_ci_low", "prefix_ci_high",
              "suffix_median", "suffix_ci_low", "suffix_ci_high",
              "ratio_median", "minimum_sc_median", "other_minimum_sc_median"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name, record in systems.items():
            row = {"system": name, "status": record["status"],
                   "family": record["family"],
                   "available_tokens": record["available_tokens"],
                   "natural_units": record["natural_units"]}
            if record["status"] == "eligible":
                primary = record["summary"]["primary_excludes_other"]
                row.update({
                    "prefix_median": primary["prefix_sc"]["median"],
                    "prefix_ci_low": primary["prefix_sc"]["ci95"][0],
                    "prefix_ci_high": primary["prefix_sc"]["ci95"][1],
                    "suffix_median": primary["suffix_sc"]["median"],
                    "suffix_ci_low": primary["suffix_sc"]["ci95"][0],
                    "suffix_ci_high": primary["suffix_sc"]["ci95"][1],
                    "ratio_median": primary["ratio"]["median"],
                    "minimum_sc_median": primary["minimum_sc"]["median"],
                    "other_minimum_sc_median": record["summary"]["sensitivity_includes_other"]["minimum_sc"]["median"],
                })
            writer.writerow(row)


def write_markdown(path, systems, comparisons):
    comparison_map = {record["comparator"]: record for record in comparisons}
    lines = [
        "# Version 2 prefix/suffix comparison", "",
        "Primary estimates exclude `OTHER`. Intervals are replicate percentile intervals. Buckets are secondary.", "",
        "| System | Status | Tokens | Prefix SC, median [95% interval] | Suffix SC, median [95% interval] | Minimum SC | Voynich minus comparator minimum SC | BH p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, record in systems.items():
        if record["status"] != "eligible":
            lines.append(f"| {name} | ineligible | {record['available_tokens']} |  |  |  |  |  |")
            continue
        primary = record["summary"]["primary_excludes_other"]
        prefix = primary["prefix_sc"]
        suffix = primary["suffix_sc"]
        comp = comparison_map.get(name)
        delta = "target" if comp is None else f"{comp['minimum_sc_difference']['median']:.3f}"
        pvalue = "" if comp is None else f"{comp['p_bh_comparator_family']:.4f}"
        lines.append(
            f"| {name} | eligible | {record['available_tokens']} | "
            f"{prefix['median']:.3f} [{prefix['ci95'][0]:.3f}, {prefix['ci95'][1]:.3f}] | "
            f"{suffix['median']:.3f} [{suffix['ci95'][0]:.3f}, {suffix['ci95'][1]:.3f}] | "
            f"{primary['minimum_sc']['median']:.3f} | {delta} | {pvalue} |"
        )
    lines.extend(["", "This table does not establish language identity or natural-language uniqueness.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_svg(path, systems):
    eligible = [(name, record) for name, record in systems.items()
                if record["status"] == "eligible"]
    width, height = 900, 110 + 28 * len(eligible)
    left, plot_width = 190, 650
    values = []
    for _, record in eligible:
        primary = record["summary"]["primary_excludes_other"]
        values.extend(primary[side]["ci95"] for side in ("prefix_sc", "suffix_sc"))
    flat = [value for pair in values for value in pair]
    xmin, xmax = max(0, min(flat) - 0.1), max(flat) + 0.1
    scale = lambda value: left + (value - xmin) / (xmax - xmin) * plot_width
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;font-size:12px}.title{font-size:17px;font-weight:bold}.axis{stroke:#444;stroke-width:1}.prefix{stroke:#315ea8;fill:#315ea8}.suffix{stroke:#c85a32;fill:#c85a32}</style>',
        '<text x="20" y="26" class="title">Boundary-aware, size-matched prefix and suffix self-clustering</text>',
        '<text x="20" y="46">Median and 95% replicate interval; OTHER excluded</text>',
    ]
    for tick in np.linspace(xmin, xmax, 6):
        x = scale(float(tick))
        svg.extend([f'<line x1="{x:.1f}" y1="62" x2="{x:.1f}" y2="{height-30}" stroke="#ddd"/>',
                    f'<text x="{x:.1f}" y="{height-10}" text-anchor="middle">{tick:.2f}</text>'])
    for index, (name, record) in enumerate(eligible):
        y = 78 + index * 28
        primary = record["summary"]["primary_excludes_other"]
        svg.append(f'<text x="{left-10}" y="{y+4}" text-anchor="end">{name}</text>')
        for offset, side, css in ((-4, "prefix_sc", "prefix"), (4, "suffix_sc", "suffix")):
            item = primary[side]
            lo, hi = map(scale, item["ci95"])
            med = scale(item["median"])
            svg.extend([f'<line x1="{lo:.1f}" y1="{y+offset}" x2="{hi:.1f}" y2="{y+offset}" class="{css}"/>',
                        f'<circle cx="{med:.1f}" cy="{y+offset}" r="3" class="{css}"/>'])
    svg.extend([f'<text x="{left}" y="60" class="prefix">Prefix</text>',
                f'<text x="{left+55}" y="60" class="suffix">Suffix</text>', "</svg>"])
    path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default="results/prefix_suffix_v2.json")
    args = parser.parse_args()
    if args.replicates < 2:
        parser.error("--replicates must be at least 2")

    voynich_units = sequence_units(load_corpus())
    target = sum(len(unit.tokens) for unit in voynich_units)
    corpora = corpus_inventory()
    seed_rng = np.random.default_rng(args.seed)
    seed_schedule = {
        "VOYNICH": seed_rng.integers(0, 2**63 - 1, args.replicates).tolist()
    }
    for name in sorted(corpora):
        seed_schedule[name] = seed_rng.integers(0, 2**63 - 1, args.replicates).tolist()

    print(f"Estimator {ESTIMATOR_VERSION}; target={target}; replicates={args.replicates}")
    voy_replicates = []
    for index, seed in enumerate(seed_schedule["VOYNICH"], 1):
        sample = bootstrap_groups_to_target(
            voynich_units, "page", target, np.random.default_rng(seed))
        voy_replicates.append(compact_score(sample))
        if index % 25 == 0 or index == args.replicates:
            print(f"  VOYNICH {index}/{args.replicates}", flush=True)

    systems = {
        "VOYNICH": {
            "status": "eligible", "family": "Target system",
            "available_tokens": target, "natural_units": len(voynich_units),
            "boundary_unit": "line nested in page bootstrap block",
            "summary": system_summary(voy_replicates),
        }
    }
    input_paths = [Path(__import__("_canonical").PARQUET_PATH)]
    for name, corpus in corpora.items():
        units = corpus["units"]
        available = sum(len(unit.tokens) for unit in units)
        input_paths.extend(corpus["paths"])
        record = {
            "status": "eligible" if available >= target else "ineligible_too_small",
            "family": corpus["family"], "available_tokens": available,
            "natural_units": len(units), "boundary_unit": corpus["source_type"],
        }
        if available >= target:
            replicates = []
            for index, seed in enumerate(seed_schedule[name], 1):
                sample = sample_units_to_target(units, target, np.random.default_rng(seed))
                replicates.append(compact_score(sample))
                if index % 25 == 0 or index == args.replicates:
                    print(f"  {name} {index}/{args.replicates}", flush=True)
            record["summary"] = system_summary(replicates)
        else:
            record["reason"] = f"{available} tokens is below exact target {target}; no padding or replacement"
        systems[name] = record

    comparisons = []
    for name, record in systems.items():
        if name == "VOYNICH" or record["status"] != "eligible":
            continue
        comparator_reps = record["summary"]["replicates"]
        differences = [v["minimum_sc"] - c["minimum_sc"]
                       for v, c in zip(voy_replicates, comparator_reps)]
        comparisons.append({
            "comparator": name,
            "minimum_sc_difference": {
                "direction": "VOYNICH minus comparator",
                "median": percentile(differences, 50),
                "ci95": [percentile(differences, 2.5), percentile(differences, 97.5)],
            },
            "voynich_exceeds_both_sides_probability": sum(
                v["prefix_sc"] > c["prefix_sc"] and v["suffix_sc"] > c["suffix_sc"]
                for v, c in zip(voy_replicates, comparator_reps)
            ) / args.replicates,
            "p_empirical": sign_pvalue(differences),
            "test": "two-sided corrected replicate sign test",
        })
    bh_adjust(comparisons)

    output_path = ROOT / args.out
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table_csv = RESULTS / "prefix_suffix_v2.csv"
    table_md = RESULTS / "prefix_suffix_v2.md"
    figure_svg = RESULTS / "prefix_suffix_v2.svg"
    command = " ".join(["python", "scripts/10_prefix_suffix_analysis.py",
                        "--replicates", str(args.replicates), "--seed", str(args.seed),
                        "--out", args.out])
    payload = {
        "schema_version": "2.0",
        "estimator_version": ESTIMATOR_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope_warning": "This comparison does not establish decipherment, language identity, natural-language uniqueness, or exclusion of untested mechanisms.",
        "method": {
            "target_tokens": target, "replicates": args.replicates,
            "voynich_resampling": "page-block bootstrap preserving separate lines",
            "comparator_resampling": "natural units without replacement to exact target; final unit is a separate contiguous fragment",
            "adjacency": "within natural sequence units only",
            "primary_other_policy": "excluded from unweighted discovered-family mean",
            "sensitivity_other_policy": "included in mean",
            "discovery": DISCOVERY,
            "threshold_grid": {"elevation": ELEVATION_THRESHOLDS,
                               "ratio_lower": RATIO_LOWERS,
                               "ratio_upper": RATIO_UPPERS},
            "multiplicity": f"Benjamini-Hochberg across {len(comparisons)} eligible comparator tests",
        },
        "provenance": {
            "command": command, "master_seed": args.seed,
            "replicate_seeds": seed_schedule, "code_revision": git_revision(),
            "input_sha256": {str(path.relative_to(ROOT)): sha256(path)
                             for path in sorted(set(input_paths))},
            "code_sha256": {
                "scripts/10_prefix_suffix_analysis.py": sha256(Path(__file__)),
                "scripts/_canonical.py": sha256(ROOT / "scripts" / "_canonical.py"),
                "docs/v2/prefix_suffix_estimator_spec.md": sha256(ROOT / "docs" / "v2" / "prefix_suffix_estimator_spec.md"),
            },
        },
        "systems": systems,
        "comparisons": comparisons,
        "generated_outputs": [display_path(path) for path in
                              (output_path, table_csv, table_md, figure_svg)],
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(table_csv, systems)
    write_markdown(table_md, systems, comparisons)
    write_svg(figure_svg, systems)
    print(f"Wrote {display_path(output_path)} and generated table/figure outputs")


if __name__ == "__main__":
    raise SystemExit(main())

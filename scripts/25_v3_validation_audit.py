#!/usr/bin/env python3
"""Audit Version 3 output against the declared scientific controls."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def nested_suffix(left, right):
    return left.endswith(right) or right.endswith(left)


def neutral_status(summary):
    low, high = summary["ci95"]
    if high < 1.0:
        return "below-neutral interval"
    if low > 1.0:
        return "above-neutral interval"
    return "interval crosses neutral"


def fmt_summary(summary):
    low, high = summary["ci95"]
    return (
        f"{summary['median']:.3f} [{low:.3f}, {high:.3f}], "
        f"fraction >=1: {summary['fraction_at_or_above_neutral']:.3f}"
    )


def audit_profile(name, profile, expected_replicates):
    failures = []
    systems = profile["systems"]
    if profile["replicate_n"] != expected_replicates:
        failures.append(
            f"{name}: profile replicate_n={profile['replicate_n']} "
            f"expected {expected_replicates}"
        )

    for system, record in systems.items():
        summary = record["summary"]
        for metric in (
            "prefix_order_ratio",
            "suffix_order_ratio",
            "minimum_order_ratio",
            "prefix_to_suffix_ratio",
            "prefix_unweighted_mean_class_ratio",
            "suffix_unweighted_mean_class_ratio",
        ):
            metric_summary = summary[metric]
            if metric_summary["replicate_n"] != expected_replicates:
                failures.append(
                    f"{name}/{system}/{metric}: "
                    f"{metric_summary['replicate_n']} usable replicates"
                )
            if any(value is None for value in metric_summary["ci95"]):
                failures.append(
                    f"{name}/{system}/{metric}: missing interval"
                )

        suffixes = summary["modal_suffix_affixes"]
        for i, left in enumerate(suffixes):
            for right in suffixes[i + 1:]:
                if nested_suffix(left, right):
                    failures.append(
                        f"{name}/{system}: nested modal suffixes "
                        f"{left!r}, {right!r}"
                    )

        for side in ("prefix", "suffix"):
            low, high = summary["included_class_n_range"][side]
            if low < 1 or high > 5:
                failures.append(
                    f"{name}/{system}: invalid {side} class range "
                    f"{[low, high]}"
                )

    return failures


def render_profile(title, profile):
    lines = [
        f"## {title}",
        "",
        f"Target tokens: {profile['target_tokens']:,}",
        "",
        "| System | Prefix order ratio | Suffix order ratio | Minimum | Neutral status |",
        "|---|---:|---:|---:|---|",
    ]
    for system, record in profile["systems"].items():
        summary = record["summary"]
        prefix = summary["prefix_order_ratio"]
        suffix = summary["suffix_order_ratio"]
        minimum = summary["minimum_order_ratio"]
        lines.append(
            f"| {system} | {fmt_summary(prefix)} | {fmt_summary(suffix)} | "
            f"{fmt_summary(minimum)} | {neutral_status(minimum)} |"
        )
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/prefix_suffix_v3_validation.json",
    )
    parser.add_argument(
        "--out",
        default="results/prefix_suffix_v3_validation_audit.md",
    )
    args = parser.parse_args()

    source = ROOT / args.input
    data = json.loads(source.read_text(encoding="utf-8"))

    expected_replicates = data["method"]["matched_subsample_replicates"]
    failures = []

    if data["status"] != "validated descriptive scientific result; finite-corpus scope":
        failures.append("result status does not match the frozen Version 3 scope")

    if data["method"]["cross_system_p_values"] != "none":
        failures.append("cross-system p-values are present")

    if data["method"]["replicate_pairing"] != (
        "none; indices have no cross-system meaning"
    ):
        failures.append("replicate-pairing guard changed")

    line_profile = data["matched_analyses"]["line_deletion_stability"]
    all_profile = data["matched_analyses"]["all_system_small_target"]
    page_profile = data["voynich_cluster_robustness"][
        "page_block_bootstrap"
    ]

    expected_line = sorted(
        name for name in data["full_corpus"]
        if name != "Ottoman Turkish"
    )
    if sorted(line_profile["systems"]) != expected_line:
        failures.append(
            "line-deletion profile does not contain exactly all systems "
            "except Ottoman Turkish"
        )

    if sorted(all_profile["systems"]) != sorted(data["full_corpus"]):
        failures.append("all-system profile is missing or adding systems")

    failures.extend(
        audit_profile(
            "line_deletion_stability",
            line_profile,
            expected_replicates,
        )
    )
    failures.extend(
        audit_profile(
            "all_system_small_target",
            all_profile,
            expected_replicates,
        )
    )

    if page_profile["replicate_n"] != expected_replicates:
        failures.append(
            "Voynich page bootstrap replicate count does not match "
            "declared validation count"
        )
    if page_profile.get("group_attribute") != "page":
        failures.append("Voynich cluster robustness is not grouped by page")
    page_summary = page_profile["summary"]
    for metric in (
        "prefix_order_ratio",
        "suffix_order_ratio",
        "minimum_order_ratio",
    ):
        if page_summary[metric]["replicate_n"] != expected_replicates:
            failures.append(
                f"Voynich page bootstrap {metric} has incomplete replicates"
            )

    if "comparator_boundary_policy" not in data["method"]:
        failures.append("comparator boundary-safe tokenization policy missing")

    for system, record in data["full_corpus"].items():
        if system == "VOYNICH":
            continue
        diagnostics = record.get("tokenization_diagnostics")
        if diagnostics is None:
            failures.append(
                f"{system}: tokenization diagnostics missing"
            )

    repeats = data.get("voynich_exact_repeat_robustness", {})
    if repeats.get("observed_exact_adjacent_repeats") is None:
        failures.append("Voynich exact-repeat robustness is missing")
    repeat_score = repeats.get(
        "score_after_breaking_at_exact_repeat_pairs", {}
    )
    if repeat_score.get("suffix_order_ratio") is None:
        failures.append(
            "Voynich exact-repeat suffix robustness score is missing"
        )

    line_voynich = line_profile["systems"]["VOYNICH"]["summary"]
    all_voynich = all_profile["systems"]["VOYNICH"]["summary"]

    comparator_names = [
        name for name in line_profile["systems"]
        if name != "VOYNICH"
    ]
    line_below_median = [
        name for name in comparator_names
        if line_profile["systems"][name]["summary"]
        ["minimum_order_ratio"]["median"] < 1.0
    ]
    line_below_interval = [
        name for name in comparator_names
        if line_profile["systems"][name]["summary"]
        ["minimum_order_ratio"]["ci95"][1] < 1.0
    ]

    lines = [
        "# Version 3 validation audit",
        "",
        f"Source: `{args.input}`",
        f"Replicates per matched profile: {expected_replicates}",
        "",
        "## Mechanical audit",
        "",
    ]
    if failures:
        lines.append(f"**FAIL: {len(failures)} validation defect(s).**")
        lines.extend(f"- {item}" for item in failures)
    else:
        lines.append(
            "**PASS:** output is structurally complete under the declared "
            "Version 3 validation rules."
        )

    lines.extend([
        "",
        "## Voynich neutral-value diagnostics",
        "",
        "- Page-block prefix: "
        + fmt_summary(page_summary["prefix_order_ratio"])
        + " (" + neutral_status(page_summary["prefix_order_ratio"]) + ")",
        "- Page-block suffix: "
        + fmt_summary(page_summary["suffix_order_ratio"])
        + " (" + neutral_status(page_summary["suffix_order_ratio"]) + ")",
        "- Page-block minimum: "
        + fmt_summary(page_summary["minimum_order_ratio"])
        + " (" + neutral_status(page_summary["minimum_order_ratio"]) + ")",
        "- Line-deletion prefix (stability only): "
        + fmt_summary(line_voynich["prefix_order_ratio"]),
        "- All-system small-target minimum: "
        + fmt_summary(all_voynich["minimum_order_ratio"])
        + " (" + neutral_status(all_voynich["minimum_order_ratio"]) + ")",
        "",
        "## Comparator pattern in the line-deletion sensitivity",
        "",
        f"- Comparators with minimum-side median below 1.0: "
        f"{len(line_below_median)}/{len(comparator_names)}.",
        f"- Comparators whose entire 95% minimum-side interval is below 1.0: "
        f"{len(line_below_interval)}/{len(comparator_names)}.",
        "",
        "## Exact-repeat robustness",
        "",
        f"- Observed exact adjacent repeats: "
        f"{repeats['observed_exact_adjacent_repeats']}.",
        f"- Expected exact adjacent repeats under within-unit shuffle: "
        f"{repeats['expected_exact_adjacent_repeats_under_within_unit_shuffle']:.3f}.",
        f"- Suffix ratio after breaking every exact adjacent repeat pair: "
        f"{repeat_score['suffix_order_ratio']:.3f}.",
        "",
    ])

    lines.extend(render_profile(
        "Line-deletion stability sensitivity",
        line_profile,
    ))
    lines.append("")
    lines.extend(render_profile(
        "All-system small-target sensitivity",
        all_profile,
    ))
    lines.extend([
        "",
        "## Claim gate",
        "",
        "No claim is promoted automatically. The mechanical audit can pass "
        "while the scientific interpretation remains bounded or null. Human "
        "review must consider interval overlap, comparator scope, corpus "
        "mismatch, affix discovery sensitivity, and the finite tested set.",
        "",
    ])

    output = ROOT / args.out
    output.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

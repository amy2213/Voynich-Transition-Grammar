#!/usr/bin/env python3
"""
test_canonical_values.py — Regression tests for published findings.

These tests verify that the results/*.json files produced by the pipeline
match the canonical numbers that appear in the README, paper, and dashboard,
within a stated tolerance. They are intended to catch silent drift —
situations where a well-meaning code change alters a number by 1% and
nobody notices until a reviewer does.

Run directly:
    python tests/test_canonical_values.py

Run under pytest (preferred, gives per-test output):
    pytest tests/test_canonical_values.py -v

Run as part of the full pipeline:
    python run_all.py --tests

Tolerances are deliberately generous. The methodology has known sources of
run-to-run variation (token parsing ~10-15%, as documented in
docs/durable_findings.md § "Methodological Caveats"). Tolerances here are
set to the tighter of:
  (a) 5% relative for well-defined numbers
  (b) ~0.02-0.05 absolute for ratios in the 1–3x range
so that genuine drift is caught but normal variation is not flagged.

Each test has a docstring stating the published value, its source, and the
tolerance rationale.
"""

import json
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def _load(filename: str) -> dict:
    """Load a results JSON, or skip the test with a clear message."""
    path = RESULTS_DIR / filename
    if not path.exists():
        raise unittest.SkipTest(
            f"{filename} not found. Run `python run_all.py` first to generate results."
        )
    with open(path) as f:
        return json.load(f)


class TestTransitionRules(unittest.TestCase):
    """
    Findings from README § "Two distributed transition rules" and
    docs/durable_findings.md § 1.1.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("core_analysis_results.json")

    def test_chedy_to_qok_attraction(self):
        """
        Published: CHEDY→QOK = 2.625x (split-half range [2.34, 2.67]).
        Tolerance: ±0.15 absolute, generous to allow for shuffle-seed variation.
        """
        ratio = self.data["transition_rules"]["CHEDY\u2192QOK"]["ratio"]
        self.assertAlmostEqual(ratio, 2.625, delta=0.15,
            msg=f"CHEDY→QOK drift: expected 2.625 ±0.15, got {ratio}")

    def test_aiin_to_qok_repulsion(self):
        """
        Published: AIIN→QOK = 0.504x (split-half range [0.39, 0.53]).
        Tolerance: ±0.05 absolute.
        """
        ratio = self.data["transition_rules"]["AIIN\u2192QOK"]["ratio"]
        self.assertAlmostEqual(ratio, 0.504, delta=0.05,
            msg=f"AIIN→QOK drift: expected 0.504 ±0.05, got {ratio}")

    def test_chedy_qok_obs_count(self):
        """
        Published: observed CHEDY→QOK count = 626. This is a raw token
        count and should be deterministic across runs (no shuffle).
        Tolerance: 0 (exact match required).
        """
        obs = self.data["transition_rules"]["CHEDY\u2192QOK"]["obs"]
        self.assertEqual(obs, 626,
            msg=f"CHEDY→QOK observed count drift: expected exactly 626, got {obs}")

    def test_unique_chedy_qok_pairs(self):
        """
        Published: 369 unique CHEDY→QOK token pairs.
        Deterministic across runs — exact match expected.
        """
        pairs = self.data["token_grammar"]["unique_pairs"]
        self.assertEqual(pairs, 369,
            msg=f"Unique pair count drift: expected 369, got {pairs}")

    def test_chedy_token_participation(self):
        """
        Published: 77% of CHEDY tokens attract QOK.
        Tolerance: ±3 percentage points.
        """
        pct = self.data["token_grammar"]["chedy_pct"]
        self.assertAlmostEqual(pct, 77.0, delta=3.0,
            msg=f"CHEDY participation drift: expected 77% ±3, got {pct}%")


class TestAIINInvariance(unittest.TestCase):
    """
    Findings from README § "AIIN density is a structural constant"
    and docs/durable_findings.md § 1.2.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("core_analysis_results.json")

    def test_currier_a_mean(self):
        """
        Published: Currier A pages show AIIN at 15.0%.
        Tolerance: ±0.5 percentage points.
        """
        m = self.data["aiin_invariance"]["currier_a_mean"]
        self.assertAlmostEqual(m, 15.0, delta=0.5,
            msg=f"Currier A AIIN mean drift: expected 15.0% ±0.5, got {m}%")

    def test_currier_b_mean(self):
        """
        Published: Currier B pages show AIIN at 15.0%.
        Tolerance: ±0.5 percentage points.
        """
        m = self.data["aiin_invariance"]["currier_b_mean"]
        self.assertAlmostEqual(m, 15.0, delta=0.5,
            msg=f"Currier B AIIN mean drift: expected 15.0% ±0.5, got {m}%")

    def test_ks_test_nonsignificant(self):
        """
        Published: KS p = 0.742 (A/B indistinguishable).
        Test: p > 0.05, meaning the invariance claim holds.
        We don't pin the exact p-value (it's somewhat sensitive to
        page-threshold filtering) but it must be well above 0.05.
        """
        p = self.data["aiin_invariance"]["ks_p"]
        self.assertGreater(p, 0.05,
            msg=f"KS p dropped below 0.05: invariance claim no longer holds (p={p})")


class TestSelfClustering(unittest.TestCase):
    """
    Findings from README § "Limitations" (method-sensitivity disclosure)
    and docs/durable_findings.md § 2.3.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("core_analysis_results.json")

    def test_pooled_backbone_self_clustering(self):
        """
        Published: Pooled backbone SC = 1.451x.
        Tolerance: ±0.1 absolute.
        """
        sc = self.data["self_clustering"]["backbone"]
        self.assertAlmostEqual(sc, 1.451, delta=0.1,
            msg=f"Pooled backbone SC drift: expected 1.451 ±0.1, got {sc}")

    def test_page_level_self_clustering_is_lower(self):
        """
        Published: Page-level SC = 0.929x, lower than pooled.
        This asymmetry is the core of the "method-sensitive" caveat.
        If page-level ever exceeds pooled, the caveat needs rewriting.
        """
        pooled = self.data["self_clustering"]["backbone"]
        page = self.data["self_clustering"]["page_level"]
        self.assertLess(page, pooled,
            msg=f"Page-level SC ({page}) should be lower than pooled ({pooled}). "
                "If this flips, the method-sensitivity caveat needs revision.")


class TestPrefixSuffixSymmetry(unittest.TestCase):
    """
    The central cross-linguistic finding: Voynich is the only system with
    symmetric-high self-clustering. From results/prefix_suffix_analysis.json.
    Published in README § "Bidirectional self-clustering symmetry" and
    docs/durable_findings.md § 1.3.

    This file is precomputed from an earlier analysis pass and is not
    regenerated by the current pipeline, so these tests guard against
    accidental hand-editing or corruption of the file.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("prefix_suffix_analysis.json")

    def test_voynich_is_symmetric_high(self):
        """
        Published: Voynich is SYMM-HIGH, prefix/suffix ratio = 0.99.
        This is the central cross-linguistic claim.
        """
        v = self.data["systems"]["VOYNICH"]
        self.assertEqual(v["bucket"], "SYMM-HIGH",
            msg=f"Voynich bucket drift: expected SYMM-HIGH, got {v['bucket']}")
        self.assertAlmostEqual(v["ratio"], 0.99, delta=0.03,
            msg=f"Voynich P/S ratio drift: expected 0.99 ±0.03, got {v['ratio']}")
        self.assertAlmostEqual(v["prefix_sc"], 1.524, delta=0.05)
        self.assertAlmostEqual(v["suffix_sc"], 1.544, delta=0.05)

    def test_voynich_is_unique_symm_high(self):
        """
        Published: Voynich is the ONLY SYMM-HIGH system among all tested.
        If any other system ever tests SYMM-HIGH, the core cross-linguistic
        claim needs rewriting.
        """
        symm_high = [
            name for name, data in self.data["systems"].items()
            if data.get("bucket") == "SYMM-HIGH"
        ]
        self.assertEqual(
            symm_high, ["VOYNICH"],
            msg=f"Uniqueness claim broken: SYMM-HIGH systems = {symm_high}. "
                "If this is intentional, update README and paper § 4."
        )

    def test_all_positive_sc_naturals_are_suffix_dominant(self):
        """
        Published: every natural language with positive self-clustering is
        suffix-dominant. This is the structural argument for Voynich's
        distinctiveness.
        """
        for name, d in self.data["systems"].items():
            if name == "VOYNICH":
                continue
            if d.get("family") == "Control":
                continue
            # "Positive self-clustering" = pooled SC > 1.1 per bucket defs
            if d["prefix_sc"] > 1.1 or d["suffix_sc"] > 1.1:
                self.assertIn(
                    d["bucket"], ("SUFFIX-DOM",),
                    msg=f"{name} has positive SC but is not SUFFIX-DOM "
                        f"(bucket={d['bucket']}). This breaks the central argument."
                )


class TestResultsFilesExist(unittest.TestCase):
    """Basic smoke tests: all canonical result files are present and valid."""

    EXPECTED_FILES = [
        "core_analysis_results.json",
        "cross_linguistic_results.json",
        "prefix_suffix_analysis.json",
        "stress_test_results.json",
        "corpus_size_analysis.json",
        "validation_report.txt",
    ]

    def test_all_canonical_files_present(self):
        for f in self.EXPECTED_FILES:
            path = RESULTS_DIR / f
            self.assertTrue(path.exists(), f"Missing canonical results file: {f}")

    def test_json_files_are_valid(self):
        for f in self.EXPECTED_FILES:
            if not f.endswith(".json"):
                continue
            path = RESULTS_DIR / f
            if not path.exists():
                continue
            try:
                with open(path) as fp:
                    json.load(fp)
            except json.JSONDecodeError as e:
                self.fail(f"{f} is not valid JSON: {e}")


if __name__ == "__main__":
    # When run as a script (not under pytest), use verbose output
    unittest.main(verbosity=2)

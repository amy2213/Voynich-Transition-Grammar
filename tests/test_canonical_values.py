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
        "extended_analysis_results.json",
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


class TestExtendedAnalysis(unittest.TestCase):
    """
    Regression tests for findings 1.4-1.10, produced by
    scripts/04_extended_analysis.py.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("extended_analysis_results.json")

    # --- 1.4 Line-bounded grammar ---

    def test_chedy_qok_within_line(self):
        """Published: within-line CHEDY→QOK = 2.54x. Tolerance: ±0.15."""
        v = self.data["1.4_line_bounded_grammar"]["chedy_qok_within"]
        self.assertAlmostEqual(v, 2.54, delta=0.15,
            msg=f"Within-line CHEDY→QOK drift: expected 2.54 ±0.15, got {v}")

    def test_chedy_qok_cross_line(self):
        """Published: cross-line CHEDY→QOK = 0.85x. Tolerance: ±0.10."""
        v = self.data["1.4_line_bounded_grammar"]["chedy_qok_cross"]
        self.assertAlmostEqual(v, 0.85, delta=0.10,
            msg=f"Cross-line CHEDY→QOK drift: expected 0.85 ±0.10, got {v}")

    def test_grammar_resets_at_line_boundary(self):
        """The defining property: within-line ratio must exceed cross-line ratio."""
        w = self.data["1.4_line_bounded_grammar"]["chedy_qok_within"]
        c = self.data["1.4_line_bounded_grammar"]["chedy_qok_cross"]
        self.assertGreater(w, c + 0.5,
            msg=f"Line-bounded grammar: within ({w}) should exceed cross ({c}) by >0.5")

    def test_template_recurrence_near_chance(self):
        """Published: template recurrence 1.04x above shuffled."""
        v = self.data["1.4_line_bounded_grammar"]["template_recurrence_ratio"]
        self.assertAlmostEqual(v, 1.04, delta=0.15,
            msg=f"Template recurrence drift: expected ~1.04, got {v}")

    # --- 1.5 Suffix agreement ---

    def test_suffix_agreement_chedy_qok(self):
        """Published: CHEDY→QOK suffix agreement = 1.18x."""
        v = self.data["1.5_suffix_agreement"]["CHEDY→QOK"]["ratio"]
        self.assertAlmostEqual(v, 1.18, delta=0.10,
            msg=f"CHEDY→QOK suffix agreement drift: expected 1.18 ±0.10, got {v}")

    def test_suffix_agreement_qok_qok(self):
        """Published: QOK→QOK suffix agreement = 1.41x."""
        v = self.data["1.5_suffix_agreement"]["QOK→QOK"]["ratio"]
        self.assertAlmostEqual(v, 1.41, delta=0.10,
            msg=f"QOK→QOK suffix agreement drift: expected 1.41 ±0.10, got {v}")

    def test_chedy_selects_qok_subtypes(self):
        """Published: Chi² = 36.4, p = 7.2e-5."""
        chi2 = self.data["1.5_suffix_agreement"]["chedy_selects_qok_subtypes"]["chi2"]
        self.assertGreater(chi2, 20,
            msg=f"CHEDY subtype selection Chi² too low: {chi2}")

    # --- 1.6 Multi-feature agreement ---

    def test_multi_feature_ok_ot(self):
        """Published: OK→OT combined 4-feature ratio = 8.74x."""
        v = self.data["1.6_multi_feature_agreement"]["OK→OT"]["all_four_ratio"]
        self.assertGreater(v, 4.0,
            msg=f"OK→OT multi-feature ratio too low: {v}")

    # --- 1.7 Cascades ---

    def test_cascade_chedy_other_chedy(self):
        """Published: CHEDY→OTHER→CHEDY cascade = +80pp."""
        v = self.data["1.7_agreement_cascades"]["chains"]["CHEDY→OTHER→CHEDY"]["cascade_pp"]
        self.assertGreater(v, 50,
            msg=f"CHEDY→OTHER→CHEDY cascade too weak: +{v}pp")

    def test_skip_agreement_qok(self):
        """Published: QOK→[OTHER]→QOK skip agreement = 2.32x."""
        v = self.data["1.7_agreement_cascades"]["skip_agreement"]["QOK→O→QOK"]["ratio"]
        self.assertGreater(v, 1.5,
            msg=f"QOK skip agreement too low: {v}x")

    # --- 1.8 Paradigms ---

    def test_paradigm_connectivity(self):
        """Published: all 50 tested types per family are connected."""
        for fam in ["QOK", "CHEDY", "AIIN"]:
            c = self.data["1.8_productive_paradigms"][fam]["connected_of_top50"]
            self.assertGreaterEqual(c, 45,
                msg=f"{fam} paradigm connectivity too low: {c}/50")

    # --- 1.9 Line position ---

    def test_chedy_avoids_line_final(self):
        """Published: CHEDY line-final residual = -2.7%. Must be negative."""
        v = self.data["1.9_line_position"]["chedy_line_final_residual_pct"]
        self.assertLess(v, 0,
            msg=f"CHEDY line-final residual should be negative, got {v}%")


# ─────────────────────────────────────────────────────────────────────────────
# REPAIR-PASS TESTS: paradigm null, cascade CIs, per-scribe, constructed control
# ─────────────────────────────────────────────────────────────────────────────

class TestParadigmNullModel(unittest.TestCase):
    """
    Regression tests for results/paradigm_null_results.json.

    The paradigm-null test (06_paradigm_null.py) revealed that Voynich's
    log-freq vs edit-1 variant-count correlation does NOT exceed a character-
    trigram null. These tests lock in the finding so future code changes don't
    silently re-introduce the retired "productive morphology" claim.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.data = _load("paradigm_null_results.json")
        except unittest.SkipTest:
            raise

    def test_voynich_correlations_not_clearly_above_null(self):
        """
        The headline finding of the null test: Voynich r values are NOT
        reliably above the trigram null's 95th percentile for all families.
        If any future run produces r values far exceeding null p95 for all
        three families, the "productive paradigm" claim might be worth
        re-examining — but currently it is retired.
        """
        verdicts = self.data["results"]["verdicts"]
        # At least one family should have a verdict classifying it as artifact
        # or not clearly above null. If all three exceed null, the finding has
        # materially changed and this test should be revisited.
        artifact_count = sum(
            1 for fam, v in verdicts.items()
            if isinstance(v, dict) and "artifact" in str(v.get("verdict", "")).lower()
        )
        self.assertGreaterEqual(artifact_count, 1,
            msg="Expected at least one family's correlation to be classified as "
                "indistinguishable from trigram null. If all three families now "
                "clearly exceed null, the Finding 1.8 retirement may need review.")


class TestCascadeUncertainty(unittest.TestCase):
    """
    Regression tests for results/cascade_uncertainty_results.json.

    All five cascades should survive Benjamini-Hochberg FDR at α=0.05.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.data = _load("cascade_uncertainty_results.json")
        except unittest.SkipTest:
            raise

    def test_all_cascades_survive_fdr(self):
        n_passing = self.data["n_chains_surviving_fdr"]
        n_tested = self.data["n_chains_tested"]
        self.assertEqual(n_passing, n_tested,
            msg=f"Cascade FDR drift: {n_passing}/{n_tested} passing BH-FDR at α=0.05")

    def test_flagship_cascade_ci_lower_bound_positive(self):
        """
        CHEDY→OTHER→CHEDY: conservative 95% CI for the cascade magnitude
        must have a positive lower bound. The point estimate is ~+80pp; the
        CI lower bound should be comfortably above zero.
        """
        chains = self.data["chains"]
        flagship = next(c for c in chains if c["chain"] == "CHEDY→OTHER→CHEDY")
        lower = flagship["cascade_pp_ci95_conservative"][0]
        self.assertGreater(lower, 20,
            msg=f"CHEDY→OTHER→CHEDY lower CI bound unexpectedly low: {lower}pp")


class TestPerScribeDecomposition(unittest.TestCase):
    """
    Regression tests for results/per_scribe_results.json.

    The three major hands (1, 2, 3) together produce 94% of the corpus. Each
    should individually test SYMM-HIGH, demonstrating that the bidirectional
    symmetry is not an aggregation artifact.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.data = _load("per_scribe_results.json")
        except unittest.SkipTest:
            raise

    def test_major_hands_symm_high(self):
        """All three major hands (1, 2, 3) individually test SYMM-HIGH."""
        for h in ["1", "2", "3"]:
            bucket = self.data["hands"][h]["bucket"]
            self.assertEqual(bucket, "SYMM-HIGH",
                msg=f"Hand {h} expected SYMM-HIGH, got {bucket}. "
                    "If this changes, the 'not an aggregation artifact' "
                    "framing in durable_findings §1.3 needs revision.")


class TestConstructedControl(unittest.TestCase):
    """
    Regression tests for results/constructed_control_results.json.

    The first-pass constructed system satisfies items 1–4 and 6 of the revised
    7-item MVE checklist by design, while failing items 5 (bidirectional
    symmetry) and 7 (open vocabulary). This locks in that the checklist table's
    Y/N ratings for constructed systems reflect actual pipeline output.

    NOTE: The JSON keys still use old 8-item numbering internally
    (e.g., "6_bidirectional_symmetry" = current item 5,
    "8_open_vocabulary" = current item 7). The code accesses the JSON
    keys as-is; the comments here use the current 7-item numbering.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.data = _load("constructed_control_results.json")
        except unittest.SkipTest:
            raise

    def test_constructed_satisfies_multiple_mve_items(self):
        """
        The constructed system must satisfy at least 4 of the 7 checklist items.
        If this drops below 4, the conclusion that items 1–4 and 6 (current
        numbering) don't discriminate NL from constructed may have been
        reversed and the checklist table needs re-examination.
        """
        self.assertGreaterEqual(self.data["n_items_satisfied"], 4,
            msg=f"Constructed control now satisfies only "
                f"{self.data['n_items_satisfied']} items; re-examine §5.")

    def test_constructed_fails_or_bidirectional_symmetry_alone_distinguishes(self):
        """
        Bidirectional symmetry (current item 5; JSON key '6_bidirectional_symmetry')
        plus open vocabulary (current item 7; JSON key '8_open_vocabulary')
        should be where the first-pass constructed system fails.
        If the constructed system passes both on first try, the checklist's
        discriminative power claim must be withdrawn.
        """
        mve = self.data["mve_checklist_scoring"]
        item_6_satisfies = mve["6_bidirectional_symmetry"]["satisfies"]
        item_8_satisfies = mve["8_open_vocabulary"]["satisfies"]
        # At least one of 6 or 8 should fail on first design attempt
        self.assertFalse(item_6_satisfies and item_8_satisfies,
            msg="First-pass constructed control now satisfies both bidirectional "
                "symmetry AND open-vocabulary requirements. If this is stable, "
                "the paper's §5 uniqueness argument must be withdrawn.")

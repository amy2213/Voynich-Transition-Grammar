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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _canonical import (  # noqa: E402
    AMBIGUOUS,
    AmbiguityPolicy,
    build_class_sequences,
    classify,
    classify_with_policy,
    transitions,
    sample_two_disjoint_contiguous_blocks,
    SequenceUnit,
    assign_affix_sequences,
    bootstrap_groups_to_target,
    discover_affixes,
    sample_units_to_target,
    self_clustering_details,
)

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
        Canonical within-line result: CHEDY→QOK = 2.659x.
        """
        ratio = self.data["transition_rules"]["CHEDY\u2192QOK"]["ratio"]
        self.assertAlmostEqual(ratio, 2.659, delta=0.001)

    def test_aiin_to_qok_repulsion(self):
        """
        Canonical within-line result: AIIN→QOK = 0.444x.
        """
        ratio = self.data["transition_rules"]["AIIN\u2192QOK"]["ratio"]
        self.assertAlmostEqual(ratio, 0.444, delta=0.001)

    def test_chedy_qok_obs_count(self):
        """
        Canonical within-line observed count = 615.
        """
        obs = self.data["transition_rules"]["CHEDY\u2192QOK"]["obs"]
        self.assertEqual(obs, 615)

    def test_transition_methodology_is_boundary_matched(self):
        method = self.data["methodology"]
        self.assertEqual(method["sequence_boundary"], "within_line")
        self.assertEqual(method["permutation_unit"],
                         "labels_shuffled_within_each_line")
        self.assertEqual(method["monte_carlo_correction"], "(b+1)/(B+1)")
        self.assertGreater(self.data["transition_rules"]["CHEDY→QOK"]["p"], 0)

    def test_unique_chedy_qok_pairs(self):
        """
        Boundary-aware canonical result: 312 unique CHEDY→QOK token pairs.
        Deterministic across runs — exact match expected.
        """
        pairs = self.data["token_grammar"]["unique_pairs"]
        self.assertEqual(pairs, 312,
            msg=f"Unique pair count drift: expected 312, got {pairs}")

    def test_chedy_token_participation(self):
        """
        Published: 77% of CHEDY tokens attract QOK.
        Tolerance: ±3 percentage points.
        """
        pct = self.data["token_grammar"]["chedy_pct"]
        self.assertAlmostEqual(pct, 77.0, delta=3.0,
            msg=f"CHEDY participation drift: expected 77% ±3, got {pct}%")


class TestAIINDensityDecomposition(unittest.TestCase):
    """
        Distinguish raw substring density from canonical-family assignment.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("core_analysis_results.json")

    def test_currier_a_mean(self):
        """
        Published: Currier A pages show AIIN at 15.0%.
        Tolerance: ±0.5 percentage points.
        """
        m = self.data["aiin_substring_density"]["currier_a_mean"]
        self.assertAlmostEqual(m, 15.0, delta=0.5,
            msg=f"Currier A AIIN mean drift: expected 15.0% ±0.5, got {m}%")

    def test_currier_b_mean(self):
        """
        Published: Currier B pages show AIIN at 15.0%.
        Tolerance: ±0.5 percentage points.
        """
        m = self.data["aiin_substring_density"]["currier_b_mean"]
        self.assertAlmostEqual(m, 15.0, delta=0.5,
            msg=f"Currier B AIIN mean drift: expected 15.0% ±0.5, got {m}%")

    def test_substring_similarity_is_not_labeled_invariance(self):
        """
        Published: KS p = 0.742 (A/B indistinguishable).
        The observed substring distributions are not distinguishable by this
        test, but that does not establish equivalence or invariance.
        """
        record = self.data["aiin_substring_density"]
        p = record["ks_p"]
        self.assertGreater(p, 0.05,
            msg=f"Substring-density descriptive result changed (p={p})")
        self.assertIn("equivalence_not_tested", record["status"])

    def test_canonical_family_density_differs(self):
        record = self.data["aiin_canonical_family_density"]
        self.assertAlmostEqual(record["currier_a_mean"], 13.58, delta=0.1)
        self.assertAlmostEqual(record["currier_b_mean"], 10.77, delta=0.1)
        self.assertLess(record["ks_p"], 0.01)


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
        Boundary-aware pooled backbone SC = 1.403x.
        Tolerance: ±0.1 absolute.
        """
        sc = self.data["self_clustering"]["backbone"]
        self.assertAlmostEqual(sc, 1.403, delta=0.02,
            msg=f"Pooled backbone SC drift: expected 1.403 ±0.02, got {sc}")

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


class TestPrefixSuffixEstimatorRecord(unittest.TestCase):
    """
    Locks the Version 2 estimator's method and generated evidence. These tests
    do not establish comparative uniqueness or language identity.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = _load("prefix_suffix_v2.json")

    def test_estimator_is_matched_and_boundary_aware(self):
        method = self.data["method"]
        self.assertEqual(method["target_tokens"], 31608)
        self.assertEqual(method["adjacency"], "within natural sequence units only")
        self.assertIn("without replacement", method["comparator_resampling"])
        self.assertIn("page-block", method["voynich_resampling"])

    def test_other_is_a_reported_sensitivity(self):
        summary = self.data["systems"]["VOYNICH"]["summary"]
        self.assertIn("primary_excludes_other", summary)
        self.assertIn("sensitivity_includes_other", summary)

    def test_provenance_is_complete(self):
        provenance = self.data["provenance"]
        self.assertEqual(self.data["estimator_version"], "2.0.0")
        self.assertIn("--replicates", provenance["command"])
        self.assertTrue(provenance["input_sha256"])
        self.assertEqual(set(provenance["code_sha256"]), {
            "scripts/10_prefix_suffix_analysis.py",
            "scripts/_canonical.py",
            "docs/v2/prefix_suffix_estimator_spec.md",
        })
        self.assertEqual(len(provenance["replicate_seeds"]["VOYNICH"]),
                         self.data["method"]["replicates"])

class TestResultsFilesExist(unittest.TestCase):
    """Smoke-test outputs explicitly tracked during the consolidation sprint."""

    EXPECTED_FILES = [
        "core_analysis_results.json",
        "prefix_suffix_v2.json",
        "prefix_suffix_v2.csv",
        "prefix_suffix_v2.md",
        "prefix_suffix_v2.svg",
        "classifier_overlap_report.json",
        "multifeature_permutation_results.json",
        "section_effect_null_results.json",
        "language_effect_null_results.json",
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

    The corrected July record reports four of five cascades surviving BH-FDR.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.data = _load("cascade_uncertainty_results.json")
        except unittest.SkipTest:
            raise

    def test_four_of_five_cascades_survive_fdr(self):
        n_passing = self.data["n_chains_surviving_fdr"]
        n_tested = self.data["n_chains_tested"]
        self.assertEqual((n_passing, n_tested), (4, 5),
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


class TestCanonicalAmbiguityPolicies(unittest.TestCase):
    def test_canonical_precedence_is_explicit(self):
        token = "qokaiin"
        self.assertEqual(classify(token), "QOK")
        self.assertEqual(
            classify_with_policy(token, AmbiguityPolicy.CANONICAL_PRECEDENCE),
            "QOK",
        )
        self.assertEqual(
            classify_with_policy(token, AmbiguityPolicy.SUBSTRING_PRECEDENCE),
            "AIIN",
        )
        self.assertEqual(
            classify_with_policy(token, AmbiguityPolicy.AMBIGUOUS_AS_CLASS),
            AMBIGUOUS,
        )

    def test_strict_exclusion_drops_and_breaks_adjacency(self):
        lines = [{"page": "f1r", "tokens": ["chedy", "qokaiin", "qokedy"]}]
        seqs = build_class_sequences(
            lines, AmbiguityPolicy.DROP_AND_BREAK_SEQUENCE
        )
        self.assertEqual(seqs, [("CHEDY",), ("QOK",)])
        counts = transitions(
            lines,
            ambiguity_policy=AmbiguityPolicy.DROP_AND_BREAK_SEQUENCE,
        )
        self.assertEqual(counts["total"], 0)
        self.assertEqual(counts["tr"].get(("CHEDY", "QOK"), 0), 0)

    def test_two_block_sampler_never_crosses_removed_seam(self):
        class FixedRng:
            @staticmethod
            def integers(low, high=None):
                return (high - 1) if high is not None else (low - 1)

        items = list(range(12))
        first, second = sample_two_disjoint_contiguous_blocks(
            items, 4, 4, FixedRng()
        )
        for block in (first, second):
            self.assertEqual(block, list(range(block[0], block[0] + 4)))
        self.assertTrue(set(first).isdisjoint(second))


class TestBoundaryAwareAffixUtilities(unittest.TestCase):
    def test_class_assignment_retains_sequence_boundaries(self):
        sequences = [("alpha", "alps"), ("alpha", "alps")]
        assigned = assign_affix_sequences(sequences, ["al"], "prefix")
        self.assertEqual(assigned, [("al", "al"), ("al", "al")])
        details = self_clustering_details(assigned, min_n=0)
        self.assertEqual(details["transition_n"], 2)

    def test_matched_sampler_does_not_join_units(self):
        class FixedRng:
            @staticmethod
            def permutation(n):
                return list(range(n))

            @staticmethod
            def integers(low, high=None):
                return low

        units = [
            SequenceUnit("s1", ("a", "b"), "sentence"),
            SequenceUnit("s2", ("c", "d"), "sentence"),
        ]
        sample = sample_units_to_target(units, 3, FixedRng())
        self.assertEqual([unit.tokens for unit in sample], [("a", "b"), ("c",)])
        self.assertEqual(sum(max(0, len(unit.tokens) - 1) for unit in sample), 1)

    def test_page_bootstrap_keeps_lines_separate(self):
        class FixedRng:
            @staticmethod
            def integers(low, high=None):
                return low

        units = [
            SequenceUnit("l1", ("a", "b"), "line", page="p1"),
            SequenceUnit("l2", ("c", "d"), "line", page="p1"),
        ]
        sample = bootstrap_groups_to_target(units, "page", 3, FixedRng())
        self.assertEqual([unit.tokens for unit in sample], [("a", "b"), ("c",)])

    def test_affix_discovery_is_deterministic(self):
        sequences = [("abx", "aby", "cdx", "cdy")] * 20
        first = discover_affixes(sequences, "prefix", min_coverage=0.1,
                                 max_coverage=0.6)
        second = discover_affixes(sequences, "prefix", min_coverage=0.1,
                                  max_coverage=0.6)
        self.assertEqual(first, second)


class TestGeneratedRepairArtifacts(unittest.TestCase):
    def test_overlap_arithmetic_is_exact_and_consistent(self):
        data = _load("classifier_overlap_report.json")
        overlap = data["overlap"]
        disagreement = data["precedence_disagreement"]
        self.assertEqual(data["corpus_tokens"], 31608)
        self.assertEqual((overlap["instances"], overlap["n_types"]), (1423, 160))
        self.assertAlmostEqual(overlap["pct_of_corpus"], 4.5020248, places=5)
        self.assertEqual((disagreement["instances"], disagreement["n_types"]),
                         (1171, 105))
        self.assertAlmostEqual(disagreement["pct_of_corpus"], 3.7047583, places=5)

    def test_permutation_result_supersedes_multiplied_marginals(self):
        data = _load("multifeature_permutation_results.json")
        corrected = [
            pair["all_four"]["ratio_vs_permuted_null"]
            for pair in data["pairs"].values()
        ]
        self.assertAlmostEqual(min(corrected), 1.53, places=2)
        self.assertAlmostEqual(max(corrected), 4.27, places=2)

    def test_v2_threshold_sensitivity_grid_is_present(self):
        data = _load("prefix_suffix_v2.json")
        cells = data["systems"]["VOYNICH"]["summary"]["threshold_sensitivity"]
        self.assertEqual(len(cells), 27)

    def test_seam_fixed_nulls_report_multiplicity(self):
        section = _load("section_effect_null_results.json")
        self.assertIn("BH", section["multiple_testing"])
        for cell in section["tests"].values():
            for test in cell.values():
                self.assertIn("p_bh_all_reported_tests", test)
                self.assertFalse(test["clears_null_bh"])

        language = _load("language_effect_null_results.json")
        self.assertIn("BH", language["multiple_testing"])
        self.assertIn("promising descriptive evidence", language["verdict"])
        self.assertIn("does not isolate language", language["verdict"])


class TestCurrentPublicClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paper = (PROJECT_ROOT / "docs" / "main.tex").read_text(encoding="utf-8")
        cls.readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    def test_paper_uses_locked_v2_estimates(self):
        for value in ("1.333", "1.458", "0.918", "0.00995"):
            self.assertIn(value, self.paper)
        self.assertIn("14 eligible comparators", self.paper)
        self.assertIn("Ottoman Turkish", self.paper)
        self.assertIn("ineligible", self.paper)

    def test_paper_does_not_restate_retired_claims(self):
        retired_positive_phrases = (
            "Voynich is the only tested system",
            "None of $16$ natural-language comparators",
            "all five tested chains survive",
            "is statistically invariant at $15.0\\%$",
            "encoded structured language is the only tested class",
            "resampling tokens with replacement",
            "33 regression tests",
        )
        for phrase in retired_positive_phrases:
            self.assertNotIn(phrase, self.paper)

    def test_scope_limits_are_explicit(self):
        combined = " ".join((self.paper + "\n" + self.readme).split())
        for limitation in (
            "do not establish natural-language uniqueness",
            "does not claim decipherment",
            "identify a language",
            "untested mechanisms",
        ):
            self.assertIn(limitation, combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)

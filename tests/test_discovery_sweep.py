import copy
import unittest

from scripts.discovery_sweep import SweepError, evaluate


class DiscoverySweepTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            "sweep_id": "sweep-001",
            "subject": "generic debug engine",
            "frozen_workload_ref": "workload:debug-v0",
            "source_classes": [
                {"id": "official_docs", "required": True},
                {"id": "github", "required": True},
                {"id": "community", "required": False},
            ],
            "policy": {"min_rounds": 3, "quiet_rounds_to_saturate": 2, "max_new_material_per_quiet_round": 0},
        }
        self.evidence = {"rounds": [
            {"round": 1, "queries": [
                {"source_class": "official_docs", "query": "official docs", "status": "SEARCHED", "evidence_ref": "search:1"},
                {"source_class": "github", "query": "github implementations", "status": "SEARCHED", "evidence_ref": "search:2"}],
             "hits": [{"candidate_id": "candidate:a", "source_class": "github", "source_ref": "github:a", "captured_at": "2026-08-14T00:30:00+09:00", "materiality": "MATERIAL", "relation_types": ["competitor"]}]},
            {"round": 2, "queries": [
                {"source_class": "official_docs", "query": "adjacent tools", "status": "SEARCHED", "evidence_ref": "search:3"},
                {"source_class": "github", "query": "alternative architecture", "status": "SEARCHED", "evidence_ref": "search:4"}], "hits": []},
            {"round": 3, "queries": [
                {"source_class": "official_docs", "query": "new terms", "status": "SEARCHED", "evidence_ref": "search:5"},
                {"source_class": "github", "query": "new terms", "status": "SEARCHED", "evidence_ref": "search:6"}], "hits": []}
        ]}

    def test_saturates_after_coverage_and_quiet_tail(self):
        report = evaluate(self.request, self.evidence)
        self.assertEqual(report["decision"], "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE")
        self.assertEqual(report["new_material_candidates_by_round"], [1, 0, 0])

    def test_missing_required_source_blocks(self):
        evidence = copy.deepcopy(self.evidence)
        for row in evidence["rounds"]:
            row["queries"] = [q for q in row["queries"] if q["source_class"] != "github"]
        self.assertIn("REQUIRED_SOURCE_github_UNSEARCHED", evaluate(self.request, evidence)["blocking_states"])

    def test_unknown_materiality_blocks(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["rounds"][0]["hits"][0]["materiality"] = "UNKNOWN"
        self.assertEqual(evaluate(self.request, evidence)["decision"], "BLOCKED_COVERAGE_OR_UNKNOWN")

    def test_duplicate_does_not_manufacture_novelty(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["rounds"][1]["hits"].append(copy.deepcopy(evidence["rounds"][0]["hits"][0]))
        self.assertEqual(evaluate(self.request, evidence)["new_material_candidates_by_round"], [1, 0, 0])

    def test_conflicting_known_materiality_fails_closed(self):
        evidence = copy.deepcopy(self.evidence)
        duplicate = copy.deepcopy(evidence["rounds"][0]["hits"][0])
        duplicate["materiality"] = "NON_MATERIAL"
        evidence["rounds"][1]["hits"].append(duplicate)
        with self.assertRaises(SweepError):
            evaluate(self.request, evidence)

    def test_unknown_can_be_resolved_by_later_evidence(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["rounds"][0]["hits"][0]["materiality"] = "UNKNOWN"
        resolved = copy.deepcopy(evidence["rounds"][0]["hits"][0])
        resolved["materiality"] = "MATERIAL"
        resolved["source_ref"] = "github:a:reviewed"
        evidence["rounds"][1]["hits"].append(resolved)
        report = evaluate(self.request, evidence)
        self.assertNotIn("candidate:a", report["unresolved_unknown_candidate_ids"])
        self.assertEqual(report["new_material_candidates_by_round"], [0, 1, 0])


if __name__ == "__main__":
    unittest.main()

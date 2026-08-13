from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "rts-discovery-sweep-report/v0"

class SweepError(ValueError):
    pass

def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def validate_request(request: dict[str, Any]) -> None:
    if not isinstance(request, dict):
        raise SweepError("request must be an object")
    for key in ("sweep_id", "subject", "frozen_workload_ref"):
        if not _nonempty(request.get(key)):
            raise SweepError(f"{key} must be a non-empty string")
    source_classes = request.get("source_classes")
    if not isinstance(source_classes, list) or not source_classes:
        raise SweepError("source_classes must be a non-empty list")
    seen = set()
    for item in source_classes:
        if not isinstance(item, dict) or set(item) != {"id", "required"}:
            raise SweepError("each source class must contain exactly id and required")
        if not _nonempty(item["id"]) or not isinstance(item["required"], bool):
            raise SweepError("invalid source class")
        if item["id"] in seen:
            raise SweepError("duplicate source class")
        seen.add(item["id"])
    policy = request.get("policy") or {}
    if not isinstance(policy, dict):
        raise SweepError("policy must be an object")
    min_rounds = int(policy.get("min_rounds", 2))
    quiet_rounds = int(policy.get("quiet_rounds_to_saturate", 2))
    max_new = int(policy.get("max_new_material_per_quiet_round", 0))
    if min_rounds < 1 or quiet_rounds < 1 or max_new < 0:
        raise SweepError("invalid policy values")

def validate_evidence(evidence: dict[str, Any], known_sources: set[str]) -> None:
    if not isinstance(evidence, dict):
        raise SweepError("evidence must be an object")
    rounds = evidence.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        raise SweepError("evidence.rounds must be a non-empty list")
    expected_round = 1
    for row in rounds:
        if not isinstance(row, dict) or set(row) != {"round", "queries", "hits"}:
            raise SweepError("each round must contain exactly round, queries, hits")
        if row["round"] != expected_round:
            raise SweepError("round numbers must be contiguous starting at 1")
        expected_round += 1
        queries, hits = row["queries"], row["hits"]
        if not isinstance(queries, list) or not isinstance(hits, list):
            raise SweepError("queries and hits must be lists")
        for q in queries:
            required = {"source_class", "query", "status"}
            if not isinstance(q, dict) or not required.issubset(q) or set(q) - (required | {"evidence_ref"}):
                raise SweepError("invalid query record")
            if q["source_class"] not in known_sources:
                raise SweepError("query uses unknown source class")
            if not _nonempty(q["query"]):
                raise SweepError("query must be non-empty")
            if q["status"] not in {"SEARCHED", "BLOCKED"}:
                raise SweepError("query status invalid")
            if q["status"] == "SEARCHED" and not _nonempty(q.get("evidence_ref")):
                raise SweepError("SEARCHED query requires evidence_ref")
        for hit in hits:
            required = {"candidate_id","source_class","source_ref","captured_at","materiality","relation_types"}
            if not isinstance(hit, dict) or set(hit) != required:
                raise SweepError("invalid hit fields")
            if hit["source_class"] not in known_sources:
                raise SweepError("hit uses unknown source class")
            for key in ("candidate_id", "source_ref", "captured_at"):
                if not _nonempty(hit[key]):
                    raise SweepError(f"hit {key} must be non-empty")
            if hit["materiality"] not in {"MATERIAL", "NON_MATERIAL", "UNKNOWN"}:
                raise SweepError("invalid hit materiality")
            if not isinstance(hit["relation_types"], list) or not all(_nonempty(x) for x in hit["relation_types"]):
                raise SweepError("relation_types invalid")

def evaluate(request: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    validate_request(request)
    known_sources = {x["id"] for x in request["source_classes"]}
    required_sources = {x["id"] for x in request["source_classes"] if x["required"]}
    validate_evidence(evidence, known_sources)
    policy = request.get("policy") or {}
    min_rounds = int(policy.get("min_rounds", 2))
    quiet_rounds = int(policy.get("quiet_rounds_to_saturate", 2))
    max_new = int(policy.get("max_new_material_per_quiet_round", 0))

    query_statuses = defaultdict(list)
    material_seen, unknown_ids = set(), set()
    all_candidates = {}
    new_material_by_round = []

    for row in evidence["rounds"]:
        for q in row["queries"]:
            query_statuses[q["source_class"]].append(q["status"])
        new_material = 0
        for hit in row["hits"]:
            cid = hit["candidate_id"]
            prev = all_candidates.get(cid)
            if prev is None:
                all_candidates[cid] = hit
            elif prev["materiality"] != hit["materiality"]:
                raise SweepError(f"candidate {cid} has conflicting materiality")
            if hit["materiality"] == "MATERIAL" and cid not in material_seen:
                material_seen.add(cid)
                new_material += 1
            if hit["materiality"] == "UNKNOWN":
                unknown_ids.add(cid)
            else:
                unknown_ids.discard(cid)
        new_material_by_round.append(new_material)

    coverage, blocking = {}, []
    for source in sorted(known_sources):
        statuses = query_statuses.get(source, [])
        state = "UNSEARCHED" if not statuses else ("SEARCHED" if "SEARCHED" in statuses else "BLOCKED")
        coverage[source] = state
        if source in required_sources and state != "SEARCHED":
            blocking.append(f"REQUIRED_SOURCE_{source}_{state}")
    if unknown_ids:
        blocking.append("UNRESOLVED_UNKNOWN_MATERIALITY")

    rounds_count = len(evidence["rounds"])
    quiet_tail = rounds_count >= quiet_rounds and all(x <= max_new for x in new_material_by_round[-quiet_rounds:])
    enough_rounds = rounds_count >= min_rounds
    if blocking:
        decision = "BLOCKED_COVERAGE_OR_UNKNOWN"
    elif enough_rounds and quiet_tail:
        decision = "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE"
    else:
        decision = "CONTINUE_SWEEP"

    return {
        "schema": SCHEMA,
        "sweep_id": request["sweep_id"],
        "subject": request["subject"],
        "frozen_workload_ref": request["frozen_workload_ref"],
        "decision": decision,
        "coverage": coverage,
        "rounds": rounds_count,
        "new_material_candidates_by_round": new_material_by_round,
        "material_candidate_ids": sorted(material_seen),
        "unresolved_unknown_candidate_ids": sorted(unknown_ids),
        "blocking_states": sorted(blocking),
        "candidate_count": len(all_candidates),
        "invariants": [
            "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE != COMPLETE_WEB_KNOWLEDGE",
            "EXTERNAL_SIGNAL != VERIFIED_TRUTH",
            "DISCOVERY != PROMOTION_AUTHORITY",
        ],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an adapter-neutral challenger discovery sweep")
    parser.add_argument("request", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    report = evaluate(request, evidence)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["decision"] == "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE" else 2

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "rts-discovery-sweep-report/v0"


class SweepError(ValueError):
    pass


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _policy(request: dict[str, Any]) -> tuple[int, int, int]:
    raw = request.get("policy") or {}
    if not isinstance(raw, dict):
        raise SweepError("policy must be an object")
    values = (
        int(raw.get("min_rounds", 2)),
        int(raw.get("quiet_rounds_to_saturate", 2)),
        int(raw.get("max_new_material_per_quiet_round", 0)),
    )
    if values[0] < 1 or values[1] < 1 or values[2] < 0:
        raise SweepError("invalid policy values")
    return values


def _source_classes(request: dict[str, Any]) -> tuple[set[str], set[str]]:
    rows = request.get("source_classes")
    if not isinstance(rows, list) or not rows:
        raise SweepError("source_classes must be a non-empty list")
    known: set[str] = set()
    required: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "required"}:
            raise SweepError("source class fields mismatch")
        if not _text(row["id"]) or not isinstance(row["required"], bool) or row["id"] in known:
            raise SweepError("invalid or duplicate source class")
        known.add(row["id"])
        if row["required"]:
            required.add(row["id"])
    return known, required


def evaluate(request: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise SweepError("request must be an object")
    for key in ("sweep_id", "subject", "frozen_workload_ref"):
        if not _text(request.get(key)):
            raise SweepError(f"{key} required")
    known_sources, required_sources = _source_classes(request)
    min_rounds, quiet_rounds, max_new = _policy(request)

    rounds = evidence.get("rounds") if isinstance(evidence, dict) else None
    if not isinstance(rounds, list) or not rounds:
        raise SweepError("evidence.rounds must be a non-empty list")

    query_statuses: dict[str, list[str]] = defaultdict(list)
    candidate_state: dict[str, str] = {}
    material_ids: set[str] = set()
    unknown_ids: set[str] = set()
    new_material_by_round: list[int] = []

    for expected_round, row in enumerate(rounds, 1):
        if not isinstance(row, dict) or set(row) != {"round", "queries", "hits"} or row["round"] != expected_round:
            raise SweepError("round shape/order invalid")
        if not isinstance(row["queries"], list) or not isinstance(row["hits"], list):
            raise SweepError("queries/hits must be lists")

        for query in row["queries"]:
            allowed = {"source_class", "query", "status", "evidence_ref"}
            if not isinstance(query, dict) or set(query) - allowed or not {"source_class", "query", "status"}.issubset(query):
                raise SweepError("query record invalid")
            source = query["source_class"]
            if source not in known_sources or not _text(query["query"]) or query["status"] not in {"SEARCHED", "BLOCKED"}:
                raise SweepError("query value invalid")
            if query["status"] == "SEARCHED" and not _text(query.get("evidence_ref")):
                raise SweepError("SEARCHED query requires evidence_ref")
            query_statuses[source].append(query["status"])

        new_material = 0
        for hit in row["hits"]:
            required_hit = {"candidate_id", "source_class", "source_ref", "captured_at", "materiality", "relation_types"}
            if not isinstance(hit, dict) or set(hit) != required_hit:
                raise SweepError("hit fields mismatch")
            if hit["source_class"] not in known_sources:
                raise SweepError("hit source class unknown")
            if not all(_text(hit[k]) for k in ("candidate_id", "source_ref", "captured_at")):
                raise SweepError("hit identity/provenance invalid")
            if hit["materiality"] not in {"MATERIAL", "NON_MATERIAL", "UNKNOWN"}:
                raise SweepError("hit materiality invalid")
            if not isinstance(hit["relation_types"], list) or not all(_text(x) for x in hit["relation_types"]):
                raise SweepError("relation_types invalid")

            cid, current = hit["candidate_id"], hit["materiality"]
            previous = candidate_state.get(cid)
            if previous and previous != current:
                if previous == "UNKNOWN" and current in {"MATERIAL", "NON_MATERIAL"}:
                    candidate_state[cid] = current
                    unknown_ids.discard(cid)
                else:
                    raise SweepError(f"candidate {cid} has conflicting materiality")
            elif previous is None:
                candidate_state[cid] = current

            final = candidate_state[cid]
            if final == "UNKNOWN":
                unknown_ids.add(cid)
            elif final == "MATERIAL" and cid not in material_ids:
                material_ids.add(cid)
                new_material += 1
        new_material_by_round.append(new_material)

    coverage: dict[str, str] = {}
    blockers: list[str] = []
    for source in sorted(known_sources):
        statuses = query_statuses.get(source, [])
        state = "UNSEARCHED" if not statuses else "SEARCHED" if "SEARCHED" in statuses else "BLOCKED"
        coverage[source] = state
        if source in required_sources and state != "SEARCHED":
            blockers.append(f"REQUIRED_SOURCE_{source}_{state}")
    if unknown_ids:
        blockers.append("UNRESOLVED_UNKNOWN_MATERIALITY")

    quiet_tail = len(rounds) >= quiet_rounds and all(x <= max_new for x in new_material_by_round[-quiet_rounds:])
    if blockers:
        decision = "BLOCKED_COVERAGE_OR_UNKNOWN"
    elif len(rounds) >= min_rounds and quiet_tail:
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
        "rounds": len(rounds),
        "new_material_candidates_by_round": new_material_by_round,
        "material_candidate_ids": sorted(material_ids),
        "unresolved_unknown_candidate_ids": sorted(unknown_ids),
        "blocking_states": sorted(blockers),
        "candidate_count": len(candidate_state),
        "invariants": [
            "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE != COMPLETE_WEB_KNOWLEDGE",
            "EXTERNAL_SIGNAL != VERIFIED_TRUTH",
            "DISCOVERY != PROMOTION_AUTHORITY",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    report = evaluate(
        json.loads(args.request.read_text(encoding="utf-8")),
        json.loads(args.evidence.read_text(encoding="utf-8")),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["decision"] == "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

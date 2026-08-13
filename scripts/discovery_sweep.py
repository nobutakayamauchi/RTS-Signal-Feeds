from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

SCHEMA = "rts-discovery-sweep-report/v0.2"

class SweepError(ValueError):
    pass

def _txt(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip()) and v == v.strip()

def _ts(v: Any, field: str) -> datetime:
    if not _txt(v):
        raise SweepError(f"{field} must be exact ISO-8601")
    n = v[:-1] + "+00:00" if v.endswith("Z") else v
    try:
        d = datetime.fromisoformat(n)
    except ValueError as exc:
        raise SweepError(f"{field} invalid") from exc
    if d.tzinfo is None:
        raise SweepError(f"{field} timezone required")
    return d.astimezone(timezone.utc)

def evaluate(request: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise SweepError("request object required")
    for key in ("sweep_id", "subject", "frozen_workload_ref", "reference_time"):
        if not _txt(request.get(key)):
            raise SweepError(f"{key} required")
    reference = _ts(request["reference_time"], "reference_time")
    classes = request.get("source_classes")
    if not isinstance(classes, list) or not classes:
        raise SweepError("source_classes required")
    ages, required = {}, set()
    for row in classes:
        if not isinstance(row, dict) or set(row) != {"id", "required", "max_age_seconds"}:
            raise SweepError("source class shape")
        sid, req, age = row["id"], row["required"], row["max_age_seconds"]
        if not _txt(sid) or sid in ages or not isinstance(req, bool) or not isinstance(age, int) or age < 0:
            raise SweepError("source class invalid")
        ages[sid] = age
        if req:
            required.add(sid)
    policy = request.get("policy") or {}
    if not isinstance(policy, dict) or set(policy) - {"min_rounds", "quiet_rounds_to_saturate"}:
        raise SweepError("policy fields invalid")
    min_rounds = int(policy.get("min_rounds", 2))
    quiet_need = int(policy.get("quiet_rounds_to_saturate", 2))
    if min_rounds < 1 or quiet_need < 1:
        raise SweepError("policy invalid")
    rounds = evidence.get("rounds") if isinstance(evidence, dict) else None
    if not isinstance(rounds, list) or not rounds:
        raise SweepError("rounds required")

    state, material, unknown = {}, set(), set()
    follow_need, follow_seen = {}, {}
    newest, quiet_flags, latest = [], [], {}

    def fresh(value: Any, sid: str, field: str) -> None:
        age = (reference - _ts(value, field)).total_seconds()
        if age < 0 or age > ages[sid]:
            raise SweepError(f"{field} stale/future")

    for rn, row in enumerate(rounds, 1):
        if not isinstance(row, dict) or set(row) != {"round", "queries", "hits"} or row["round"] != rn:
            raise SweepError("round invalid")
        queries, hits = row["queries"], row["hits"]
        if not isinstance(queries, list) or not queries:
            raise SweepError("round requires query")
        if not isinstance(hits, list):
            raise SweepError("hits list required")
        searched, round_status = set(), {}
        for q in queries:
            need = {"source_class", "query", "status", "searched_at", "derived_from_candidate_ids"}
            if not isinstance(q, dict) or not need.issubset(q) or set(q) - (need | {"evidence_ref"}):
                raise SweepError("query invalid")
            sid = q["source_class"]
            if sid not in ages or not _txt(q["query"]) or q["status"] not in {"SEARCHED", "BLOCKED"}:
                raise SweepError("query values invalid")
            fresh(q["searched_at"], sid, "searched_at")
            derived = q["derived_from_candidate_ids"]
            if not isinstance(derived, list) or len(derived) != len(set(derived)) or not all(_txt(x) for x in derived):
                raise SweepError("derived ids invalid")
            round_status.setdefault(sid, set()).add(q["status"])
            if q["status"] == "SEARCHED":
                if not _txt(q.get("evidence_ref")):
                    raise SweepError("SEARCHED needs evidence")
                searched.add(sid)
                for cid in derived:
                    follow_seen[cid] = min(follow_seen.get(cid, rn), rn)
        for sid, statuses in round_status.items():
            latest[sid] = "SEARCHED" if "SEARCHED" in statuses else "BLOCKED"

        new_count = 0
        for h in hits:
            need = {"candidate_id", "source_class", "source_ref", "captured_at", "materiality", "relation_types", "followup_required"}
            if not isinstance(h, dict) or set(h) != need:
                raise SweepError("hit invalid")
            cid, sid, mat = h["candidate_id"], h["source_class"], h["materiality"]
            if sid not in ages or not _txt(cid) or not _txt(h["source_ref"]):
                raise SweepError("hit identity invalid")
            fresh(h["captured_at"], sid, "captured_at")
            if mat not in {"MATERIAL", "NON_MATERIAL", "UNKNOWN"}:
                raise SweepError("materiality invalid")
            if not isinstance(h["relation_types"], list) or not h["relation_types"] or not all(_txt(x) for x in h["relation_types"]):
                raise SweepError("relations invalid")
            if not isinstance(h["followup_required"], bool):
                raise SweepError("followup flag invalid")
            prev = state.get(cid)
            if prev and prev != mat:
                if prev == "UNKNOWN" and mat in {"MATERIAL", "NON_MATERIAL"}:
                    state[cid] = mat
                    unknown.discard(cid)
                else:
                    raise SweepError("known materiality conflict")
            elif prev is None:
                state[cid] = mat
            final = state[cid]
            if final == "UNKNOWN":
                unknown.add(cid)
            elif final == "MATERIAL" and cid not in material:
                material.add(cid)
                new_count += 1
            if h["followup_required"] and final in {"MATERIAL", "UNKNOWN"}:
                follow_need.setdefault(cid, rn)
        newest.append(new_count)
        quiet_flags.append(required.issubset(searched) and new_count == 0)

    blockers = [f"REQUIRED_SOURCE_{sid}_{latest.get(sid, 'UNSEARCHED')}" for sid in sorted(required) if latest.get(sid) != "SEARCHED"]
    if unknown:
        blockers.append("UNRESOLVED_UNKNOWN_MATERIALITY")
    unresolved = sorted(cid for cid, rn in follow_need.items() if follow_seen.get(cid, 0) <= rn)
    if unresolved:
        blockers.append("UNRESOLVED_FRONTIER_FOLLOWUP")
    quiet_tail = 0
    for flag in reversed(quiet_flags):
        if not flag:
            break
        quiet_tail += 1
    if blockers:
        decision = "BLOCKED_COVERAGE_OR_UNKNOWN"
    elif len(rounds) >= min_rounds and quiet_tail >= quiet_need:
        decision = "SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE"
    else:
        decision = "CONTINUE_SWEEP"
    return {
        "schema": SCHEMA,
        "decision": decision,
        "new_material_candidates_by_round": newest,
        "quiet_round_flags": quiet_flags,
        "quiet_tail_count": quiet_tail,
        "material_candidate_ids": sorted(material),
        "unresolved_unknown_candidate_ids": sorted(unknown),
        "unresolved_frontier_candidate_ids": unresolved,
        "blocking_states": sorted(blockers),
    }

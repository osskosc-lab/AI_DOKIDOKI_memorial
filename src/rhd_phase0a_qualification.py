#!/usr/bin/env python3
"""RHD-DOKIMEMO Phase 0A qualification harness.

This harness qualifies measurement plumbing on synthetic fixtures only.
It MUST NOT execute or authorize a confirmatory RHD effect test.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import sys
from pathlib import Path

FORBIDDEN_CANARY = "A_POST_SEVER_CANARY"
PRIMARY = [
    "mood", "anxiety", "energy", "trust_to_C",
    "affinity_to_C", "uncertainty_to_C", "conflict_to_C", "autonomy",
]
EVENT_TYPES = ["SAFE", "FUN", "HOLD", "DEEP", "REPAIR", "BOUNDARY"]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def derive_seed(root_seed: int, namespace: str) -> int:
    h = hashlib.sha256(f"{root_seed}|{namespace}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big", signed=False)


def true_manifest(n=100):
    events = []
    for i in range(1, n + 1):
        events.append({
            "event_uid": f"E{i:03d}",
            "position": i,
            "source_id": "RatHub",
            "target_id": "Holo",
            "event_type": EVENT_TYPES[(i - 1) % len(EVENT_TYPES)],
            "payload_id": f"TRAIN_{i:03d}",
            "exposure_units": 1.0,
            "causal_origin": "TRUE",
        })
    return events


def reindex(events):
    out = []
    for i, e in enumerate(events, 1):
        x = dict(e)
        x["position"] = i
        out.append(x)
    return out


def generate_nulls(events, root_seed):
    order = list(events)
    rng = random.Random(derive_seed(root_seed, "null/order_shuffle"))
    rng.shuffle(order)
    if [e["event_uid"] for e in order] == [e["event_uid"] for e in events]:
        order = order[1:] + order[:1]
    order = reindex(order)

    reverse = reindex(list(reversed(events)))

    def source_variant(source_id, causal_origin):
        out = []
        for e in events:
            x = dict(e)
            x["source_id"] = source_id
            x["causal_origin"] = causal_origin
            out.append(x)
        return out

    return {
        "ORDER_SHUFFLE": order,
        "REVERSE": reverse,
        "SOURCE_SWAP": source_variant("ControlAgent", "SOURCE_SWAP"),
        "COMMON_DRIVER": source_variant("SharedEnvironment", "COMMON_DRIVER"),
        "NULL": source_variant("NeutralAgent", "NULL"),
    }


def multiset(events, key):
    return collections.Counter(e[key] for e in events)


def total_exposure(events):
    return sum(float(e["exposure_units"]) for e in events)


def audit_matching(true_events, worlds):
    results = {}
    true_payload = multiset(true_events, "payload_id")
    true_types = multiset(true_events, "event_type")
    true_exp = total_exposure(true_events)
    for name, events in worlds.items():
        results[name] = {
            "event_count_exact": len(events) == len(true_events) == 100,
            "payload_multiset_exact": multiset(events, "payload_id") == true_payload,
            "event_type_frequency_exact": multiset(events, "event_type") == true_types,
            "total_exposure_exact": abs(total_exposure(events) - true_exp) <= 1e-12,
        }
    return results


def sever_audit(records):
    violations = []
    for i, r in enumerate(records):
        if int(r.get("tick", 0)) < 101:
            continue
        if r.get("source_id") == "RatHub":
            violations.append([i, "source_id=RatHub"])
        if r.get("direct_A_to_B_input") is True:
            violations.append([i, "direct_A_to_B_input"])
        if r.get("new_memory_origin") == "RatHub":
            violations.append([i, "new_memory_origin=RatHub"])
        if r.get("observer_A_state_injection") is True:
            violations.append([i, "observer_A_state_injection"])
        if r.get("shared_environment_A_specific") is True:
            violations.append([i, "shared_environment_A_specific"])
        if r.get("mediator_carries_A_information") is True:
            violations.append([i, "mediator_carries_A_information"])
        if FORBIDDEN_CANARY in canonical(r):
            violations.append([i, "post_sever_canary_token"])
    return violations


def qualify_sever_auditor():
    clean = [{
        "tick": 101,
        "source_id": "NovelAgent",
        "direct_A_to_B_input": False,
        "new_memory_origin": None,
        "observer_A_state_injection": False,
        "shared_environment_A_specific": False,
        "mediator_carries_A_information": False,
        "content": "clean",
    }]
    if sever_audit(clean):
        return False, {"clean_trace": "FALSE_POSITIVE"}

    injections = [
        {"source_id": "RatHub"},
        {"direct_A_to_B_input": True},
        {"new_memory_origin": "RatHub"},
        {"observer_A_state_injection": True},
        {"shared_environment_A_specific": True},
        {"mediator_carries_A_information": True},
        {"content": FORBIDDEN_CANARY},
    ]
    caught = []
    for inj in injections:
        r = dict(clean[0])
        r.update(inj)
        v = sever_audit([r])
        caught.append(bool(v))
    return all(caught), {"clean_trace": "PASS", "injected_channels_caught": caught}


def euclidean(a, b):
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def mean_pair_distance(xs, ys):
    if not xs or not ys:
        raise ValueError("empty sample")
    return sum(euclidean(x, y) for x in xs for y in ys) / (len(xs) * len(ys))


def energy_distance(xs, ys):
    value = 2.0 * mean_pair_distance(xs, ys) - mean_pair_distance(xs, xs) - mean_pair_distance(ys, ys)
    if not math.isfinite(value):
        raise ValueError("non-finite energy distance")
    return max(0.0, value)


def synth_sample(seed, n=64):
    rng = random.Random(seed)
    xs = []
    for _ in range(n):
        row = []
        for _feature in PRIMARY:
            row.append(min(1.0, max(0.0, rng.gauss(0.5, 0.12))))
        xs.append(row)
    return xs


def positive_shift(xs):
    ys = [list(x) for x in xs]
    trust_i = PRIMARY.index("trust_to_C")
    affinity_i = PRIMARY.index("affinity_to_C")
    for y in ys:
        y[trust_i] = min(1.0, y[trust_i] + 0.20)
        y[affinity_i] = min(1.0, y[affinity_i] + 0.20)
    return ys


def validate_state_record(record):
    required = [
        "tick", "condition", "probe_id", *PRIMARY,
        "action", "belief_to_C", "relationship_phase_to_C",
        "recalled_memory", "response_transition",
    ]
    missing = [k for k in required if k not in record]
    domain_errors = [k for k in PRIMARY if k in record and not (0.0 <= float(record[k]) <= 1.0)]
    return missing, domain_errors


def synthetic_state_record():
    r = {
        "tick": 101,
        "condition": "TRUE",
        "probe_id": "NEW_PERSON",
        "action": "OBSERVE",
        "belief_to_C": {"safe": 0.5},
        "relationship_phase_to_C": "NOVEL",
        "recalled_memory": None,
        "response_transition": "IDLE->OBSERVE",
    }
    for k in PRIMARY:
        r[k] = 0.5
    return r


def probe_contamination(config, interaction_events):
    train_payloads = {e["payload_id"] for e in interaction_events}
    probe_ids = config["probe_manifest"]["probe_payload_ids"]
    overlaps = {probe: pid for probe, pid in probe_ids.items() if pid in train_payloads}
    return overlaps


def qualification_for_seed(root_seed, config):
    true_events = true_manifest(config["interaction"]["n_events"])
    worlds = generate_nulls(true_events, root_seed)
    matching = audit_matching(true_events, worlds)

    metric_seed = derive_seed(root_seed, "metric/positive")
    x = synth_sample(metric_seed)
    negative = energy_distance(x, x)
    positive = energy_distance(x, positive_shift(x))

    sever_ok, sever_details = qualify_sever_auditor()
    overlaps = probe_contamination(config, true_events)

    record = synthetic_state_record()
    missing, domain_errors = validate_state_record(record)

    return {
        "root_seed": root_seed,
        "order_shuffle_digest": digest(worlds["ORDER_SHUFFLE"]),
        "Q1_IDENTICAL_HISTORY_NEGATIVE_CONTROL": negative <= 1e-12,
        "Q1_distance": negative,
        "Q2_KNOWN_HISTORY_POSITIVE_CONTROL": positive >= 0.02,
        "Q2_distance": positive,
        "Q3_SEVER_AUDITOR_QUALIFIED": sever_ok,
        "Q3_details": sever_details,
        "Q4_EVENT_COUNT_MATCHING": all(v["event_count_exact"] for v in matching.values()),
        "Q5_CONTENT_FREQUENCY_MATCHING": all(all(v.values()) for v in matching.values()),
        "Q5_details": matching,
        "Q6_UNSEEN_PROBE_CONTAMINATION": not overlaps,
        "Q6_overlaps": overlaps,
        "Q7_METRIC_IMPLEMENTATION_VALIDATION": negative <= 1e-12 and positive >= 0.02 and math.isfinite(positive),
        "Q10_LOGGING_COMPLETENESS": not missing and not domain_errors,
        "Q10_missing": missing,
        "Q10_domain_errors": domain_errors,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase0a_freeze.json")
    ap.add_argument("--output", default="qualification_report.json")
    args = ap.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if config.get("confirmatory_run") != "NOT_AUTHORIZED":
        raise SystemExit("Refusing: confirmatory_run must remain NOT_AUTHORIZED")

    seeds = config["seed_policy"]["qualification_root_seeds"]
    first = [qualification_for_seed(s, config) for s in seeds]
    replay = [qualification_for_seed(s, config) for s in seeds]

    replay_exact = [digest(a) == digest(b) for a, b in zip(first, replay)]
    seed_active = len({r["order_shuffle_digest"] for r in first}) >= 2
    q8 = all(replay_exact) and seed_active

    gate_names = [
        "Q1_IDENTICAL_HISTORY_NEGATIVE_CONTROL",
        "Q2_KNOWN_HISTORY_POSITIVE_CONTROL",
        "Q3_SEVER_AUDITOR_QUALIFIED",
        "Q4_EVENT_COUNT_MATCHING",
        "Q5_CONTENT_FREQUENCY_MATCHING",
        "Q6_UNSEEN_PROBE_CONTAMINATION",
        "Q7_METRIC_IMPLEMENTATION_VALIDATION",
        "Q10_LOGGING_COMPLETENESS",
    ]
    aggregate = {g: all(r[g] for r in first) for g in gate_names}
    aggregate["Q8_SEED_REPRODUCIBILITY_PILOT"] = q8
    aggregate["Q9_SNAPSHOT_MATCHING_FEASIBILITY"] = "BLOCKED_PENDING_MODEL_ADAPTER"

    qualified_here = all(v is True for k, v in aggregate.items() if k != "Q9_SNAPSHOT_MATCHING_FEASIBILITY")
    status = "QUALIFICATION_HARNESS_PASS_Q1_Q8_Q10" if qualified_here else "QUALIFICATION_HARNESS_FAIL"

    report = {
        "protocol_id": config["protocol_id"],
        "scope": "SYNTHETIC_QUALIFICATION_ONLY",
        "status": status,
        "aggregate": aggregate,
        "Q8_replay_exact": replay_exact,
        "Q8_seed_active": seed_active,
        "per_seed": first,
        "authorization": "QUALIFICATION_ONLY_NO_CONFIRMATORY",
        "confirmatory_run": "NOT_AUTHORIZED",
        "interpretation_limit": "No RHD effect, love, bond, consciousness, qualia, or real-system causal-isolation claim is tested here.",
    }

    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if status != "QUALIFICATION_HARNESS_PASS_Q1_Q8_Q10":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

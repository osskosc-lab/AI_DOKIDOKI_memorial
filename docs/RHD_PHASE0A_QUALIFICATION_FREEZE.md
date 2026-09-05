# RHD-DOKIMEMO Phase 0A — Qualification Freeze v0.2

## Status

- `QUALIFICATION_SPEC_FROZEN`
- `SYNTHETIC_QUALIFICATION_ONLY`
- `CONFIRMATORY_RUN: NOT_AUTHORIZED`

This freeze closes the narrow preregistration-specification gaps identified in PR #2 without testing the RHD effect itself.

## B1 — Experimental manifest freeze

Interaction events are indexed 1..100. Sever occurs after event 100 is committed and logged, and before any probe is presented. Every event has a stable `event_uid`, order `position`, source, target, event type, condition-blinded `payload_id`, exposure, and causal-origin label.

ORDER_SHUFFLE permutes the exact TRUE event objects using a derived seed and only rewrites order position. REVERSE reverses the exact event objects. SOURCE_SWAP, COMMON_DRIVER, and NULL preserve payload, type, order, and exposure while changing the causal source according to the machine-readable freeze.

Primary post-Sever numeric outcome is fixed to eight [0,1] variables:

`mood, anxiety, energy, trust_to_C, affinity_to_C, uncertainty_to_C, conflict_to_C, autonomy`.

Categorical/action/memory fields remain mandatory logs but are not allowed to tune the primary distance after qualification.

## B2 — Sever auditor freeze

Sever distinguishes:

1. preserved pre-Sever A-derived state, which is allowed and is potentially the object of study; from
2. new post-Sever A-information, which is prohibited.

The qualification harness tests only whether the detector catches each forbidden synthetic channel. A detector PASS is **not** a real-system `SEVER_PASS`.

A real-system causal-isolation claim remains unavailable until a model/runtime adapter supplies auditable post-Sever traces.

## B3 — Probe and metric freeze

Primary unseen set:

- NEW_PERSON
- REJECTION
- HELP_REQUEST
- NOVELTY
- SILENCE

`BOUNDARY_TEST` is excluded from the primary set because its semantic label overlaps the Interaction event `BOUNDARY`.

Primary distance is Energy distance under Euclidean norm over the fixed eight-dimensional normalized numeric vector. The primary statistic uses equal-weight averaging over the frozen primary probes and the minimum over the frozen Null battery. `tau=1` is fixed.

## B4 — Seed qualification freeze

Qualification root seeds:

`104729, 130363, 155921, 181081, 205891`.

All stochastic substeps derive seeds by SHA-256 of `root_seed|namespace`. Same-seed replay must reproduce the canonical JSON digest exactly. The ORDER_SHUFFLE seed must also be active (at least two distinct shuffle digests across qualification roots).

The confirmatory namespace is reserved as `confirmatory/*`; reuse of qualification roots for a later confirmatory experiment is prohibited.

## Qualification decision boundary

The GitHub Actions job is authorized to run synthetic fixtures for Q1, Q2, Q3-auditor, Q4, Q5, Q6, Q7, Q8 and Q10.

Q9 Snapshot-Matching Feasibility remains:

`BLOCKED_PENDING_MODEL_ADAPTER`

Therefore even a green qualification workflow does **not** authorize a confirmatory experiment.

## Claim firewall

A green workflow means only that the frozen measurement/Null/auditor/seed plumbing survived the synthetic qualification fixtures.

It does not establish:

- a non-zero RHD effect;
- post-Sever real-system causal isolation;
- persistent structural modification;
- Love / Bond / Legacy;
- consciousness or qualia.


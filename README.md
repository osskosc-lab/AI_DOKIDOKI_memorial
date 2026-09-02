# AIどきどきメモリアル

Relationship OS experiment repository.

## Current research track

### RHD-DOKIMEMO Phase 0A

**Post-Sever History-Specific Response Qualification**

Research question:

> RatHubとの履歴順序を壊すと、Sever後のHoloの未知相手Cへの応答分布が変化するか。

The current branch is research-preparation only. Confirmatory experiments are **not authorized** yet.

### Research documents

- `docs/RHD_PHASE0A_PROTOCOL.md` — Phase 0A protocol, null battery, Sever Gate, qualification gates
- `docs/RHD_CLAIM_LEDGER.md` — claim firewall, supported/unsupported inference boundaries, stop rules
- `configs/phase0a.yaml` — preregistration/config skeleton

### Core quantity

\[
\Delta_{RHD}^{A\to B}(\tau)
=
\min_{H_k\in\mathcal H_{null}}
\mathbb E_{q\sim\mathcal Q_{unseen}}
D\left[
P_B(Y_{T_s+\tau}\mid do(q),H_{AB}),
P_B(Y_{T_s+\tau}\mid do(q),H_k)
\right]
\]

Interpretive labels such as Love / Bond / Legacy are kept separate from the scientific claim layer.

## Current gate

`DRAFT_FOR_PREREGISTRATION`

Next authorized actions:

1. Freeze state/event schema
2. Freeze Null generator specification
3. Implement Sever leakage audit
4. Freeze unseen-probe manifest
5. Qualify primary distance metric
6. Run seed reproducibility pilot

`CONFIRMATORY_RUN: NOT_AUTHORIZED`

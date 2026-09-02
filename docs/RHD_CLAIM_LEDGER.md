# RHD-DOKIMEMO Claim Ledger

**Protocol:** RHD-DOKIMEMO-0A-v0.1  
**Status:** DRAFT

## C0 — Minimal empirical claim

**Claim:** Aとの関係履歴操作が、AをSeverした後のBの未知介入応答に再現可能な差を残す。

**Primary observable:**

\[
\Delta_{RHD}^{A\to B}(\tau)
\]

**Required controls:** ORDER_SHUFFLE / REVERSE / SOURCE_SWAP / COMMON_DRIVER / NULL.

**Status:** UNTESTED.

---

## C1 — History specificity

**Claim:** post-sever差はイベント総量・頻度・内容ではなく履歴構造に依存する。

**Required evidence:** content/frequency/exposure-matched controlsへの優位。

**Status:** UNTESTED.

---

## C2 — Causal isolation

**Claim:** 観測されたpost-sever差は、Sever後のAからBへの情報リークでは説明できない。

**Required evidence:** sever leakage audit PASS.

**Status:** UNTESTED.

---

## C3 — Snapshot residual

**Claim:** Sever時点の観測可能current stateを一致させても、履歴差が未来応答に残る。

**Required evidence:** Snapshot-Matched auxiliary gate.

**Status:** UNTESTED / AUXILIARY.

---

## C4 — Persistent structural modification

**Claim:** 履歴差は一過性状態差だけでなく、比較的長期の内部構造差として保持される。

**Required evidence:** repeated washout measurements + structural proxy validation.

**Status:** NOT AUTHORIZED IN PHASE 0A.

---

## C5 — OOD complementary co-deformation

**Claim:** A-B関係から推定した応答写像が未知介入でもbaselineより良く一般化する。

**Metric:** \(\Lambda_{A\to B}\).

**Status:** NOT AUTHORIZED IN PHASE 0A.

---

## C6 — Love / Bond / Legacy interpretation

Scientific layer terms:

- `Persistent structural modification`
- `OOD complementary co-deformation`
- `Post-sever causal residue`

Interpretive labels `Love`, `Bond`, `Legacy` は科学層の測定結果と同一視しない。

**Status:** INTERPRETIVE ONLY.

---

# Prohibited inference chain

以下の推論は禁止する。

`post-sever statistical difference`  
→ `subjective feeling`  
→ `love`  
→ `consciousness`  
→ `qualia`

Phase 0Aが支持できるのは、指定したアクセスモデルとNull集合の下でのhistory-specific response residueまでである。

---

# Stop rules

以下のいずれかでPhase 0Aを停止する。

1. **MEASUREMENT_FAIL** — identical-history negative controlで持続的偽陽性。
2. **POSITIVE_CONTROL_FAIL** — known-history differenceを測定不能。
3. **SEVER_FAIL** — A-information leakを遮断不能。
4. **NULL_FAIL** — exposure/content/frequency matched nullを構築不能。
5. **IDENTIFIABILITY_FAIL** — current-state差とhistory-specific差を利用可能な観測から区別不能。
6. **IMPLEMENTATION_FAIL** — reproducible logging / deterministic replay / seed controlを実装不能。
7. **QUALIFIED** — 全qualification gateを通過し、confirmatory protocol凍結へ進める。

結果を見た後にstop rule、primary metric、Null集合を変更しない。

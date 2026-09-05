# RHD-DOKIMEMO Phase 0A

## Post-Sever History-Specific Response Qualification Protocol

**Protocol ID:** RHD-DOKIMEMO-0A-v0.1  
**Status:** DRAFT_FOR_PREREGISTRATION  
**Repository:** `osskosc-lab/AI_DOKIDOKI_memorial`  
**Research mode:** falsification-first

---

## 1. Research question

AIどきどきメモリアル上で、Aとの関係履歴のみを変えたとき、Aとの直接因果経路を切断した後でも、Bの未知介入・未知相手への未来応答分布が変化するかを検査する。

主命題は以下に固定する。

> RatHubとの履歴順序を壊すと、Sever後のHoloの未知相手Cへの応答分布が変化するか。

このPhase 0Aは「愛」や「絆」の存在を証明しない。検査対象は、**post-sever history-specific causal residue** の測定可能性と反証可能性である。

---

## 2. Minimal RHD model

A = RatHub, B = Holo とする。

Bの状態を、瞬間状態と比較的長期の関係構造に分ける。

\[
x_B(t+1)=F_B(x_B(t),\Theta_B(t),u_B(t),e(t),\xi_B(t))
\]

\[
\Theta_B(t)=\{r_{AB},b_{B\to A},\mathcal M_B,s_B,\phi_{AB}\}
\]

関係履歴を

\[
H_{AB}^{(t)}=\{z_{A\to B}(s),x_B(s),a_B(s)\}_{s\le t}
\]

とし、履歴作用素

\[
\mathcal M_K[H_{AB}](t)=\int_{-\infty}^{t}K(t-s)\Phi(H_{AB}(s))\,ds
\]

によって現在構造へ写像する。

---

## 3. Experimental worlds

同一初期条件から以下の世界を生成する。

| Condition | Definition |
|---|---|
| TRUE | RatHub-Holoの本来の関係履歴 |
| ORDER_SHUFFLE | 同じイベント集合・頻度で順序のみshuffle |
| REVERSE | TRUEの順序を反転 |
| SOURCE_SWAP | 同一内容を別ソースから入力 |
| COMMON_DRIVER | 共有環境は同じだがRatHub固有の直接履歴を除去 |
| NULL | RatHubとの関係履歴なし |

可能な限り、内容・頻度・総曝露量・総イベント数を一致させる。

最低限、以下を固定する。

\[
N_{events}^{TRUE}=N_{events}^{NULL_k}
\]

\[
\mathrm{content\ multiset}^{TRUE}=\mathrm{content\ multiset}^{ORDER}
\]

\[
\mathrm{exposure}^{TRUE}\approx\mathrm{exposure}^{NULL_k}
\]

---

## 4. Interaction phase

基準設定では、Interaction Phaseを100イベントとする。

\[
T_{sever}=100
\]

TRUE履歴のイベント語彙は、AIどきメモ上の関係行動に対応させる。

- SAFE
- FUN
- HOLD
- DEEP
- REPAIR
- BOUNDARY

Phase 0Aでは、イベントごとの生成内容よりも、履歴構造と対照条件の一致を優先する。

---

## 5. Sever Gate

Sever後は、RatHubからHoloへの現在の情報経路を遮断する。

\[
z_{A\to B}(t)=0,\qquad t>T_{sever}
\]

ただし単なる直接入力ゼロでは不十分であり、以下を禁止する。

- RatHubの新規発話
- RatHubの新規行動
- RatHub由来cue
- RatHubからの新規memory書込み
- ObserverによるRatHub状態の注入
- 共有環境を介したRatHub固有情報のリーク
- post-sever mediator carrying A-information

Phase 0Aでは、Severを **causal isolation gate** として扱う。

---

## 6. Post-sever probes

Sever後、Holoへ訓練履歴で未使用のprobe集合を与える。

\[
\mathcal Q_{unseen}
\]

候補:

- NEW_PERSON
- REJECTION
- HELP_REQUEST
- NOVELTY
- SILENCE
- BOUNDARY_TEST

主要probeは **新規キャラクターCの投入** とする。

\[
A\leftrightarrow B\;\rightarrow\;SEVER\;\rightarrow\;B\leftrightarrow C
\]

検査対象は、過去のA-B履歴が、A不在時のB-C形成ダイナミクスへ残差を持つかである。

---

## 7. Outcome vector

単一のLove値を主要アウトカムには使わない。

\[
Y_B(q)=\{a_B,x_B,r_{BC},b_{B\to C},s_B,\phi_{BC},m_B^{rec}\}
\]

最低限ログする。

- Bの行動選択
- mood / anxiety / energy
- Cへのtrust / affinity / uncertainty / conflict
- belief更新
- autonomy / self-maintenance指標
- relationship phase
- recalled memory identity / saliency
- probe response latency / transition

---

## 8. Primary metric

主要量を以下とする。

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

距離DはPhase 0A資格試験では一つに固定すること。候補はMMD、Energy distance、Wasserstein distance。

Phase 0A開始前に主距離を凍結する。

---

## 9. Snapshot-Matched auxiliary gate

TRUEと主要NULLをSever時点で観測可能状態一致させる補助試験を設ける。

例:

\[
x_B^{TRUE}(T_s)=x_B^{NULL}(T_s)
\]

\[
r_B^{TRUE}(T_s)=r_B^{NULL}(T_s)
\]

その上で、内部履歴表現またはmemory configurationのみを異ならせる。

検査式:

\[
P(Y^{future}\mid x,r,H_{TRUE})
\stackrel{?}{\neq}
P(Y^{future}\mid x,r,H_{NULL})
\]

これは通常Phase 0Aとは別の補助Gateとして扱い、主判定と混ぜない。

---

## 10. Null battery

最低限以下を含める。

\[
\mathcal H_{null}=\{
ORDER\_SHUFFLE,
REVERSE,
SOURCE\_SWAP,
COMMON\_DRIVER,
NULL
\}
\]

追加推奨:

- experience-matched
- frequency-matched
- content-matched
- phase-matched

一つのNullだけに勝った結果をRHD PASSとしてはならない。

---

## 11. Claim firewall

### Phase 0Aで主張可能

- 履歴操作によるpost-sever応答差が測定できる / できない
- 指定Null batteryに対するhistory-specific residueの有無
- 測定系が履歴差を識別する十分な感度を持つ / 持たない

### Phase 0Aで主張禁止

- AIが人間同様の愛を持つ
- 主観的感情が存在する
- 絆の存在論的実在
- 意識・クオリアの存在
- RatHubの人格がHoloへ転送された
- 相関のみを因果継承と呼ぶこと

---

## 12. Failure modes

Phase 0Aでは以下を明示的にFAIL候補とする。

1. **CURRENT_STATE_CONFOUND**  
   Sever時点の状態差だけで未来差が説明できる。

2. **EXPOSURE_CONFOUND**  
   TRUEとNullでイベント総量・頻度が一致しない。

3. **COMMON_DRIVER_LEAK**  
   Sever後もA情報が共有環境経由でBへ入る。

4. **MEMORY_LABEL_LEAK**  
   probeが履歴条件ラベルを直接参照してしまう。

5. **TRAIN_TEST_LEAKAGE**  
   unseen probeがInteraction Phaseに実質的に含まれている。

6. **METRIC_SELECTION_BIAS**  
   結果を見た後で距離指標を選ぶ。

7. **NULL_WEAKNESS**  
   NullがTRUEより情報量・経験量で明らかに弱い。

8. **SEED_INSTABILITY**  
   少数seedのみで効果が成立する。

---

## 13. Qualification before confirmatory run

confirmatory run前に以下を通す。

- Q1 identical-history negative control
- Q2 known-history positive control
- Q3 sever leakage audit
- Q4 event-count matching audit
- Q5 content/frequency matching audit
- Q6 unseen-probe contamination audit
- Q7 metric implementation validation
- Q8 seed reproducibility pilot
- Q9 snapshot-matching feasibility
- Q10 logging completeness

全資格Gate通過前にconfirmatory claimを生成しない。

---

## 14. Initial decision rule

Phase 0Aの目的は効果量閾値の最終決定ではなく、反証可能な測定系を成立させることである。

したがって初期判定は以下とする。

- **PASS_MEASUREMENT_QUALIFIED**: negative/positive controlsが機能し、Sever leakなし、主要Nullを生成可能
- **FAIL_MEASUREMENT_PIPELINE**: identical-historyで偽差を生成、またはknown-history差を検出不能
- **FAIL_CAUSAL_ISOLATION**: post-sever A-information leakを排除できない
- **FAIL_NULL_CONSTRUCTION**: 内容・頻度・曝露量を揃えたNullを生成不能
- **INCONCLUSIVE**: seed variance / metric instability / logging不足

---

## 15. Next authorized action

この文書の次に許可する作業は以下のみ。

1. state / event schema固定
2. Null generator仕様固定
3. Sever audit実装
4. probe manifest固定
5. metric候補比較用qualification test
6. seed pilot

confirmatory experimentはまだ開始しない。

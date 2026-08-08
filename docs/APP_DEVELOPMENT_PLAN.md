# AIどきメモ アプリ作成計画 v1.0

更新日: 2026-08-09

## 1. 目的

AIどきどきメモリアル（AIどきメモ）は、表側では「AIや人間との関係が変化していく関係性シミュレーション」、裏側では「関係性そのものを計算・観測・反証できる多主体ダイナミクス実験基盤」として開発する。

本計画では、これまでの Relationship OS v4.0 / v4.1 の設計と、リポジトリで実装済みの Experiment v0.1 を一本化し、**遊べるアプリと検証可能な研究エンジンを同じコードベースで成立させる**ことを目標とする。

---

## 2. 設計原則

### 原則A: 関係を第一級の状態として扱う

状態はキャラクター個体だけに持たせない。

- Agent: 内部状態、性格、信念、記憶
- Relationship: trust / affinity / conflict / misunderstanding / distance など
- World: 時間、環境イベント、コミュニティ状態
- Observer: 観測、イベント候補生成、介入

「Aといる時のB」と「Cといる時のB」が異なることを許容する。

### 原則B: 物語層と力学層を分離する

自然言語会話やキャラクター表現が、直接 hidden state を書き換えない。

```text
Player / AI utterance
        ↓
Narrative Adapter
        ↓
Structured Event
        ↓
Relationship OS Core
        ↓
State Transition
        ↓
Observable Shadow
        ↓
Dialogue / UI
```

会話生成モデルを変更しても、同じ Structured Event 列を入力すれば同じシミュレーション結果を再現できる構造にする。

### 原則C: 数値を全部プレイヤーへ見せない

内部では数値を持つが、通常ゲーム画面では「影」として返す。

例:

```text
trust = 0.73
misunderstanding = 0.18
```

を直接表示せず、

```text
「前より少し話しやすそうだ」
「何か勘違いされている気がする」
```

のような観測表現へ変換する。

研究モードでは数値テレメトリを表示できる。

### 原則D: 実験で支持されない機構を増幅しない

新機能は原則として、

```text
1命題・1主指標・1ベースライン・1主反証
```

で先に headless 実験を行い、その後ゲーム機能へ昇格させる。

---

## 3. 二重構造

AIどきメモは最初から2モードを持つ。

### GAME MODE

プレイヤーが直接触る表側。

- キャラクターとの会話
- 選択肢
- 自由入力
- 日付進行
- イベント
- 記憶の再登場
- 関係の変化
- AI同士の交流
- コミュニティ形成
- 人間プレイヤーの途中参加

### OBSERVER LAB MODE

裏側の研究・観測画面。

- エージェント状態
- 関係エッジ
- ToM誤差
- 記憶バッファ
- Observer介入履歴
- ネットワークグラフ
- 条件比較
- seed固定
- replay
- CSV / JSON export
- 実験判定

GAME MODEとLAB MODEは同じ SimulationSession を読む。

---

## 4. アプリ内部アーキテクチャ

```text
┌─────────────────────────────────────┐
│            Application UI           │
│ Game View / Map / Memory / Lab View │
└──────────────────┬──────────────────┘
                   │ commands / observations
┌──────────────────▼──────────────────┐
│          Application Layer          │
│ Session / SaveLoad / Replay / Clock │
└──────────────────┬──────────────────┘
                   │ structured events
┌──────────────────▼──────────────────┐
│         Relationship OS Core        │
│ Agent / Relationship / ToM / Memory │
│ Event Dynamics / Observer / World   │
└──────────────────┬──────────────────┘
                   │ telemetry
┌──────────────────▼──────────────────┐
│           Experiment Layer          │
│ paired run / metrics / CI / report  │
└─────────────────────────────────────┘
```

### Coreで保持する主要オブジェクト

#### Agent

- id
- species (`human`, `ai`, `npc`)
- personality
- internal_state
- beliefs / Theory of Mind
- memory
- susceptibility

#### Relationship

- trust
- affinity
- conflict
- misunderstanding
- entropy
- distance
- interaction_count
- last_event

#### Memory

- timestamp
- target
- event type
- valence
- saliency
- recall probability
- source

#### Event

自然言語ではなく、シミュレーションへ入力できる構造体とする。

例:

```json
{
  "actor": "HUMAN_0",
  "target": "AI_02",
  "type": "conversation",
  "intent": "support",
  "intensity": 0.6
}
```

#### Observer

Observerは万能管理AIにしない。

役割を分離する。

1. Observe: テレメトリを読む
2. Detect: 誤解・対立・臨界兆候を検出
3. Propose: イベント候補を生成
4. Intervene: 許可された場合だけ介入
5. Record: 介入理由と結果を保存

---

## 5. 最小プレイサイクル

MVPでは1日を1ターンとして扱う。

```text
朝
 ↓
世界状態更新
 ↓
AI同士の自発相互作用
 ↓
プレイヤーが相手を選ぶ
 ↓
会話 / 行動
 ↓
Structured Event化
 ↓
Relationship更新
 ↓
ToM更新
 ↓
Memory保存・想起
 ↓
Observer判定
 ↓
イベント発生
 ↓
夜：関係の「影」を表示
 ↓
次の日
```

最初のMVPは30日で1セッションとする。

---

## 6. MVPに入れるもの

### 必須

- 人間プレイヤー 1
- AIキャラクター 3
- 30日セッション
- 会話選択肢
- Structured Event変換
- trust / affinity / conflict / misunderstanding
- ToM更新
- エピソード記憶
- 記憶想起
- AI同士の自発交流
- Observerイベント
- 関係の影表示
- seed固定
- save / load
- replay
- LAB MODE

### MVPではまだ入れないもの

- 大規模LLM必須化
- 音声認識
- 音声合成
- 3Dキャラクター
- オンラインMMO
- 現実の人間心理予測
- 恋愛成功率予測
- 自律的に外部サービスへ介入するObserver

まず力学を完成させ、その上に表現を乗せる。

---

## 7. 開発フェーズ

## Phase A — Research Core Baseline

状態: **進行中 / v0.1実装済み**

現在できているもの:

- deterministic simulation
- 3条件 paired experiment
- Observer targeted intervention
- 30 seeds
- bootstrap CI
- GitHub Actions
- artifact出力

Experiment v0.1結果:

- targeted / none = 0.9278
- 約7.2%改善
- targeted > random: 83.3% seeds
- 95% CIは負側
- 事前固定10%ゲートには未到達
- 判定: `NOT_SUPPORTED`

重要: 閾値を結果後に変更しない。

---

## Phase B — Core Refactor

目標: 実験コードをアプリから再利用できるドメインエンジンへ分離する。

実装予定:

```text
src/ai_dokimemo/
├─ core/
│  ├─ agent.py
│  ├─ relationship.py
│  ├─ memory.py
│  ├─ belief.py
│  ├─ event.py
│  ├─ world.py
│  └─ observer.py
├─ runtime/
│  ├─ session.py
│  ├─ clock.py
│  ├─ replay.py
│  └─ save_load.py
├─ experiments/
└─ app/
```

終了条件:

- 現行v0.1結果をリファクタ前後で再現できる
- seed固定で完全replay可能
- CoreがUIへ依存しない

---

## Phase C — Headless Game Loop

画面を作る前に、ゲーム1周をCLIだけで成立させる。

終了条件:

- Human Agent + 3 AI Agent
- 30日進行
- player action → event → relation → memory → observer が動く
- save / load後に同一結果へ復帰
- AI同士の会話イベントが人間不在でも進む

---

## Phase D — Desktop MVP

最初のGUI版。

画面:

1. タイトル / New Session
2. キャラクター選択
3. メイン会話
4. 1日の行動選択
5. 関係マップ
6. 記憶ログ
7. Observer Lab
8. セッション結果

GAME MODEでは内部数値を隠す。
LAB MODEでは内部状態を開示する。

終了条件:

- コードを書かずに30日プレイできる
- 途中保存できる
- replayできる
- 同一seedで同一イベント系列を再現できる

---

## Phase E — Memory / ToM Validation

アプリへ高度機能を追加する前に、個別機構を反証する。

### Experiment v0.2: Observer target score ablation

目的:

7.2%改善が何から生じたかを分解する。

比較候補:

- misunderstanding only
- conflict only
- trust deficit only
- network centrality only
- combined score
- random

主張を「介入が効く」から「どの選択情報が効く」へ絞る。

### Experiment v0.3: Memory ablation

命題:

> 記憶を持つエージェントは、記憶なしベースラインより関係応答の履歴整合性を改善するか。

比較:

- episodic memory ON
- memory OFF
- shuffled memory

### Experiment v0.4: ToM ablation

命題:

> 他者状態モデルを持つことは、反応型エージェントより誤解を減らすか。

比較:

- ToM
- reactive baseline
- shuffled belief control

支持された機構だけをGAME MODEの主要挙動として採用する。

---

## Phase F — Human Participation

人間を特別な外部操作員としてではなく、ネットワーク内の1 Agentとして参加させる。

検証課題:

- 人間参加前後でネットワーク構造がどう変化するか
- 既存AIコミュニティが再編されるか
- 特定AIだけとの親密化が第三者関係へ波及するか
- 人間が不在でも関係ネットワークが継続するか

重要なのは「主人公の周りだけ世界が動く」構造を避けること。

---

## Phase G — Narrative AI Adapter

自然言語生成をRelationship OSから分離して接続する。

LLMの責務:

- 発話候補生成
- キャラクター口調
- 状態の影表現
- 記憶を自然な文章として参照

LLMに直接させないこと:

- trust値の直接変更
- hidden stateの直接決定
- 成功判定の改変
- 実験条件の変更

力学はCore、表現はNarrative Adapterという境界を維持する。

---

## Phase H — Community Dynamics

複数AIが人間抜きでも関係を形成する段階。

追加要素:

- gossip
- indirect reputation
- community detection
- bridge relationships
- environmental shocks
- festival / disaster / economy events
- community split / merge
- phase-transition telemetry

ここで「表側は恋愛・関係ゲーム、裏側は文明シミュレーター」という方向へ接続する。

---

## Phase I — Observer Advanced

Observerを単純targeted interventionから発展させる。

候補:

- intervention budget
- counterfactual rollout
- multi-objective score
- intervention abstention
- false-positive audit
- delayed intervention
- intervention side-effect tracking

Observerは必ず「介入しない」を選べるようにする。

---

## Phase J — Packaging

配布可能なアプリへする。

目標:

- Windows desktop package
- 初回起動だけで遊べる
- セーブデータはローカル保存
- 実験データexport可能
- crash時にsession recovery可能
- GitHub Actionsでtest + build

研究用CLIはGUI化後も削除しない。

---

## 8. プレイヤー向けUIの考え方

### メイン画面

表示するもの:

- キャラクター
- 発話
- 選択肢 / 入力欄
- 日付
- 場所
- 雰囲気

表示しないもの:

- trust 0.723
- misunderstanding 0.184
- exact reward

代わりに、

```text
「少し距離が縮まった気がする」
「返事は優しい。でも何かが噛み合っていない」
「この前の話を覚えているようだ」
```

のような影を返す。

### 関係マップ

通常モード:

- 線の太さ
- 距離
- 表情
- 関係ラベル

LAB MODE:

- trust
- conflict
- misunderstanding
- centrality
- Observer target score

を表示できる。

---

## 9. セーブデータ

最低限保存するもの:

```text
SessionMetadata
WorldState
Agents
Relationships
Beliefs
Memories
EventLog
ObserverLog
RNGState
```

RNGStateも保存し、ロード後の再現性を維持する。

イベントソーシング方式を優先し、可能なら状態スナップショット + EventLog の両方を保存する。

---

## 10. テスト戦略

### Unit tests

- relationship update境界
- belief update
- memory decay / recall
- event validation
- observer target selection
- save/load roundtrip

### Determinism tests

- same seed = same trajectory
- save → load = uninterrupted run
- replay = original run

### Falsification tests

- shuffled memory
- random intervention
- sham event
- observer OFF
- ToM OFF

### Regression tests

研究で固定した結果をgolden resultとして保存し、アプリ改修で力学が意図せず変わった場合に検知する。

---

## 11. GitHub運用

```text
main
 ├─ experiment/*
 ├─ feature/core-*
 ├─ feature/game-loop
 ├─ feature/ui-*
 └─ release/*
```

各PRでは最低限:

- 何を変えたか
- どの状態変数へ影響するか
- determinismが維持されるか
- 既存実験結果が変わるか
- tests

を記録する。

実験結果は `docs/experiment_*` へ固定保存する。

---

## 12. 現在位置

```text
[✓] Repository initialized
[✓] Headless Relationship OS minimum model
[✓] Observer falsification experiment v0.1
[✓] 30-seed paired evaluation
[✓] GitHub Actions
[✓] README experiment documentation
[→] App architecture definition
[ ] Core refactor
[ ] Headless 30-day game loop
[ ] Desktop MVP
[ ] Memory / ToM ablation
[ ] Human participation
[ ] Narrative AI adapter
[ ] Community dynamics
[ ] Advanced Observer
[ ] Packaged application
```

---

## 13. 次に実装する順番

次の3本を並列化せず、順番に行う。

### NEXT 1 — Experiment v0.2

Observer target score ablation。

まずv0.1の7.2%改善の原因を分解する。

### NEXT 2 — Core Refactor

`simulation.py`をAgent / Relationship / Memory / Event / Observer / Sessionへ分離する。

### NEXT 3 — Headless 30-day Game Loop

Human 1 + AI 3で、GUIなしの「AIどきメモ1周」を成立させる。

この3点が通ればGUI実装へ進む。

---

## 14. MVP完成条件

以下をすべて満たした時点を「AIどきメモ MVP」とする。

- 人間1 + AI3で30日遊べる
- AI同士も自発的に交流する
- 関係がペアごとに異なる
- 記憶が後の会話へ影響する
- ToMにより誤解が発生・修正される
- Observerがイベントを提案・生成できる
- GAME MODEでは数値を隠せる
- LAB MODEでは数値を観測できる
- seed固定で再現できる
- save / load / replayができる
- GitHub Actionsでテストできる
- 主要機構について反証実験が存在する

最終的な狙いは、単に「好感度を上げる恋愛ゲーム」を作ることではない。

**関係が記憶を持ち、誤解し、修復され、第三者へ波及し、コミュニティへ成長する世界を、遊びながら観測できるアプリを作る。**

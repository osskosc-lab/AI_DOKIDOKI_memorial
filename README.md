# AIどきどきメモリアル — Relationship OS Experiment Lab

表側は関係性シミュレーター、裏側は反証可能な多主体ダイナミクス実験基盤です。

このリポジトリでは、AI・人間・仮想人格を同じ「エージェント」として扱い、個体の感情値だけでなく、**関係そのものを状態変数として計算・観測・介入**します。

初期版では `Relationship OS v4.1 - Advanced Dynamics` の三層構造を、再現可能な最小実験へ落としています。

- **Micro layer**: エージェント内部状態、Theory of Mind、減衰する関係記憶
- **Meso layer**: 信頼、対立、観測、ゴシップ、関係エッジ
- **Macro layer**: Observerによるイベント生成と関係ネットワークへの介入

---

## アプリ開発ロードマップ

AIどきメモは、研究用シミュレーターとゲームを別物にせず、**同じRelationship OS CoreをGAME MODEとOBSERVER LAB MODEの2つの画面から利用するアプリ**として開発します。

詳細計画:

- [AIどきメモ アプリ作成計画](docs/APP_DEVELOPMENT_PLAN.md)

現在位置:

```text
[✓] Headless Relationship OS minimum model
[✓] Observer falsification experiment v0.1
[✓] 30-seed paired evaluation / GitHub Actions
[→] Experiment v0.2: Observer target score ablation
[ ] Core refactor
[ ] Human 1 + AI 3 の30日 headless game loop
[ ] Desktop MVP
[ ] Memory / ToM ablation
[ ] Human participation
[ ] Narrative AI adapter
[ ] Community dynamics
[ ] Advanced Observer
[ ] Packaged application
```

直近の実装順は、**v0.2反証実験 → Core Refactor → 30日ゲームループ → GUI** とします。

---

## Experiment v0.1 — Observer targeting falsification

### 研究質問

誤解が最大の関係へ介入するObserverは、同じ回数・同じ強度のランダム介入および無介入より、最終局面の誤解を減らせるか。

この実験では、Observerを単なるログ解析器ではなく、関係ネットワークへ介入する因果主体として扱います。

### 固定命題

> 誤解が最大の関係へ和解介入を行うと、同一乱数系列の無介入条件に対し、最終20ステップの平均誤解を10%以上低下させるか。

成功条件は結果を見る前に固定し、実験後には変更していません。

---

## 実験条件

同じ初期状態と乱数系列から、以下の3条件を比較します。

| 条件 | 内容 |
|---|---|
| `none` | Observerは観測のみを行い、介入しない |
| `random` | 同じ回数・同じ強度で、ランダムな関係へ介入する |
| `targeted` | 現時点で誤解が最大の関係へ介入する |

条件間で共有するもの:

- 初期エージェント状態
- 初期関係ネットワーク
- 観測ノイズ
- 環境ノイズ
- 相互作用順序

これにより、条件差をObserverの対象選択方針へできるだけ限定します。

---

## 操作的定義

### 誤解

各エージェントが持つ相手の状態推定と、相手の実際の内部状態との差を、方向付きTheory of Mind誤差として測定します。

主指標は、関係エッジ上の方向付きToM誤差の平均です。

### 主指標

- 最終20ステップにおける平均誤解

### ベースライン

- 無介入条件 `none`

### 反証対照

- 同量のランダム介入条件 `random`

対象選択介入がランダム介入と変わらなければ、「誤解最大の関係を選ぶこと」自体の効果は支持されません。

---

## 実験設定

- シード数: **30**
- エージェント数: **16**
- シミュレーション長: **140 steps**
- 評価窓: **最終20 steps**
- 比較方法: 条件間対応ありのpaired design
- 信頼区間: paired bootstrap 95% CI

---

## 事前固定した判定ゲート

仮説を支持するためには、次の3条件をすべて満たす必要があります。

1. `targeted / none <= 0.90`
2. 70%以上のシードで `targeted` が `random` を上回る
3. `targeted - none` のpaired bootstrap 95% CI上限が0未満

つまり、単に平均値が少し良いだけでは支持としません。

---

## 結果

| 条件 | 最終20ステップの平均誤解 |
|---|---:|
| 無介入 `none` | 0.002635 |
| ランダム介入 `random` | 0.002568 |
| 対象選択介入 `targeted` | **0.002432** |

追加結果:

- `targeted / none = 0.9278`
- 無介入比の低下量: 約 **7.2%**
- `targeted - none = -0.000203`
- paired bootstrap 95% CI: **[-0.000261, -0.000153]**
- `targeted` が `random` を上回ったシード割合: **83.3%**

### 判定ゲート

| ゲート | 結果 |
|---|---|
| `targeted / none <= 0.90` | 不通過 |
| 70%以上のシードでrandomより良い | 通過 |
| paired 95% CI上限 < 0 | 通過 |

### 最終判定

```text
NOT_SUPPORTED
```

対象選択介入には安定した改善傾向が見られましたが、事前に固定した「10%以上低下」という閾値には届きませんでした。

したがって、v0.1の命題は支持されません。

---

## 解釈

今回の結果から言えるのは、toy model内部では、Observerが誤解の大きい関係を選んで介入することで、無介入やランダム介入より誤解を減らす傾向が観測された、ということです。

ただし、7.2%の改善は、事前に設定した10%の成功基準を満たしていません。

この結果は「失敗」ではなく、次の問いを具体化します。

- 効果を生んだのは誤解スコアそのものか
- 対立度や信頼度を加えると改善するか
- ネットワーク中心性の高い関係への介入が重要か
- 介入頻度や強度ではなく、対象選択規則が本質か

次段階では、対象選択スコアのアブレーションによって、7.2%の改善を生んだ因果成分を分解します。

---

## 再現方法

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

依存関係をインストール:

```bash
python -m pip install -e ".[dev]"
```

テスト実行:

```bash
pytest
```

30シード実験:

```bash
ai-dokimemo-experiment --output artifacts/experiment_v0_1 --seeds 30
```

GitHub Actionsでも同じテストと30シード実験を実行します。

---

## 生成物

実験実行後、出力ディレクトリに以下が生成されます。

- `summary.json` — 判定、効果量、信頼区間
- `seed_results.csv` — シード別結果
- `timeseries.csv` — 条件別時系列
- `REPORT.md` — 日本語実験報告
- `misunderstanding_timeseries.png` — 誤解の時間発展
- `outcome_boxplot.png` — 条件別結果分布

リポジトリ内の固定結果:

- `docs/experiment_v0_1/REPORT.md`
- `docs/experiment_v0_1/summary.json`

---

## リポジトリ構成

```text
AI_DOKIDOKI_memorial/
├─ .github/workflows/experiment.yml
├─ docs/
│  ├─ APP_DEVELOPMENT_PLAN.md
│  └─ experiment_v0_1/
│     ├─ REPORT.md
│     └─ summary.json
├─ scripts/run_experiment.py
├─ src/ai_dokimemo/
│  ├─ simulation.py
│  └─ experiment.py
├─ tests/test_simulation.py
├─ pyproject.toml
└─ README.md
```

---

## 現在の非主張

この実験が検証するのは、Relationship OSのtoy model内部におけるObserver対象選択の因果効果です。

現段階では、以下を主張しません。

- 人間の心理を正確に再現している
- 恋愛関係を予測できる
- 現実社会で同じ介入効果が得られる
- AIが意識や本物の感情を持つ
- 関係性OSが社会科学的に妥当である

外的妥当性は、別の実験とデータによって検証する必要があります。

---

## 開発方針

AIどきどきメモリアルは、恋愛ゲームらしい物語表現を持ちながら、裏側では次の原則を守ります。

```text
1命題・1指標・1ベースライン・1反証実験
```

面白い挙動を見つけることよりも、何が支持され、何が支持されなかったかを区別できる実験基盤を目指します。

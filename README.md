# AIどきどきメモリアル - Relationship OS Experiment Lab

表側は関係性シミュレーター、裏側は反証可能な多主体ダイナミクス実験基盤です。

この初期版は `Relationship OS v4.1 - Advanced Dynamics` の三層構造を、再現可能な最小実験へ落としています。

- **Micro**: エージェント内部状態、Theory of Mind、減衰する関係記憶
- **Meso**: 信頼、対立、観測、ゴシップ
- **Macro**: Observerによる和解イベント生成

## Experiment v0.1: Observer targeting falsification

### 命題

誤解が最大の関係へ介入するObserverは、同じ回数・同じ強度のランダム介入および無介入より、最終局面の誤解を減らすか。

### 固定設計

- 主指標: 関係エッジ上の方向付きToM誤差の平均（最終20ステップ平均）
- ベースライン: 無介入
- 反証対照: ランダムな関係への同量介入
- 成功ゲート:
  1. `targeted / none <= 0.90`
  2. 70%以上のシードでtargetedがrandomを上回る
  3. paired differenceの95% bootstrap CI上限が0未満

全条件は初期状態、環境ノイズ、観測ノイズ、相互作用順序を共有します。

## Local run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ai-dokimemo-experiment --output artifacts/experiment_v0_1 --seeds 30
```

生成物:

- `summary.json`: 判定と効果量
- `seed_results.csv`: シード別結果
- `timeseries.csv`: 時系列
- `REPORT.md`: 日本語実験報告
- `misunderstanding_timeseries.png`
- `outcome_boxplot.png`

GitHub Actionsでも同じ30シード実験を実行し、成果物をartifactとして保存します。

## 非主張

この実験はtoy model内部の因果機構を検証します。人間の心理、恋愛行動、社会全体への妥当性はまだ主張しません。

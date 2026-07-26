"""Paired falsification experiment for the Observer intervention."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .simulation import Condition, SimulationConfig, run_simulation


def _bootstrap_ci(values: np.ndarray, seed: int = 20260726) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    if len(values) == 1:
        return float(values[0]), float(values[0])
    samples = rng.choice(values, size=(10_000, len(values)), replace=True).mean(axis=1)
    low, high = np.quantile(samples, [0.025, 0.975])
    return float(low), float(high)


def run_experiment(
    output_dir: str | Path,
    seeds: int = 30,
    steps: int = 140,
    agents: int = 16,
) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    config = SimulationConfig(n_agents=agents, n_steps=steps)

    rows: list[dict[str, object]] = []
    time_rows: list[dict[str, object]] = []

    for seed in range(seeds):
        for condition in Condition:
            result = run_simulation(seed=seed, condition=condition, config=config)
            rows.append(
                {
                    "seed": seed,
                    "condition": condition.value,
                    "tail_misunderstanding": result.tail_mean("misunderstanding"),
                    "tail_trust": result.tail_mean("trust"),
                    "tail_conflict": result.tail_mean("conflict"),
                    "final_misunderstanding": float(result.metrics["misunderstanding"][-1]),
                    "final_trust": float(result.metrics["trust"][-1]),
                    "intervention_count": len(result.interventions),
                }
            )
            for step in range(steps):
                time_rows.append(
                    {
                        "seed": seed,
                        "condition": condition.value,
                        "step": step,
                        "misunderstanding": float(result.metrics["misunderstanding"][step]),
                        "trust": float(result.metrics["trust"][step]),
                        "conflict": float(result.metrics["conflict"][step]),
                    }
                )

    df = pd.DataFrame(rows)
    time_df = pd.DataFrame(time_rows)
    df.to_csv(output / "seed_results.csv", index=False)
    time_df.to_csv(output / "timeseries.csv", index=False)

    pivot_mis = df.pivot(index="seed", columns="condition", values="tail_misunderstanding")
    pivot_trust = df.pivot(index="seed", columns="condition", values="tail_trust")

    targeted_vs_none = pivot_mis["targeted"] - pivot_mis["none"]
    targeted_vs_random = pivot_mis["targeted"] - pivot_mis["random"]
    relative_ratio = pivot_mis["targeted"] / pivot_mis["none"]
    trust_gain = pivot_trust["targeted"] - pivot_trust["none"]

    ci_none = _bootstrap_ci(targeted_vs_none.to_numpy())
    ci_random = _bootstrap_ci(targeted_vs_random.to_numpy(), seed=20260727)
    ratio_ci = _bootstrap_ci(relative_ratio.to_numpy(), seed=20260728)

    gate_ratio = float(relative_ratio.mean()) <= 0.90
    gate_targeting = float((targeted_vs_random < 0).mean()) >= 0.70
    gate_ci = ci_none[1] < 0.0
    verdict = "SUPPORTED" if gate_ratio and gate_targeting and gate_ci else "NOT_SUPPORTED"

    summary: dict[str, object] = {
        "experiment": "observer_targeting_falsification_v0.1",
        "primary_hypothesis": (
            "Targeted reconciliation reduces tail mean misunderstanding to at most "
            "90% of the no-intervention baseline under paired seeds."
        ),
        "seeds": seeds,
        "steps": steps,
        "agents": agents,
        "primary_metric": "mean directed misunderstanding over relationship edges, averaged over final 20 steps",
        "baseline": "no Observer intervention with identical exogenous random schedule",
        "falsification_control": "same-dose reconciliation applied to a random relationship edge",
        "means": {
            condition: {
                "tail_misunderstanding": float(
                    df.loc[df.condition == condition, "tail_misunderstanding"].mean()
                ),
                "tail_trust": float(df.loc[df.condition == condition, "tail_trust"].mean()),
                "tail_conflict": float(
                    df.loc[df.condition == condition, "tail_conflict"].mean()
                ),
            }
            for condition in ["none", "random", "targeted"]
        },
        "paired_effects": {
            "targeted_minus_none_misunderstanding": float(targeted_vs_none.mean()),
            "targeted_minus_none_95pct_bootstrap_ci": list(ci_none),
            "targeted_minus_random_misunderstanding": float(targeted_vs_random.mean()),
            "targeted_minus_random_95pct_bootstrap_ci": list(ci_random),
            "targeted_over_none_ratio": float(relative_ratio.mean()),
            "targeted_over_none_ratio_95pct_bootstrap_ci": list(ratio_ci),
            "targeted_beats_random_seed_fraction": float((targeted_vs_random < 0).mean()),
            "targeted_minus_none_trust": float(trust_gain.mean()),
        },
        "decision_gates": {
            "ratio_at_most_0.90": gate_ratio,
            "beats_random_in_at_least_70pct_seeds": gate_targeting,
            "paired_difference_ci_below_zero": gate_ci,
        },
        "verdict": verdict,
        "non_claims": [
            "This does not validate human psychology or romantic behavior.",
            "This does not prove the Observer policy is optimal outside this toy model.",
            "The result tests the implementation-level causal mechanism only.",
        ],
    }

    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    mean_time = time_df.groupby(["condition", "step"], as_index=False)[
        ["misunderstanding", "trust", "conflict"]
    ].mean()

    plt.figure(figsize=(8, 5))
    for condition in ["none", "random", "targeted"]:
        sub = mean_time[mean_time.condition == condition]
        plt.plot(sub.step, sub.misunderstanding, label=condition)
    plt.xlabel("Step")
    plt.ylabel("Mean misunderstanding")
    plt.title("Observer intervention falsification")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "misunderstanding_timeseries.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    ordered = [
        df.loc[df.condition == condition, "tail_misunderstanding"].to_numpy()
        for condition in ["none", "random", "targeted"]
    ]
    plt.boxplot(ordered, tick_labels=["none", "random", "targeted"])
    plt.ylabel("Tail mean misunderstanding")
    plt.title("Paired-seed outcome distribution")
    plt.tight_layout()
    plt.savefig(output / "outcome_boxplot.png", dpi=180)
    plt.close()

    report = f"""# AIどきメモ Observer介入実験 v0.1

## 命題

誤解が最大の関係へ和解介入を行うと、同一乱数系列の無介入条件に対し、最終20ステップの平均誤解を10%以上低下させるか。

## 設計

- シード数: {seeds}
- エージェント数: {agents}
- ステップ数: {steps}
- 主指標: 関係エッジ上の方向付きToM誤差の平均（最終20ステップ平均）
- ベースライン: 無介入
- 反証対照: 同じ回数・同じ強度のランダム関係介入
- 乱数制御: 初期条件、観測ノイズ、環境ノイズ、相互作用順序を条件間で共有

## 結果

- 無介入 平均誤解: {summary['means']['none']['tail_misunderstanding']:.6f}
- ランダム介入 平均誤解: {summary['means']['random']['tail_misunderstanding']:.6f}
- 対象選択介入 平均誤解: {summary['means']['targeted']['tail_misunderstanding']:.6f}
- 対象選択 / 無介入 比: {summary['paired_effects']['targeted_over_none_ratio']:.4f}
- 対象選択 - 無介入: {summary['paired_effects']['targeted_minus_none_misunderstanding']:.6f}
- 95% bootstrap CI: [{ci_none[0]:.6f}, {ci_none[1]:.6f}]
- 対象選択がランダム介入を上回ったシード割合: {summary['paired_effects']['targeted_beats_random_seed_fraction']:.3f}
- 判定: **{verdict}**

## 判定ゲート

- 対象選択 / 無介入 <= 0.90: {gate_ratio}
- 70%以上のシードでランダム介入より良い: {gate_targeting}
- 対応差の95% CI上限 < 0: {gate_ci}

## 解釈限界

これはRelationship OSの実装内で、Observerの「対象選択」に因果効果があるかを試すtoy-model実験です。人間心理、恋愛、現実社会への外的妥当性は主張しません。
"""
    (output / "REPORT.md").write_text(report, encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/experiment_v0_1")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--steps", type=int, default=140)
    parser.add_argument("--agents", type=int, default=16)
    args = parser.parse_args()
    summary = run_experiment(args.output, args.seeds, args.steps, args.agents)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

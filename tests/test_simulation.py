import numpy as np

from ai_dokimemo.simulation import Condition, SimulationConfig, run_simulation


def small_config() -> SimulationConfig:
    return SimulationConfig(
        n_agents=8,
        n_steps=35,
        interactions_per_step=12,
        gossip_per_step=2,
        intervention_start=5,
        intervention_interval=5,
    )


def test_same_seed_is_deterministic() -> None:
    first = run_simulation(11, Condition.TARGETED, small_config())
    second = run_simulation(11, Condition.TARGETED, small_config())
    for metric in first.metrics:
        np.testing.assert_allclose(first.metrics[metric], second.metrics[metric])


def test_state_and_relationship_bounds() -> None:
    result = run_simulation(3, Condition.RANDOM, small_config())
    final = result.final_state
    assert np.all((final["states"] >= 0.0) & (final["states"] <= 1.0))
    assert np.all((final["beliefs"] >= 0.0) & (final["beliefs"] <= 1.0))
    mask = final["adjacency"]
    assert np.all((final["trust"][mask] >= 0.01) & (final["trust"][mask] <= 1.0))
    assert np.all((final["conflict"][mask] >= 0.0) & (final["conflict"][mask] <= 1.0))
    assert np.all((final["memory"][mask] >= -1.0) & (final["memory"][mask] <= 1.0))


def test_reconciliation_immediately_reduces_selected_pair_error() -> None:
    result = run_simulation(7, Condition.TARGETED, small_config())
    assert result.interventions
    for event in result.interventions:
        assert event["pair_misunderstanding_after"] < event["pair_misunderstanding_before"]


def test_no_condition_has_no_interventions() -> None:
    result = run_simulation(5, Condition.NONE, small_config())
    assert result.interventions == []

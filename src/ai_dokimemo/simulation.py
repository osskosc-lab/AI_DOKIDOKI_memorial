"""Core relationship-dynamics simulation.

The model keeps the v4.1 three-layer structure:
- Micro: latent state, Theory-of-Mind beliefs, and decaying relational memory.
- Meso: trust, conflict, observation, and gossip on a fixed relationship graph.
- Macro: an Observer may inject a reconciliation event.

The experiment deliberately keeps the graph fixed so the three conditions can share
exactly the same exogenous random schedule. This gives a paired causal comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np


class Condition(str, Enum):
    """Observer policy used in a simulation run."""

    NONE = "none"
    RANDOM = "random"
    TARGETED = "targeted"


@dataclass(frozen=True)
class SimulationConfig:
    n_agents: int = 16
    n_steps: int = 140
    edge_probability: float = 0.22
    interactions_per_step: int = 32
    gossip_per_step: int = 5
    intervention_start: int = 20
    intervention_interval: int = 10
    observation_noise: float = 0.11
    environment_noise: float = 0.025
    memory_decay: float = 0.94
    reconciliation_strength: float = 0.58

    def validate(self) -> None:
        if self.n_agents < 4:
            raise ValueError("n_agents must be at least 4")
        if self.n_steps < 2:
            raise ValueError("n_steps must be at least 2")
        if not 0.0 <= self.edge_probability <= 1.0:
            raise ValueError("edge_probability must be in [0, 1]")
        if self.interactions_per_step < 1:
            raise ValueError("interactions_per_step must be positive")
        if self.gossip_per_step < 0:
            raise ValueError("gossip_per_step must be non-negative")
        if self.intervention_interval < 1:
            raise ValueError("intervention_interval must be positive")


@dataclass
class SimulationResult:
    seed: int
    condition: Condition
    metrics: dict[str, np.ndarray]
    final_state: dict[str, np.ndarray]
    interventions: list[dict[str, Any]]

    def tail_mean(self, metric: str, tail: int = 20) -> float:
        values = self.metrics[metric]
        return float(np.mean(values[-min(tail, len(values)) :]))


def _make_adjacency(rng: np.random.Generator, n: int, p: float) -> np.ndarray:
    """Create a connected undirected graph: ring backbone plus random shortcuts."""
    adjacency = np.zeros((n, n), dtype=bool)
    for i in range(n):
        j = (i + 1) % n
        adjacency[i, j] = adjacency[j, i] = True

    draws = rng.random((n, n))
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if draws[i, j] < p:
                adjacency[i, j] = adjacency[j, i] = True
    np.fill_diagonal(adjacency, False)
    return adjacency


def _edge_list(adjacency: np.ndarray) -> np.ndarray:
    return np.argwhere(np.triu(adjacency, k=1))


def _directed_misunderstanding(
    beliefs: np.ndarray, states: np.ndarray, adjacency: np.ndarray
) -> np.ndarray:
    errors = 0.5 * np.sum((beliefs - states[np.newaxis, :, :]) ** 2, axis=2)
    mask = adjacency.astype(float)
    denom = max(float(mask.sum()), 1.0)
    return np.array([(errors * mask).sum() / denom], dtype=float)


def _metric_snapshot(
    beliefs: np.ndarray,
    states: np.ndarray,
    trust: np.ndarray,
    conflict: np.ndarray,
    memory: np.ndarray,
    adjacency: np.ndarray,
) -> dict[str, float]:
    mask = adjacency
    directed_mis = float(_directed_misunderstanding(beliefs, states, adjacency)[0])
    return {
        "misunderstanding": directed_mis,
        "trust": float(np.mean(trust[mask])),
        "conflict": float(np.mean(conflict[mask])),
        "positive_memory": float(np.mean(memory[mask])),
        "state_dispersion": float(np.mean(np.var(states, axis=0))),
    }


def _precompute_schedule(
    seed: int, config: SimulationConfig, adjacency: np.ndarray
) -> dict[str, np.ndarray]:
    """Generate all exogenous randomness once for paired-condition comparability."""
    rng = np.random.default_rng(seed + 1_000_003)
    edges = _edge_list(adjacency)
    n_edges = len(edges)
    n = config.n_agents
    t = config.n_steps
    k = config.interactions_per_step
    g = config.gossip_per_step

    interaction_edge_indices = rng.integers(0, n_edges, size=(t, k))
    interaction_directions = rng.integers(0, 2, size=(t, k))
    observation_noise = rng.normal(0.0, config.observation_noise, size=(t, k, 2))
    environment_noise = rng.normal(0.0, config.environment_noise, size=(t, n, 2))
    common_environment = rng.normal(0.0, 0.012, size=(t, 2))

    gossip_sources = rng.integers(0, n, size=(t, g)) if g else np.empty((t, 0), int)
    gossip_targets = rng.integers(0, n, size=(t, g)) if g else np.empty((t, 0), int)
    gossip_neighbor_rank = rng.random((t, g)) if g else np.empty((t, 0), float)
    random_intervention_edge = rng.integers(0, n_edges, size=t)

    return {
        "edges": edges,
        "interaction_edge_indices": interaction_edge_indices,
        "interaction_directions": interaction_directions,
        "observation_noise": observation_noise,
        "environment_noise": environment_noise,
        "common_environment": common_environment,
        "gossip_sources": gossip_sources,
        "gossip_targets": gossip_targets,
        "gossip_neighbor_rank": gossip_neighbor_rank,
        "random_intervention_edge": random_intervention_edge,
    }


def _select_targeted_edge(
    edges: np.ndarray,
    beliefs: np.ndarray,
    states: np.ndarray,
    conflict: np.ndarray,
) -> tuple[int, int, float]:
    scores = []
    for u, v in edges:
        uv = 0.5 * np.sum((beliefs[u, v] - states[v]) ** 2)
        vu = 0.5 * np.sum((beliefs[v, u] - states[u]) ** 2)
        score = float((uv + vu) * (0.30 + conflict[u, v]))
        scores.append(score)
    index = int(np.argmax(np.asarray(scores)))
    u, v = map(int, edges[index])
    return u, v, float(scores[index])


def _reconcile(
    u: int,
    v: int,
    beliefs: np.ndarray,
    states: np.ndarray,
    trust: np.ndarray,
    conflict: np.ndarray,
    memory: np.ndarray,
    strength: float,
) -> None:
    beliefs[u, v] = (1.0 - strength) * beliefs[u, v] + strength * states[v]
    beliefs[v, u] = (1.0 - strength) * beliefs[v, u] + strength * states[u]
    trust[u, v] = trust[v, u] = np.clip(trust[u, v] + 0.075, 0.01, 1.0)
    conflict[u, v] = conflict[v, u] = np.clip(conflict[u, v] - 0.14, 0.0, 1.0)
    memory[u, v] = memory[v, u] = np.clip(memory[u, v] + 0.24, -1.0, 1.0)


def run_simulation(
    seed: int,
    condition: Condition | str,
    config: SimulationConfig | None = None,
) -> SimulationResult:
    """Run one deterministic simulation for a seed and Observer condition."""
    config = config or SimulationConfig()
    config.validate()
    condition = Condition(condition)

    init_rng = np.random.default_rng(seed)
    n = config.n_agents
    adjacency = _make_adjacency(init_rng, n, config.edge_probability)
    schedule = _precompute_schedule(seed, config, adjacency)
    edges = schedule["edges"]

    states = np.clip(init_rng.normal(0.5, 0.16, size=(n, 2)), 0.0, 1.0)
    beliefs = np.clip(
        states[np.newaxis, :, :] + init_rng.normal(0.0, 0.24, size=(n, n, 2)),
        0.0,
        1.0,
    )
    for i in range(n):
        beliefs[i, i] = states[i]

    trust = np.zeros((n, n), dtype=float)
    conflict = np.zeros((n, n), dtype=float)
    memory = np.zeros((n, n), dtype=float)
    base_trust = init_rng.uniform(0.18, 0.45, size=(n, n))
    base_conflict = init_rng.uniform(0.02, 0.22, size=(n, n))
    trust[adjacency] = base_trust[adjacency]
    conflict[adjacency] = base_conflict[adjacency]
    trust = (trust + trust.T) / 2.0
    conflict = (conflict + conflict.T) / 2.0

    metric_names = [
        "misunderstanding",
        "trust",
        "conflict",
        "positive_memory",
        "state_dispersion",
    ]
    metrics = {name: np.zeros(config.n_steps, dtype=float) for name in metric_names}
    interventions: list[dict[str, Any]] = []

    for step in range(config.n_steps):
        memory *= config.memory_decay
        np.fill_diagonal(memory, 0.0)

        states = np.clip(
            states
            + schedule["common_environment"][step]
            + schedule["environment_noise"][step],
            0.0,
            1.0,
        )

        for q in range(config.interactions_per_step):
            edge_index = int(schedule["interaction_edge_indices"][step, q])
            a, b = map(int, edges[edge_index])
            if int(schedule["interaction_directions"][step, q]) == 0:
                u, v = a, b
            else:
                u, v = b, a

            noise_scale = 0.55 + 0.80 * conflict[u, v] - 0.35 * trust[u, v]
            observation = np.clip(
                states[v] + schedule["observation_noise"][step, q] * noise_scale,
                0.0,
                1.0,
            )
            alpha = np.clip(0.06 + 0.38 * trust[u, v] + 0.08 * memory[u, v], 0.03, 0.55)
            beliefs[u, v] = (1.0 - alpha) * beliefs[u, v] + alpha * observation

            error = float(np.sqrt(np.mean((beliefs[u, v] - states[v]) ** 2)))
            emotional_gap = float(abs(states[u, 0] - states[v, 0]))
            coherence = 1.0 - np.clip(error / 0.75, 0.0, 1.0)

            d_trust = 0.012 * (coherence - 0.48) + 0.006 * memory[u, v]
            d_conflict = 0.011 * (emotional_gap + error - 0.48) - 0.005 * memory[u, v]
            new_trust = np.clip(trust[u, v] + d_trust, 0.01, 1.0)
            new_conflict = np.clip(conflict[u, v] + d_conflict, 0.0, 1.0)
            trust[u, v] = trust[v, u] = new_trust
            conflict[u, v] = conflict[v, u] = new_conflict

            memory_delta = 0.025 * (coherence - new_conflict)
            memory[u, v] = memory[v, u] = np.clip(memory[u, v] + memory_delta, -1.0, 1.0)

            support = (new_trust - new_conflict - 0.15) * 0.004
            states[u, 0] = np.clip(states[u, 0] + support, 0.0, 1.0)
            states[v, 0] = np.clip(states[v, 0] + support * 0.35, 0.0, 1.0)

        for q in range(config.gossip_per_step):
            source = int(schedule["gossip_sources"][step, q])
            neighbors = np.flatnonzero(adjacency[source])
            if len(neighbors) == 0:
                continue
            rank = int(schedule["gossip_neighbor_rank"][step, q] * len(neighbors))
            receiver = int(neighbors[min(rank, len(neighbors) - 1)])
            target = int(schedule["gossip_targets"][step, q])
            if target in (source, receiver):
                target = (target + 2) % n
            weight = np.clip(0.04 + 0.22 * trust[source, receiver], 0.04, 0.28)
            beliefs[receiver, target] = np.clip(
                (1.0 - weight) * beliefs[receiver, target]
                + weight * beliefs[source, target],
                0.0,
                1.0,
            )

        should_intervene = (
            condition is not Condition.NONE
            and step >= config.intervention_start
            and (step - config.intervention_start) % config.intervention_interval == 0
        )
        if should_intervene:
            if condition is Condition.TARGETED:
                u, v, score = _select_targeted_edge(edges, beliefs, states, conflict)
            else:
                edge_index = int(schedule["random_intervention_edge"][step])
                u, v = map(int, edges[edge_index])
                score = float("nan")
            before = float(
                0.5 * np.sum((beliefs[u, v] - states[v]) ** 2)
                + 0.5 * np.sum((beliefs[v, u] - states[u]) ** 2)
            )
            _reconcile(
                u,
                v,
                beliefs,
                states,
                trust,
                conflict,
                memory,
                config.reconciliation_strength,
            )
            after = float(
                0.5 * np.sum((beliefs[u, v] - states[v]) ** 2)
                + 0.5 * np.sum((beliefs[v, u] - states[u]) ** 2)
            )
            interventions.append(
                {
                    "step": step,
                    "u": u,
                    "v": v,
                    "selection_score": score,
                    "pair_misunderstanding_before": before,
                    "pair_misunderstanding_after": after,
                }
            )

        snapshot = _metric_snapshot(beliefs, states, trust, conflict, memory, adjacency)
        for name, value in snapshot.items():
            metrics[name][step] = value

    return SimulationResult(
        seed=seed,
        condition=condition,
        metrics=metrics,
        final_state={
            "states": states.copy(),
            "beliefs": beliefs.copy(),
            "trust": trust.copy(),
            "conflict": conflict.copy(),
            "memory": memory.copy(),
            "adjacency": adjacency.copy(),
        },
        interventions=interventions,
    )

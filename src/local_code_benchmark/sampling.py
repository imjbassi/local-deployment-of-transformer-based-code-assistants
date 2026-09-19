"""Analysis for the 20-sample stochastic sensitivity condition.

The preregistered sampling condition reports pass@1 and pass@5 with the
unbiased HumanEval estimator and paired task-bootstrap intervals. Sampling
results are a secondary condition; they never replace the greedy primary
endpoint.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .metrics import bootstrap_mean_ci, task_pass_at_k

DEFAULT_K = (1, 5)


def load_sample_outcomes(payload: dict[str, Any]) -> dict[str, list[tuple[bool, bool]]]:
    """Return per-task HumanEval and HumanEval+ outcomes for every sample."""
    evaluations = payload.get("eval")
    if not isinstance(evaluations, dict) or not evaluations:
        raise ValueError("EvalPlus result has no 'eval' object")
    outcomes: dict[str, list[tuple[bool, bool]]] = {}
    for task_id, attempts in sorted(evaluations.items()):
        if not isinstance(attempts, list) or not attempts:
            raise ValueError(f"{task_id} has no evaluated samples")
        task: list[tuple[bool, bool]] = []
        for attempt in attempts:
            base_passed = attempt.get("base_status") == "pass"
            task.append((base_passed, base_passed and attempt.get("plus_status") == "pass"))
        outcomes[task_id] = task
    sample_counts = {len(values) for values in outcomes.values()}
    if len(sample_counts) != 1:
        raise ValueError(
            f"every task requires the same sample count; found {sorted(sample_counts)}"
        )
    return outcomes


def analyze_samples(
    outcomes: dict[str, list[tuple[bool, bool]]],
    *,
    k_values: tuple[int, ...] = DEFAULT_K,
    expected_tasks: int = 164,
    bootstrap_replicates: int = 10_000,
    seed: int = 2026,
) -> dict[str, Any]:
    """Return pass@k point estimates and task-bootstrap intervals."""
    if len(outcomes) != expected_tasks:
        raise ValueError(f"expected {expected_tasks} tasks; found {len(outcomes)}")
    tasks = sorted(outcomes)
    n_samples = len(outcomes[tasks[0]])
    result: dict[str, Any] = {
        "n_samples": n_samples,
        "expected_tasks": expected_tasks,
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": seed,
        "pass_at_k": {},
    }
    for index, benchmark in enumerate(("humaneval", "humaneval_plus")):
        per_benchmark: dict[str, Any] = {}
        for k in k_values:
            estimates = task_pass_at_k(
                ([outcomes[task][sample][index] for sample in range(n_samples)] for task in tasks),
                k,
            )
            point = sum(estimates) / len(estimates)
            interval = bootstrap_mean_ci(
                estimates, replicates=bootstrap_replicates, seed=seed + k + index
            )
            per_benchmark[f"pass_at_{k}"] = {
                "estimate": point,
                "bootstrap_ci_95": list(interval),
            }
        result["pass_at_k"][benchmark] = per_benchmark
    return result


def paired_pass_at_k_difference(
    condition: dict[str, list[tuple[bool, bool]]],
    baseline: dict[str, list[tuple[bool, bool]]],
    *,
    k: int = 1,
    benchmark_index: int = 0,
    bootstrap_replicates: int = 10_000,
    seed: int = 2026,
) -> dict[str, Any]:
    """Compare two conditions on the same tasks.

    Both conditions must cover the identical task set. The per-task pass@k
    estimates are differenced task by task, so the bootstrap resamples tasks
    while keeping each task's paired outcome together.
    """
    if set(condition) != set(baseline):
        raise ValueError("both conditions must contain the identical task IDs")
    tasks = sorted(condition)

    def estimates(outcomes: dict[str, list[tuple[bool, bool]]]) -> list[float]:
        n_samples = len(outcomes[tasks[0]])
        return task_pass_at_k(
            (
                [outcomes[task][sample][benchmark_index] for sample in range(n_samples)]
                for task in tasks
            ),
            k,
        )

    differences = [a - b for a, b in zip(estimates(condition), estimates(baseline), strict=True)]
    interval = bootstrap_mean_ci(differences, replicates=bootstrap_replicates, seed=seed)
    return {
        "k": k,
        "difference": sum(differences) / len(differences),
        "paired_bootstrap_ci_95": list(interval),
        "excludes_zero": interval[0] > 0 or interval[1] < 0,
    }


def parse_result(value: str) -> tuple[str, Path]:
    label, separator, raw_path = value.partition("=")
    if not separator or not label or not raw_path:
        raise argparse.ArgumentTypeError("results must use LABEL=PATH")
    return label, Path(raw_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze the 20-sample sensitivity condition.")
    parser.add_argument(
        "--result", action="append", required=True, type=parse_result, metavar="LABEL=PATH"
    )
    parser.add_argument("--expected-tasks", type=int, default=164)
    parser.add_argument("--bootstrap-replicates", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    conditions = {}
    for label, path in args.result:
        payload = json.loads(path.read_text(encoding="utf-8"))
        conditions[label] = analyze_samples(
            load_sample_outcomes(payload),
            expected_tasks=args.expected_tasks,
            bootstrap_replicates=args.bootstrap_replicates,
            seed=args.seed,
        )
    report = {"condition": "sampling_sensitivity", "results": conditions}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

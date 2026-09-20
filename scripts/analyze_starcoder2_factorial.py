#!/usr/bin/env python3
"""Describe StarCoder2 continuation behavior across the 2x2 prompt/stop factorial.

This script treats model outputs as text. It does not import or execute generated code.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Any

from evalplus.data import get_human_eval_plus

TOP_LEVEL_DEF = re.compile(r"(?m)^def\s+([A-Za-z_]\w*)\s*\(")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--no-new-def-stop", type=Path, required=True)
    parser.add_argument("--no-trailing-newline", type=Path, required=True)
    parser.add_argument("--neither", type=Path, required=True)
    parser.add_argument("--no-trailing-newline-sanitized", type=Path, required=True)
    parser.add_argument("--neither-sanitized", type=Path, required=True)
    parser.add_argument("--no-trailing-newline-eval", type=Path, required=True)
    parser.add_argument("--neither-eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_jsonl(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            task_id = row["task_id"]
            if task_id in rows:
                raise ValueError(f"duplicate task ID in {path}: {task_id}")
            rows[task_id] = row["solution"]
    return rows


def summarize_condition(
    *,
    path: Path,
    trailing_newline: bool,
    new_def_stop: bool,
    tasks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rows = load_jsonl(path)
    expected = set(tasks)
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise ValueError(f"task mismatch in {path}: missing={missing}, extra={extra}")

    metric_ids: dict[str, list[str]] = {
        "empty_completion": [],
        "any_top_level_def": [],
        "repeated_entry_point_def": [],
        "additional_top_level_def": [],
    }
    completion_lengths: list[int] = []
    for task_id, task in tasks.items():
        prompt = task["prompt"].strip() + ("\n" if trailing_newline else "")
        solution = rows[task_id]
        if not solution.startswith(prompt):
            raise ValueError(f"solution for {task_id} in {path} does not preserve its prompt")
        completion = solution[len(prompt) :]
        completion_lengths.append(len(completion))
        definitions = TOP_LEVEL_DEF.findall(completion)
        entry_point = task["entry_point"]

        if not completion.strip():
            metric_ids["empty_completion"].append(task_id)
        if definitions:
            metric_ids["any_top_level_def"].append(task_id)
        if entry_point in definitions:
            metric_ids["repeated_entry_point_def"].append(task_id)
        if any(name != entry_point for name in definitions):
            metric_ids["additional_top_level_def"].append(task_id)

    total = len(tasks)
    metrics = {
        name: {
            "count": len(task_ids),
            "rate": len(task_ids) / total,
            "task_ids": task_ids,
        }
        for name, task_ids in metric_ids.items()
    }
    return {
        "path": str(path),
        "trailing_prompt_newline": trailing_newline,
        "new_def_stop": new_def_stop,
        "tasks": total,
        "metrics": metrics,
        "completion_characters": {
            "minimum": min(completion_lengths),
            "median": statistics.median(completion_lengths),
            "mean": statistics.fmean(completion_lengths),
            "maximum": max(completion_lengths),
        },
    }


def compare_sanitized(
    *,
    baseline_path: Path,
    factorial_path: Path,
    baseline_eval_path: Path,
) -> dict[str, Any]:
    baseline = load_jsonl(baseline_path)
    factorial = load_jsonl(factorial_path)
    if set(baseline) != set(factorial):
        raise ValueError("sanitized factorial files do not contain the same tasks")

    different = [task_id for task_id in baseline if baseline[task_id] != factorial[task_id]]
    eval_rows = json.loads(baseline_eval_path.read_text(encoding="utf-8"))["eval"]
    baseline_passes = {
        "humaneval": [
            task_id
            for task_id, rows in eval_rows.items()
            if rows[0]["base_status"] == "pass"
        ],
        "humaneval_plus": [
            task_id
            for task_id, rows in eval_rows.items()
            if rows[0]["base_status"] == "pass" and rows[0]["plus_status"] == "pass"
        ],
    }
    baseline_passes_in_different = {
        benchmark: sorted(set(task_ids) & set(different))
        for benchmark, task_ids in baseline_passes.items()
    }
    preserved_passes = {
        benchmark: len(task_ids) - len(baseline_passes_in_different[benchmark])
        for benchmark, task_ids in baseline_passes.items()
    }
    return {
        "baseline_path": str(baseline_path),
        "factorial_path": str(factorial_path),
        "baseline_eval_path": str(baseline_eval_path),
        "identical_candidates": len(baseline) - len(different),
        "different_candidates": len(different),
        "different_task_ids": different,
        "baseline_passes_in_different_candidates": baseline_passes_in_different,
        "preserved_baseline_passes": preserved_passes,
        "factorial_score_bounds": {
            benchmark: [count, count + len(different)]
            for benchmark, count in preserved_passes.items()
        },
        "interpretation": (
            "Static byte comparison only. Bounds are not a hardened evaluation result; "
            "the upper endpoint assumes every changed candidate passes."
        ),
    }


def summarize_hardened_evaluation(
    *, baseline_eval_path: Path, factorial_eval_path: Path
) -> dict[str, Any]:
    def outcomes(path: Path) -> dict[str, tuple[bool, bool]]:
        rows = json.loads(path.read_text(encoding="utf-8"))["eval"]
        return {
            task_id: (
                result[0]["base_status"] == "pass",
                result[0]["base_status"] == "pass"
                and result[0]["plus_status"] == "pass",
            )
            for task_id, result in rows.items()
        }

    baseline = outcomes(baseline_eval_path)
    factorial = outcomes(factorial_eval_path)
    if set(baseline) != set(factorial):
        raise ValueError("hardened evaluator outputs do not contain the same tasks")

    benchmarks = {"humaneval": 0, "humaneval_plus": 1}
    scores: dict[str, int] = {}
    transitions: dict[str, dict[str, int]] = {}
    for benchmark, index in benchmarks.items():
        scores[benchmark] = sum(result[index] for result in factorial.values())
        transitions[benchmark] = {
            "fail_to_pass": sum(
                not baseline[task_id][index] and factorial[task_id][index]
                for task_id in baseline
            ),
            "pass_to_fail": sum(
                baseline[task_id][index] and not factorial[task_id][index]
                for task_id in baseline
            ),
        }
    return {
        "status": "complete",
        "baseline_eval_path": str(baseline_eval_path),
        "factorial_eval_path": str(factorial_eval_path),
        "scores": scores,
        "transitions_vs_no_trailing_newline": transitions,
    }


def main() -> None:
    args = parse_args()
    tasks = get_human_eval_plus(version="v0.1.10")
    conditions = {
        "stock": (args.stock, True, True),
        "no_new_def_stop": (args.no_new_def_stop, True, False),
        "no_trailing_newline": (args.no_trailing_newline, False, True),
        "no_trailing_newline_no_new_def_stop": (args.neither, False, False),
    }
    output = {
        "analysis": "starcoder2_prompt_newline_by_new_def_stop_factorial",
        "dataset": "HumanEval+ v0.1.10 prompts; 164 HumanEval tasks",
        "safety": "text-only analysis; generated code was not imported or executed",
        "conditions": {
            name: summarize_condition(
                path=path.resolve(),
                trailing_newline=trailing_newline,
                new_def_stop=new_def_stop,
                tasks=tasks,
            )
            for name, (path, trailing_newline, new_def_stop) in conditions.items()
        },
        "sanitized_comparison": compare_sanitized(
            baseline_path=args.no_trailing_newline_sanitized.resolve(),
            factorial_path=args.neither_sanitized.resolve(),
            baseline_eval_path=args.no_trailing_newline_eval.resolve(),
        ),
        "hardened_evaluation": summarize_hardened_evaluation(
            baseline_eval_path=args.no_trailing_newline_eval.resolve(),
            factorial_eval_path=args.neither_eval.resolve(),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

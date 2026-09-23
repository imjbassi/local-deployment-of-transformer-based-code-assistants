"""Recount retained evaluator outcomes as data; never execute generated Python."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def evaluated(path: Path) -> dict[str, tuple[bool, bool]]:
    rows = json.loads(path.read_text(encoding="utf-8"))["eval"]
    expected = {f"HumanEval/{i}" for i in range(164)}
    if set(rows) != expected or any(len(value) != 1 for value in rows.values()):
        raise ValueError(f"Expected one result for every HumanEval task: {path}")
    return {
        task: (
            value[0]["base_status"] == "pass",
            value[0]["base_status"] == "pass" and value[0]["plus_status"] == "pass",
        )
        for task, value in rows.items()
    }


def audit(root: Path) -> dict:
    manifest = root / "SHA256SUMS"
    if manifest.exists():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            target = (root / relative).resolve()
            if not target.is_relative_to(root.resolve()):
                raise ValueError(f"Unsafe manifest entry: {relative}")
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Checksum mismatch: {relative}")
    targets = json.loads((root / "protocol/published_targets.json").read_text())
    models = sorted(targets["models"], key=lambda model: model["humaneval"])
    primary = {
        model["key"]: evaluated(
            root / "artifacts/primary/humaneval" / f"{model['key']}_eval_results.json"
        )
        for model in models
    }
    controls = root / "artifacts/controls"
    conditions = {
        "stock": controls / "stock-evalplus/stock-evalplus-starcoder2-3b_eval_results.json",
        "newline_no_stop": controls / "stop-ablation/starcoder2-no-new-def-stop_eval_results.json",
        "no_newline_stop": controls
        / "prompt-newline-ablation"
        / "starcoder2-3b-no-trailing-newline_eval_results.json",
        "no_newline_no_stop": controls
        / "prompt-newline-ablation"
        / "starcoder2-3b-no-trailing-newline-no-new-def-stop_eval_results.json",
    }
    results = {name: evaluated(path) for name, path in conditions.items()}
    counts = {
        name: [sum(row[i] for row in outcomes.values()) for i in (0, 1)]
        for name, outcomes in (primary | results).items()
    }
    comparisons = []
    for lower, higher in zip(models, models[1:], strict=False):
        a, b = primary[lower["key"]], primary[higher["key"]]
        wins = sum(b[task][0] and not a[task][0] for task in a)
        losses = sum(a[task][0] and not b[task][0] for task in a)
        discordant = wins + losses
        p = min(
            1.0,
            2 * sum(math.comb(discordant, i) for i in range(min(wins, losses) + 1)) / 2**discordant,
        )
        comparisons.append(
            {
                "higher": higher["key"],
                "lower": lower["key"],
                "higher_only_pass": wins,
                "lower_only_pass": losses,
                "exact_two_sided_mcnemar_p": p,
                "bonferroni_four_pairs_p": min(1.0, 4 * p),
            }
        )
    # Reconcile normalized analysis inputs against the actual evaluator records.
    rows = [
        json.loads(line)
        for line in (root / "artifacts/primary/outcomes.jsonl").read_text().splitlines()
    ]
    seen = set()
    for row in rows:
        key = row["model_key"], row["task_id"]
        if key in seen:
            raise ValueError(f"Duplicate outcome: {key}")
        seen.add(key)
        if primary[key[0]][key[1]] != (row["humaneval_passed"], row["humaneval_plus_passed"]):
            raise ValueError(f"Evaluator/normalized outcome mismatch: {key}")
    if len(seen) != 820:
        raise ValueError("Expected 820 primary model/task pairs")
    return {
        "counts_he_heplus": counts,
        "post_hoc_multiplicity_sensitivity": comparisons,
        "interpretation": "Additional paired-task sensitivity; original decision unchanged.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(audit(args.root), indent=2) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report)

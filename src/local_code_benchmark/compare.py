"""Compare two retained generation JSONL files without executing their contents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_records(path: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    records: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(lines, 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number} is not valid JSON") from exc
        task_id = record.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError(f"{path}:{line_number} has no non-empty task_id")
        if task_id in records:
            raise ValueError(f"{path} contains duplicate task_id {task_id}")
        records[task_id] = record
    return lines, records


def compare_jsonl(reference: Path, candidate: Path) -> dict[str, Any]:
    """Return file-, record-, and solution-level identity evidence."""
    reference_lines, reference_records = load_records(reference)
    candidate_lines, candidate_records = load_records(candidate)
    reference_tasks = set(reference_records)
    candidate_tasks = set(candidate_records)
    shared_tasks = sorted(reference_tasks & candidate_tasks)
    differing_records = [
        task for task in shared_tasks if reference_records[task] != candidate_records[task]
    ]
    differing_solutions = [
        task
        for task in shared_tasks
        if reference_records[task].get("solution") != candidate_records[task].get("solution")
    ]
    return {
        "reference": str(reference),
        "candidate": str(candidate),
        "reference_sha256": sha256(reference),
        "candidate_sha256": sha256(candidate),
        "reference_record_count": len(reference_lines),
        "candidate_record_count": len(candidate_lines),
        "shared_record_count": len(shared_tasks),
        "missing_from_candidate": sorted(reference_tasks - candidate_tasks),
        "extra_in_candidate": sorted(candidate_tasks - reference_tasks),
        "differing_record_task_ids": differing_records,
        "differing_solution_task_ids": differing_solutions,
        "files_byte_identical": reference.read_bytes() == candidate.read_bytes(),
        "shared_records_identical": not differing_records,
        "shared_solutions_identical": not differing_solutions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = compare_jsonl(args.reference, args.candidate)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

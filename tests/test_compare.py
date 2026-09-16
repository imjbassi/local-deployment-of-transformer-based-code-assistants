import json
from pathlib import Path

import pytest

from local_code_benchmark.compare import compare_jsonl


def write_jsonl(path: Path, records: list[dict[str, str]]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def test_compare_reports_task_level_solution_difference(tmp_path: Path) -> None:
    reference = tmp_path / "reference.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    write_jsonl(
        reference,
        [
            {"task_id": "HumanEval/0", "solution": "a"},
            {"task_id": "HumanEval/1", "solution": "b"},
        ],
    )
    write_jsonl(
        candidate,
        [
            {"task_id": "HumanEval/0", "solution": "a"},
            {"task_id": "HumanEval/1", "solution": "changed"},
        ],
    )

    result = compare_jsonl(reference, candidate)

    assert result["shared_record_count"] == 2
    assert result["differing_solution_task_ids"] == ["HumanEval/1"]
    assert result["shared_solutions_identical"] is False
    assert result["files_byte_identical"] is False


def test_compare_rejects_duplicate_tasks(tmp_path: Path) -> None:
    reference = tmp_path / "reference.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    records = [
        {"task_id": "HumanEval/0", "solution": "a"},
        {"task_id": "HumanEval/0", "solution": "b"},
    ]
    write_jsonl(reference, records)
    write_jsonl(candidate, records[:1])

    with pytest.raises(ValueError, match="duplicate task_id"):
        compare_jsonl(reference, candidate)

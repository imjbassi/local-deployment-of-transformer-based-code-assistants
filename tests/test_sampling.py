import pytest

from local_code_benchmark.sampling import analyze_samples, load_sample_outcomes


def evalplus_payload(statuses: dict[str, list[tuple[str, str]]]) -> dict:
    return {
        "eval": {
            task_id: [{"base_status": base, "plus_status": plus} for base, plus in attempts]
            for task_id, attempts in statuses.items()
        }
    }


def test_load_sample_outcomes_requires_equal_sample_counts() -> None:
    payload = evalplus_payload(
        {
            "HumanEval/0": [("pass", "pass"), ("fail", "fail")],
            "HumanEval/1": [("pass", "pass")],
        }
    )
    with pytest.raises(ValueError, match="same sample count"):
        load_sample_outcomes(payload)


def test_plus_requires_base_pass() -> None:
    payload = evalplus_payload({"HumanEval/0": [("fail", "pass")]})
    assert load_sample_outcomes(payload) == {"HumanEval/0": [(False, False)]}


def test_analyze_samples_matches_unbiased_estimator() -> None:
    # Two tasks, four samples each: one always passes, one passes twice.
    outcomes = {
        "HumanEval/0": [(True, True)] * 4,
        "HumanEval/1": [(True, False), (True, False), (False, False), (False, False)],
    }
    report = analyze_samples(
        outcomes, k_values=(1, 2), expected_tasks=2, bootstrap_replicates=100, seed=7
    )

    humaneval = report["pass_at_k"]["humaneval"]
    assert humaneval["pass_at_1"]["estimate"] == pytest.approx((1.0 + 0.5) / 2)
    # pass@2 for the second task is 1 - C(2,2)/C(4,2) = 1 - 1/6.
    assert humaneval["pass_at_2"]["estimate"] == pytest.approx((1.0 + (1 - 1 / 6)) / 2)
    assert report["pass_at_k"]["humaneval_plus"]["pass_at_1"]["estimate"] == pytest.approx(0.5)
    low, high = humaneval["pass_at_1"]["bootstrap_ci_95"]
    assert low <= humaneval["pass_at_1"]["estimate"] <= high
    assert report["n_samples"] == 4


def test_analyze_samples_rejects_unexpected_task_count() -> None:
    with pytest.raises(ValueError, match="expected 164 tasks"):
        analyze_samples({"HumanEval/0": [(True, True)]})

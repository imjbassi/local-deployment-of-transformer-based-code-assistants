import pytest

from local_code_benchmark.sampling import (
    analyze_samples,
    load_sample_outcomes,
    paired_pass_at_k_difference,
)


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


def test_paired_difference_is_signed_and_paired() -> None:
    # Every task improves, so no bootstrap resample can produce a zero mean.
    better = {f"HumanEval/{i}": [(True, True)] * 4 for i in range(4)}
    worse = {f"HumanEval/{i}": [(False, False)] * 4 for i in range(4)}

    result = paired_pass_at_k_difference(better, worse, bootstrap_replicates=200, seed=3)
    assert result["difference"] == pytest.approx(1.0)
    assert result["excludes_zero"] is True

    flipped = paired_pass_at_k_difference(worse, better, bootstrap_replicates=200, seed=3)
    assert flipped["difference"] == pytest.approx(-1.0)


def test_paired_difference_interval_can_include_zero() -> None:
    # Half the tasks improve, so resampling the unchanged task twice gives zero.
    condition = {"HumanEval/0": [(True, True)] * 4, "HumanEval/1": [(True, True)] * 4}
    baseline = {"HumanEval/0": [(True, True)] * 4, "HumanEval/1": [(False, False)] * 4}

    result = paired_pass_at_k_difference(condition, baseline, bootstrap_replicates=200, seed=3)
    assert result["difference"] == pytest.approx(0.5)
    assert result["excludes_zero"] is False


def test_paired_difference_requires_matching_tasks() -> None:
    with pytest.raises(ValueError, match="identical task IDs"):
        paired_pass_at_k_difference(
            {"HumanEval/0": [(True, True)]}, {"HumanEval/1": [(True, True)]}
        )


def test_analyze_samples_rejects_unexpected_task_count() -> None:
    with pytest.raises(ValueError, match="expected 164 tasks"):
        analyze_samples({"HumanEval/0": [(True, True)]})

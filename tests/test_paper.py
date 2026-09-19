import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manuscript_primary_table_matches_analysis() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    analysis = json.loads(
        (ROOT / "artifacts" / "primary" / "primary-analysis.json").read_text(encoding="utf-8")
    )
    counts = {
        "qwen2.5-coder-0.5b": (39, 33),
        "starcoder2-3b": (3, 3),
        "deepseek-coder-1.3b": (56, 47),
        "qwen2.5-coder-1.5b": (64, 56),
        "qwen2.5-coder-3b": (86, 70),
    }

    for model, (humaneval_count, plus_count) in counts.items():
        rates = analysis["local_rates"][model]
        humaneval = f"{100 * rates['humaneval']:.1f}\\% ({humaneval_count}/164)"
        humaneval_plus = f"{100 * rates['humaneval_plus']:.1f}\\% ({plus_count}/164)"
        assert humaneval in manuscript
        assert humaneval_plus in manuscript

    assert "Kendall's tau-b was 0.8" in manuscript
    assert "interval of [0.6, 0.8]" in manuscript
    assert "[-28.66, -15.85]" in manuscript
    assert "unmodified-EvalPlus StarCoder2 control scored 1.2\\% (2/164)" in manuscript
    assert "failed to reproduce" in manuscript.lower()


def test_manuscript_newline_ablation_matches_artifacts() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    ablation = ROOT / "artifacts" / "controls" / "prompt-newline-ablation"
    analysis = json.loads((ablation / "ablation-analysis.json").read_text(encoding="utf-8"))
    counts = {
        "qwen2.5-coder-0.5b": (37, 31),
        "starcoder2-3b": (49, 42),
        "deepseek-coder-1.3b": (54, 46),
        "qwen2.5-coder-1.5b": (67, 56),
        "qwen2.5-coder-3b": (85, 71),
    }

    for model, (humaneval_count, plus_count) in counts.items():
        rates = analysis["local_rates"][model]
        assert round(164 * rates["humaneval"]) == humaneval_count
        assert round(164 * rates["humaneval_plus"]) == plus_count

    assert analysis["kendall_tau_b"] == 1.0
    assert analysis["kendall_tau_b_bootstrap_ci_95"] == [0.8, 1.0]
    assert "29.9\\% (49/164)" in manuscript
    assert "25.6\\% (42/164)" in manuscript
    assert "tau-b was 1.0" in manuscript
    assert "does not replace the primary decision" in manuscript


def test_manuscript_sampling_table_matches_analysis() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    report = json.loads(
        (
            ROOT / "artifacts" / "controls" / "sampling-sensitivity" / "sampling-analysis.json"
        ).read_text(encoding="utf-8")
    )
    expected = {
        "qwen2.5-coder-1.5b": (37.6, 50.8),
        "deepseek-coder-1.3b": (32.2, 41.3),
        "starcoder2-3b": (2.3, 5.6),
        "starcoder2-3b-no-trailing-newline": (29.8, 40.4),
    }

    for label, (pass_at_1, pass_at_5) in expected.items():
        rates = report["results"][label]["pass_at_k"]["humaneval"]
        assert report["results"][label]["n_samples"] == 20
        assert round(100 * rates["pass_at_1"]["estimate"], 1) == pass_at_1
        assert round(100 * rates["pass_at_5"]["estimate"], 1) == pass_at_5
        assert f"{pass_at_1} [" in manuscript
        assert f"{pass_at_5} [" in manuscript

    assert "Seeds 23 and 37 were not run" in manuscript


def test_manuscript_qwen_ablations_match_artifacts() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    summary = json.loads(
        (
            ROOT / "artifacts" / "controls" / "qwen-secondary-ablations" / "summary.json"
        ).read_text(encoding="utf-8")
    )
    expected = {"chat-prompt": (48.6, 66.5, 11.07), "int8": (24.4, 34.4, -13.17)}

    for label, (pass_at_1, pass_at_5, paired) in expected.items():
        condition = summary["results"][label]
        rates = condition["pass_at_k"]["humaneval"]
        assert round(100 * rates["pass_at_1"]["estimate"], 1) == pass_at_1
        assert round(100 * rates["pass_at_5"]["estimate"], 1) == pass_at_5
        difference = condition["paired_difference_vs_reference"]["humaneval"]["pass_at_1"]
        assert round(100 * difference["difference"], 2) == paired
        assert difference["excludes_zero"] is True
        assert f"{pass_at_1} & {pass_at_5}" in manuscript

    assert "11.07" in manuscript
    assert "13.17" in manuscript


def test_manuscript_keeps_release_boundaries_explicit() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8").lower()
    assert "it does not enter the primary endpoint" in manuscript
    assert "do not show that the published score is erroneous" in manuscript
    assert "10.5281/zenodo.22800651" in manuscript


def test_rendered_pdf_is_checked_in() -> None:
    pdf = (
        ROOT
        / "paper"
        / "output"
        / "pdf"
        / "Do_Published_HumanEval_Rankings_Survive_Local_Deployment.pdf"
    )
    assert pdf.read_bytes().startswith(b"%PDF-")

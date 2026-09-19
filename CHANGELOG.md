# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Post-hoc five-model ablation that omits only the trailing newline EvalPlus
  0.3.1 appends to base-model prompts, with generations, hardened evaluator
  outputs, 820 outcomes, analysis, summary, checksums, runner
  (`scripts/prompt_newline_ablation.py`), and evaluation workflow. StarCoder2-3B
  rises from 3/164 to 49/164 on HumanEval and the published order is recovered
  (tau-b = 1.0, 95% interval [0.8, 1.0]).
- Upstream provenance for the prompt boundary (EvalPlus commits `3ff1e38` and
  `4df7001`) and for the StarCoder2 leaderboard values (StarCoder2 report
  Table 9).
- Zenodo DOI [10.5281/zenodo.22800651](https://doi.org/10.5281/zenodo.22800651) for the v1.2.0 release in the
  README, `CITATION.cff`, and manuscript.
- Preregistered 20-sample sensitivity condition (seed 11) for
  Qwen2.5-Coder-1.5B, DeepSeek-Coder-1.3B, and StarCoder2-3B, plus a post-hoc
  no-trailing-newline run for StarCoder2-3B: 13,120 completions, hardened
  evaluator outputs, pass@1 and pass@5 with task-bootstrap intervals, summary,
  and checksums. Sampling pass@1 tracks greedy pass@1 within about two points,
  and StarCoder2-3B stays at 2.3% under the stock prompt.
- `local_code_benchmark.sampling` analysis module and a guard that fails a
  sampling run when any module is placed off the GPU.
- Preregistered prompt and 8-bit ablations on Qwen2.5-Coder-1.5B at seed 11,
  with generations, hardened evaluator outputs, paired task-bootstrap
  differences, summary, and checksums. The chat-template prompt adds 11.07
  points of HumanEval pass@1 and 8-bit weights remove 13.17; both intervals
  exclude zero. All preregistered secondary conditions are now closed.
- `paired_pass_at_k_difference` for task-paired comparisons between two
  sampling conditions.

### Changed

- Manuscript version 1.3 attributes the StarCoder2 reversal to the trailing
  prompt newline, replaces the "unresolved anomaly" framing, and no longer
  describes the EvalPlus leaderboard value as an independent measurement.

## [1.2.0] - 2026-09-16

### Added

- Independent EvalPlus leaderboard values and documented greedy direct-completion
  setup as an explicit third comparison source in the manuscript.
- A complete post-hoc StarCoder2-3B ablation removing only the exact `\ndef `
  generation stop, with 164 raw and sanitized records.
- Hardened evaluator output showing 17/164 (10.4%) HumanEval and 15/164 (9.1%)
  HumanEval+ for the ablation.
- A 20-task stock-path equivalence prefix, byte-identity record, workflow run
  provenance, checksums, and machine-readable summary.

### Changed

- Reframed the residual StarCoder2 gap as an unresolved anomaly: the stop rule
  explains a substantial fraction of failures but does not recover the
  independent 31.7%/27.4% result.

## [1.1.0] - 2026-09-15

### Added

- Evidence-backed technical report for the five-model primary experiment.
- Canonical LaTeX and BibTeX sources, Tectonic build script, rendered PDF, and
  internal claim-to-evidence review.
- Regression checks tying manuscript counts and release boundaries to the
  primary analysis artifacts.
- A paired task-bootstrap interval for Kendall's tau-b (10,000 replicates,
  analysis seed 2026).
- Full unmodified-EvalPlus StarCoder2-3B control generations and two-task
  stock-harness equivalence artifacts for all five models.
- Hardened stock-control evaluator output confirming 2/164 (1.2%) on both
  HumanEval and HumanEval+.
- A non-executing JSONL comparison command for retained generation artifacts.

## [1.0.0] - 2026-09-14

### Added

- Installable `local_code_benchmark` package and command-line interface.
- Pinned HumanEval dataset provenance and runtime model revision capture.
- Deterministic sampling, warm-up runs, actual token accounting, and one-model-at-a-time loading.
- Official pass@k estimator and opt-in HumanEval functional evaluation.
- Task-bootstrap confidence intervals and separate accuracy/performance modes.
- Modern Qwen2.5-Coder, DeepSeek-Coder, and Code Llama comparison conditions.
- FP16, 8-bit, 4-bit, and prompt-prefix sensitivity controls.
- JSON/JSONL run artifacts, archive validation, unit tests, linting, packaging, and CI.
- A scoped external-ranking protocol, explicit primary endpoint, trigger-based
  compute budget, EvalPlus converter, and executable analysis command.
- Citation, contribution, security, publication-status, and license documents.

### Changed

- Replaced the divergent legacy scripts with one compatibility entry point.
- Removed the unsupported historical and self-audit manuscripts from the release
  tree; neither is a result of the new study.

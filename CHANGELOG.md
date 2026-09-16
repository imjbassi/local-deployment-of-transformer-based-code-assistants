# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

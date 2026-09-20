# Anonymous replication artifact

This history-free package supports the anonymous paper's primary ranking result
and StarCoder2 mechanism audit. It contains frozen model identifiers, retained
generations, hardened evaluator outputs, task-level analyses, evaluation image
digests, analysis code, and tests.

Generated Python in `artifacts/` is untrusted. Do not import or execute it on a
host system. Functional reevaluation must use the network-isolated container
defined in `containers/evalplus/Dockerfile`.

Key evidence:

- `artifacts/primary/primary-analysis.json` and `outcomes.jsonl`: five-model
  primary rank-transfer result.
- `artifacts/controls/prompt-newline-ablation/`: five-model newline ablation and
  complete StarCoder2 newline-by-stop factorial, including hardened results.
- `protocol/published_targets.json`: immutable model revisions and published
  targets.
- `scripts/` and `src/`: analysis and reusable implementation.
- `tests/`: executable consistency checks.

The archive excludes Git history, author metadata, release DOIs, repository
ownership, machine-specific metadata, and absolute local paths. Verify
`SHA256SUMS` before review.


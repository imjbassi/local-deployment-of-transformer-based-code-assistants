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

## Reproduce the reported numbers (no GPU and no generated-code execution)

Use Python 3.10-3.13. From the extracted archive root:

```bash
python scripts/audit_paper_evidence.py
python -m pip install --no-deps -e .
python -m local_code_benchmark.analyze artifacts/primary/outcomes.jsonl --output primary-recomputed.json
python -m local_code_benchmark.analyze artifacts/controls/prompt-newline-ablation/outcomes.jsonl --output newline-recomputed.json
```

The first command verifies the root SHA-256 manifest, checks the 164 task IDs
per greedy evaluator file, reconciles all 820 primary outcomes, and recounts
the controls. Expected counts (HE / HE+): primary StarCoder2 3/3, unmodified
provider 2/2, stop ablation 17/15, no-newline 49/42, and fourth cell 50/43.
The two rank analyses should return tau-b 0.8 and 1.0 respectively, with
intervals [0.6, 0.8] and [0.8, 1.0]. Bootstrap computation may take minutes.
`paper/evidence-audit.json` records the additional exact paired-test check.

For implementation tests, install pytest and run `python -m pytest`.
The public-report wording/PDF tests are excluded because that identified report
is not part of this anonymous package. All other tests and required scripts
are included.

## Regeneration and functional evaluation

`protocol/constraints-wsl-cu128.txt` records the primary generation versions;
`protocol/published_targets.json` pins every model revision. Generation needs
a compatible CUDA GPU and the evaluation extras in `pyproject.toml`. Install
PyTorch from the cu128 index before applying the constraints. Retain new runs
under a separate output directory rather than replacing the evidence.

```bash
python scripts/primary_codegen.py --output-root results/replication
python scripts/prompt_newline_ablation.py --help
python scripts/starcoder2_stop_ablation.py --help
```

The diagnostic runners' help lists the output path, model key, and stop-list
switches. Metadata beside each retained condition records the applied settings.
The original specification text is in `protocol/PRESPECIFIED_PLAN.md`;
this copy documents the plan but is not an independent timestamp attestation.

For Linux or WSL with Docker, copy sanitized samples into a disposable exchange
directory and run from this archive's root:

```bash
mkdir -p results/recheck
cp artifacts/controls/prompt-newline-ablation/starcoder2-3b-no-trailing-newline-no-new-def-stop.jsonl results/recheck/
bash scripts/evaluate_in_docker.sh results/recheck/starcoder2-3b-no-trailing-newline-no-new-def-stop.jsonl
```

The launcher fetches public data before execution, then runs generated Python
without networking under capability, mount, memory, and process restrictions.
Building the Docker image alone does not apply those runtime restrictions.
Image construction needs internet access; a rebuilt image's digest need not
equal a historical run's recorded digest.

## Provenance, licensing, and anonymity

HumanEval prompts embedded in the retained candidates originate in OpenAI's
HumanEval (MIT; original notice in `licenses/HUMANEVAL-MIT.txt`). EvalPlus is
an external dependency under Apache-2.0 with an additional HumanEval notice
(`licenses/EVALPLUS-APACHE.txt`). Model weights are not distributed here;
their original model repositories govern access and use. Generated completions
are experimental outputs, not a guarantee of correctness, novelty, or fitness
for reuse. The study code's MIT terms are in `LICENSE`; its own author name
is temporarily represented by an anonymous attribution for double-anonymous
review. Original third-party attributions are unchanged.

The archive excludes Git history, cached bytecode, author URLs, and machine
paths. `ANONYMIZATION.json` lists files whose metadata was changed. JSONL
candidate files are preserved byte-for-byte; evaluator solution strings and
outcomes are unchanged. Historical nested manifests are omitted because their
metadata hashes no longer apply; use only the root `SHA256SUMS`. This removes
direct identifiers but cannot prevent matching scientific content to a public
preprint or repository. Supply the ZIP through the submission system, not an
author-owned public URL. There were no human participants or private datasets.

# Primary results

The preregistered five-model primary run completed on 2026-09-14. Each model
generated one greedy completion for all 164 HumanEval tasks in BF16 on an RTX
4070. The same completions were scored against HumanEval and HumanEval+ with
EvalPlus 0.3.1 in a network-isolated container.

| Model | Published HE | Local HE | Published HE+ | Local HE+ |
|---|---:|---:|---:|---:|
| Qwen2.5-Coder-0.5B | 28.0 | 23.8 (39/164) | 23.8 | 20.1 (33/164) |
| StarCoder2-3B | 31.7 | 1.8 (3/164) | 27.4 | 1.8 (3/164) |
| DeepSeek-Coder-1.3B | 34.8 | 34.1 (56/164) | 26.8 | 28.7 (47/164) |
| Qwen2.5-Coder-1.5B | 43.9 | 39.0 (64/164) | 36.6 | 34.1 (56/164) |
| Qwen2.5-Coder-3B | 52.4 | 52.4 (86/164) | 42.7 | 42.7 (70/164) |

## Primary decision

The published HumanEval order was not reproduced. Kendall's tau-b is 0.8, with
a paired task-bootstrap 95% interval of [0.6, 0.8]. The local order from low to
high is StarCoder2-3B, Qwen2.5-Coder-0.5B,
DeepSeek-Coder-1.3B, Qwen2.5-Coder-1.5B, and Qwen2.5-Coder-3B.

StarCoder2-3B reverses its published ordering with Qwen2.5-Coder-0.5B. The local
paired pass@1 difference (StarCoder2 minus Qwen0.5B) is -21.95 percentage
points, with a preregistered paired-bootstrap 95% interval of [-28.66, -15.85].
Because the interval excludes zero in the reversed direction, the primary
decision is **failed to reproduce**.

## Interpretation boundary

This result applies to the uniform local deployment condition in
[`EXPERIMENT_PLAN.md`](EXPERIMENT_PLAN.md). It does not establish that the
published StarCoder2 score is wrong. The Qwen2.5-Coder report identifies the
models and benchmark but does not state every decoding, stopping, and software
detail needed to reconstruct Table 5 from the paper alone.

A direct diagnostic showed that the pinned StarCoder2 checkpoint generates
sensible code for its model-card prompt, but begins HumanEval/0 by repeating the
function definition. EvalPlus treats the exact text `\ndef ` as a generation
boundary, then removes the repeated definition during truncation. The provider
decodes only newly generated tokens; the prompt appears in retained raw JSONL
because EvalPlus deliberately stores `prompt + implementation`.

The EvalPlus leaderboard lists 31.7% HumanEval and 27.4% HumanEval+ for
StarCoder2-3B. That row was added on 2024-02-29, the day after StarCoder2's
release and before EvalPlus code generation supported StarCoder2, with values
identical to Table 9 of the StarCoder2 technical report. The leaderboard,
StarCoder2, and Qwen2.5-Coder values should therefore be treated as one
measurement, not three independent ones.

A post-hoc one-factor ablation removed only `\ndef ` from the stop list. It
produced 17/164 (10.4%) HumanEval and 15/164 (9.1%) HumanEval+ passes: a real
but partial effect.

## Post-hoc diagnosis: trailing prompt newline

EvalPlus 0.3.1 sends `task["prompt"].strip() + "\n"` to base models. The
prompt was stripped upstream on 2024-03-17 in a commit titled "fix: starcoder
l2r inference" (`evalplus/evalplus@3ff1e38`), and a newline was re-appended on
2024-08-03 (`evalplus/evalplus@4df7001`), after the StarCoder2 report. The exact
code that produced the StarCoder2 report's values is not public, so this history
explains the sensitivity rather than reconstructing that run. StarCoder2's tokenizer normally merges
the newline after a closing docstring with the following indentation, so a
prompt ending in a lone `\n` token is off-distribution. At HumanEval/0 the model
then restarts the function at top level, which the `\ndef ` stop truncates to
an empty body.

A second post-hoc ablation kept every stop text and changed only the model input
to omit that trailing newline, for all five checkpoints. Hardened evaluation
(GitHub Actions run 35235307019) produced:

| Model | Published HE / HE+ | Primary HE / HE+ | No trailing newline HE / HE+ |
|---|---:|---:|---:|
| Qwen2.5-Coder-0.5B | 28.0 / 23.8 | 39 / 33 | 22.6 (37) / 18.9 (31) |
| StarCoder2-3B | 31.7 / 27.4 | 3 / 3 | 29.9 (49) / 25.6 (42) |
| DeepSeek-Coder-1.3B | 34.8 / 26.8 | 56 / 47 | 32.9 (54) / 28.0 (46) |
| Qwen2.5-Coder-1.5B | 43.9 / 36.6 | 64 / 56 | 40.9 (67) / 34.1 (56) |
| Qwen2.5-Coder-3B | 52.4 / 42.7 | 86 / 70 | 51.8 (85) / 43.3 (71) |

StarCoder2-3B moves from 2–3 passes to 49/164, within three tasks of its
published HumanEval and HumanEval+ counts. The other checkpoints change by at
most three tasks. Under this condition the published order is recovered exactly:
Kendall's tau-b is 1.0 (paired task-bootstrap 95% interval [0.8, 1.0]), and the
preregistered rule would classify the condition as reproduced. Because the
condition was selected after the primary result, this does not replace the
primary decision; it identifies the documented pipeline change on which that
decision depends. Artifacts are in
[`artifacts/controls/prompt-newline-ablation`](artifacts/controls/prompt-newline-ablation).

## Artifacts and remaining work

[`artifacts/primary`](artifacts/primary) contains raw and sanitized completions,
the five full evaluator result files, 820 task-level outcomes, the analysis JSON,
environment metadata, and checksums. These files include untrusted generated
Python and must not be executed outside a sandbox.

[`artifacts/controls`](artifacts/controls) additionally contains a complete
unmodified-EvalPlus StarCoder2-3B control generation and two-task equivalence
records for all five models. The two-task raw and sanitized outputs are
byte-identical to the retained primary records. Hardened functional scoring of
the full stock control produced 2/164 (1.2%) on both HumanEval and HumanEval+,
with passes on HumanEval/49 and HumanEval/53. The primary wrapper also passed
HumanEval/50, producing 3/164 (1.8%). Thus the unmodified stock harness does not
restore the published score or ordering and does not explain the low primary
result.

The complete stop-rule ablation is retained in
[`artifacts/controls/stop-ablation`](artifacts/controls/stop-ablation), including
raw and sanitized generations, hardened evaluator output, checksums, condition
metadata, and the first 20 stock-path records. Those 20 records are byte-identical
to the faster full-run path and document that decode-once stopping and hook
restoration change execution cost rather than outputs under the altered list.

The prompt-newline ablation directory contains raw and sanitized generations
for all five checkpoints, runner metadata, hardened evaluator outputs, 820
task-level outcomes, the ablation analysis, a summary, and checksums.

The planned 20-sample sensitivity condition and independent review have not yet
been completed. The primary result is complete and auditable; an archival paper
release remains gated as described in
[`PUBLICATION_STATUS.md`](PUBLICATION_STATUS.md).

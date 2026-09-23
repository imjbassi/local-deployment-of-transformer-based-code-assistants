# Primary results

The prespecified five-model primary run completed on 2026-09-14. The endpoint
and decision rule were committed as `1025978` before aggregate inspection. Each model
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

The published HumanEval order did not transfer to the pinned local pipeline.
Kendall's tau-b is 0.8, with a paired task-resampling interval of [0.6, 0.8]. The local order from low to
high is StarCoder2-3B, Qwen2.5-Coder-0.5B,
DeepSeek-Coder-1.3B, Qwen2.5-Coder-1.5B, and Qwen2.5-Coder-3B.

StarCoder2-3B reverses its published ordering with Qwen2.5-Coder-0.5B. The local
paired pass@1 difference (StarCoder2 minus Qwen0.5B) is -21.95 percentage
points, with a prespecified paired task-resampling interval of [-28.66, -15.85].
Because the interval excludes zero in the reversed direction, the primary
decision is **failed to transfer** (the archived JSON retains the historical
machine-readable label `failed_to_reproduce`).

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
prespecified rule would classify the condition as transferred. Because the
condition was selected after the primary result, this does not replace the
primary decision; it identifies the documented pipeline change on which that
decision depends. Artifacts are in
[`artifacts/controls/prompt-newline-ablation`](artifacts/controls/prompt-newline-ablation).

### Completed 2×2 generation diagnostic

A final post-hoc cell omitted both the trailing prompt newline and the exact
`\ndef ` stop for StarCoder2-3B. Generation completed for all 164 tasks with
the pinned checkpoint and settings. Text-only classification of raw suffixes
gives:

| Prompt / stop condition | Empty suffix | Any top-level `def` | Repeated entry-point `def` |
|---|---:|---:|---:|
| Newline / standard stop | 142 | 0 | 0 |
| Newline / no `\ndef ` stop | 2 | 152 | 63 |
| No newline / standard stop | 0 | 0 | 0 |
| No newline / no `\ndef ` stop | 0 | 143 | 38 |

The stop therefore hides a broad multi-definition continuation tendency in
both prompt conditions, while newline removal eliminates the empty retained
suffixes seen in the stock condition. Sanitization narrows the consequence:
151/164 fourth-cell candidates are byte-identical to the hardened-evaluated
no-newline baseline. The 13 changed candidates were all baseline failures, so
static comparison gave pre-evaluation bounds of 49–62 HumanEval and 42–55
HumanEval+ passes. The pinned hardened evaluator scored the fourth cell at
50/164 and 43/164: one fail-to-pass and no pass-to-fail transition on each
suite. Generated Python was not executed on the host.

## Stochastic sensitivity (prespecified secondary condition)

The prespecified 20-sample condition (temperature 0.2, top-p 0.95, seed 11,
BF16, 512 new tokens) is complete for the three planned checkpoints, plus a
post-hoc no-trailing-newline run for StarCoder2-3B. All four runs were
uninterrupted. Hardened evaluation (GitHub Actions run 35411593164) gives:

| Condition | pass@1 (95% CI) | pass@5 (95% CI) | Greedy pass@1 |
|---|---:|---:|---:|
| Qwen2.5-Coder-1.5B | 37.6 [31.2, 44.1] | 50.8 [43.8, 57.8] | 39.0 |
| DeepSeek-Coder-1.3B | 32.2 [25.9, 38.7] | 41.3 [34.2, 48.6] | 34.1 |
| StarCoder2-3B, stock prompt | 2.3 [0.9, 4.2] | 5.6 [2.8, 8.7] | 1.8 |
| StarCoder2-3B, no trailing newline | 29.8 [23.7, 36.2] | 40.4 [33.4, 47.4] | 29.9 |

Intervals are paired task bootstraps over the 164 tasks with 10,000
replicates. HumanEval+ pass@1 follows the same pattern (31.5, 27.8, 2.3, and
26.1 respectively).

Sampling pass@1 is within about two points of greedy pass@1 in every condition.
StarCoder2-3B remains at 2.3% under the stock prompt even with 20 samples per
task, so its primary result is not an artifact of greedy decoding, and the
trailing-newline condition recovers it under sampling as well.

Seeds 23 and 37 were not run. `EXPERIMENT_PLAN.md` triggers them only on a rank
reversal or an adjacent pair below five percentage points; the seed-11 order is
preserved and the closest adjacent pair (Qwen2.5-Coder-1.5B minus
DeepSeek-Coder-1.3B) differs by 5.37 points. That margin is narrow, so the
absence of a trigger should not be read as a wide separation.

DeepSeek-Coder-1.3B generated at batch size 2 rather than 20. Its multi-head
key/value cache for 20 concurrent sequences exhausts the 12 GB GPU, after which
the driver spills into host memory and a single task exceeds 15 minutes. Batch
size changes throughput only; the sample count, temperature, top-p, prompt,
stop texts, and token cap are identical across conditions.

## Prompt and 8-bit ablations (prespecified secondary conditions)

Both remaining prespecified conditions ran on Qwen2.5-Coder-1.5B at seed 11
with the reference sampling settings, changing one factor each. The
chat-prompt condition stops forcing the base prompt, so EvalPlus builds its
instruction-style prompt with its own default prefixes; the int8 condition
loads bitsandbytes 8-bit weights instead of BF16. Hardened evaluation (GitHub
Actions run 35431439493) gives:

| Condition | pass@1 (95% CI) | pass@5 | Paired pass@1 difference |
|---|---:|---:|---:|
| Reference: BF16, base prompt | 37.6 [31.2, 44.1] | 50.8 | — |
| Chat-template prompt | 48.6 [42.4, 55.0] | 66.5 | +11.07 [+4.39, +17.74] |
| 8-bit weights | 24.4 [18.7, 30.4] | 34.4 | -13.17 [-17.90, -8.66] |

Paired differences resample the 164 tasks while keeping each task's two
outcomes together. Both intervals exclude zero. HumanEval+ shows the same
directions: 43.7% for the chat prompt (+12.23 [+5.64, +18.96]) and 23.2% for
8-bit (-8.23 [-12.29, -4.24]).

These are one-model sensitivity checks and do not affect the primary decision.
They do sharpen its interpretation: two ordinary deployment choices move a
single checkpoint by about 11 and 13 points, which is larger than most gaps
between adjacent models in the published table. A score is a property of the
whole evaluation system, not of the checkpoint alone.

No further seeds were triggered. Neither ablation is a multi-model ranking, and
both differ from the reference by more than five percentage points.

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
task-level outcomes, the ablation analysis, and a summary. It also contains the
generated no-newline/no-`\ndef ` StarCoder2 cell, all-task continuation
classification, sanitized-candidate comparison, hardened evaluator output,
workflow provenance, and refreshed checksums.

The 20-sample generations, hardened evaluator outputs, pass@k analysis, summary,
and checksums are in
[`artifacts/controls/sampling-sensitivity`](artifacts/controls/sampling-sensitivity).

The prompt and 8-bit generations, hardened evaluator outputs, paired analysis,
summary, and checksums are in
[`artifacts/controls/qwen-secondary-ablations`](artifacts/controls/qwen-secondary-ablations).

The author confirms that a second person reviewed the work. The returned
sign-off should be retained with the final release materials using
[`paper/INDEPENDENT_REVIEW_PACKET.md`](paper/INDEPENDENT_REVIEW_PACKET.md).
The primary result is complete and auditable; archival status is described in
[`PUBLICATION_STATUS.md`](PUBLICATION_STATUS.md).

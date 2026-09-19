# Publication status

## Current state

The five-model primary experiment and preregistered analysis are complete. The
primary decision is `failed_to_reproduce`; measured values and interpretation
limits are in `RESULTS.md`, with auditable artifacts in `artifacts/primary`.

The repository now includes a versioned technical report of the completed
primary experiment under `paper/`. It is not a completed archival or
peer-reviewed paper. The historical PDF is not evidence for the new study and
the removed self-audit manuscript must not be restored as the contribution.

## Release gate

A paper or archival release requires all of the following:

1. **Complete:** greedy runs for all five primary checkpoints and all 164 tasks.
2. **Complete:** functional evaluation with pinned EvalPlus 0.3.1 inside a
   disposable, network-isolated container.
3. **Complete for the primary run:** model revisions, environment metadata,
   raw/sanitized completions, evaluator outputs, and checksums are checked in.
4. **Complete:** the preregistered rank endpoint, paired uncertainty, and
   three-way decision were generated from task-level artifacts.
5. **Complete:** the planned 20-sample sensitivity condition ran for the three
   named checkpoints at seed 11, and the prompt and 8-bit ablations ran on
   Qwen2.5-Coder-1.5B. No further seeds were triggered: the ordering is
   preserved and the closest adjacent pair differs by 5.37 percentage points.
6. **Open:** obtain a second-person review of protocol-to-artifact mapping and
   the eventual manuscript.
7. **Complete:** release v1.2.0 is archived on Zenodo as
   [10.5281/zenodo.22800651](https://doi.org/10.5281/zenodo.22800651).

## Additional control status

A full 164-task StarCoder2-3B generation through unmodified EvalPlus 0.3.1 is
retained in `artifacts/controls/`. Static comparison finds two sanitized records
that differ from the primary generation. A network-isolated hardened evaluation
on an ephemeral GitHub runner scored the stock control at 2/164 (1.2%) on both
HumanEval and HumanEval+. The primary wrapper scored 3/164 (1.8%), so the stock
control does not restore the published result. The evaluator JSON and image
identifier are retained with the control artifacts.

The two-task unmodified-EvalPlus equivalence check is complete for all five
models. Raw and sanitized records match the retained primary artifacts byte for
byte; hashes and condition metadata are in
`protocol/all_models_stock_equivalence.json`.

A post-hoc StarCoder2-3B ablation removing only the exact `\ndef ` generation
stop is complete. Hardened evaluation scored 17/164 (10.4%) on HumanEval and
15/164 (9.1%) on HumanEval+. A separately retained 20-task stock prefix is
byte-identical to the performance-only generation path. The change explains
only part of the local failure.

A post-hoc five-model ablation that keeps every stop and omits only the
trailing newline EvalPlus 0.3.1 appends to base-model prompts is complete.
Hardened evaluation scored StarCoder2-3B at 49/164 (29.9%) on HumanEval and
42/164 (25.6%) on HumanEval+, within three tasks of its published values; the
other checkpoints moved by at most three tasks, and the published order was
recovered (tau-b = 1.0, 95% interval [0.8, 1.0]). The EvalPlus leaderboard's
StarCoder2 values match the StarCoder2 technical report and are not an
independent measurement.

The preregistered 20-sample condition is complete for Qwen2.5-Coder-1.5B,
DeepSeek-Coder-1.3B, and StarCoder2-3B, with a post-hoc no-trailing-newline run
for StarCoder2-3B. Sampling pass@1 is within about two points of greedy pass@1
in every condition, and StarCoder2-3B stays at 2.3% under the stock prompt, so
its primary result is not a greedy-decoding artifact.

The two remaining preregistered ablations on Qwen2.5-Coder-1.5B are complete.
Against the reference condition, the chat-template prompt adds 11.07 points of
HumanEval pass@1 (paired 95% interval [4.39, 17.74]) and bitsandbytes 8-bit
weights remove 13.17 points ([-17.90, -8.66]). Both are single-checkpoint
sensitivity checks and do not alter the primary decision.

Until the open gates pass, the defensible claim is limited to the completed
primary condition and its stated interpretation boundary; do not describe the
repository as a finished or peer-reviewed paper.

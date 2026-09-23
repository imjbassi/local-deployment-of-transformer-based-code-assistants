# Trailing newline changes StarCoder2-3B HumanEval from 3/164 to 49/164

Filed upstream as <https://github.com/evalplus/evalplus/issues/319>.

We observed a large model-specific effect from the trailing newline added to
stripped HumanEval prompts in the direct-completion path. This report is meant
as an actionable pipeline-sensitivity finding, not a claim that the newline is
universally harmful or that it caused any historical published score.

## Upstream history

- `3ff1e38868abf7dcf1e53e8926bb0188aebcbd8d` (2024-03-17),
  `fix: starcoder l2r inference`, changed the constructed prompt to `.strip()`:
  <https://github.com/evalplus/evalplus/commit/3ff1e38868abf7dcf1e53e8926bb0188aebcbd8d>
- `4df700112e142efdebca6a7e8ce69882951f7532` (2024-08-03),
  `fix: add a newliner after striped prompt`, changed it to
  `task["prompt"].strip() + "\n"`:
  <https://github.com/evalplus/evalplus/commit/4df700112e142efdebca6a7e8ce69882951f7532>

## Reproduction

Checkpoint: `bigcode/starcoder2-3b` at the immutable revision recorded in the
linked artifact. We used greedy BF16 generation, a 512-token cap, all 164
HumanEval tasks, EvalPlus 0.3.1, HumanEval+ dataset v0.1.10, and hardened
network-isolated evaluation. The counterfactual changed only whether the model
input ended with the appended newline; the stored candidate remained
`prompt + completion`. The stop-factor counterfactual changed only the exact
`\ndef ` stop.

Functional results (passes out of 164):

| Prompt boundary | `\ndef ` stop | HumanEval | HumanEval+ |
|---|---:|---:|---:|
| Appended newline | Enabled | 3 | 3 |
| Appended newline | Disabled | 17 | 15 |
| No appended newline | Enabled | 49 | 42 |
| No appended newline | Disabled | 50 | 43 |

Text-only counts in the retained raw suffixes:

| Prompt boundary | `\ndef ` stop | Empty | Any line-start `def` | Repeated entry point |
|---|---:|---:|---:|---:|
| Appended newline | Enabled | 142 | 0 | 0 |
| Appended newline | Disabled | 2 | 152 | 63 |
| No appended newline | Enabled | 0 | 0 | 0 |
| No appended newline | Disabled | 0 | 143 | 38 |

The definition classifier is lexical rather than AST-based, and enabled-stop
counts are post-truncation observations. Removing the newline changed
StarCoder2-3B from 3 to 49 HumanEval passes; removing the interacting stop after
that changed only one additional outcome. In a five-model check, the other four
models moved by at most three net tasks when the newline was removed.

## Suggested action

Please consider making prompt-boundary behavior explicit and configurable for
base-model direct completion, documenting the exact prompt bytes, and adding a
regression test that covers StarCoder2-style continuation at the closing
docstring boundary. Maintainer guidance on whether the appended newline is an
intentional cross-model default would be valuable.

Full task-level generations, evaluator outputs, metadata, checksums, and the
analysis are available here:
<https://github.com/imjbassi/local-deployment-of-transformer-based-code-assistants>

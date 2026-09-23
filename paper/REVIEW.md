# Manuscript review

Review date: 2026-09-22
Scope: internal evidence, LaTeX, citation, and rendering review of version 1.9

The previous review overstated submission readiness: it did not test the
extracted supplement, which omitted controls and the required license file.
Those defects are corrected. See `PUBLICATION_CRITIQUE.md` for the audit.

## Verdict

The manuscript is suitable as a transparent technical report of the completed
primary experiment, post-hoc StarCoder2 diagnostics, five-model prompt-newline
condition, and prespecified secondary conditions. It is framed as a rank-transfer
study rather than an exact historical reproduction. It is not labeled peer
reviewed. An independent second-person review remains the one open publication
gate.

The canonical source is `main.tex`, the bibliography is maintained in
`references.bib`, and the checked-in PDF is compiled from those files with
Tectonic.

## Build and rendering review

- Tectonic 0.17.0 completed the LaTeX and BibTeX passes successfully.
- The final log contains no overfull boxes, unresolved citations, unresolved
  references, or LaTeX errors.
- All eight report pages and four submission-draft pages were rendered with
  Poppler and inspected after the revision.
- Both full-width tables, the vector result figure, headers, footers, hyperlinks,
  column transitions, and the balanced bibliography render without clipping or
  overlap.
- All Latin Modern fonts used by the PDF are embedded and subsetted.

## Claim-to-evidence audit

| Claim | Evidence | Status |
|---|---|---|
| Five models completed 164 tasks | Five 164-line sample files and evaluator outputs | Verified |
| Local HumanEval and HumanEval+ counts | `outcomes.jsonl` and five evaluator result files | Verified |
| Kendall's tau-b is 0.8 with 95% interval [0.6, 0.8] | `primary-analysis.json`, 10,000 paired replicates, seed 2026 | Verified |
| StarCoder2/Qwen0.5 reversal and interval | `primary-analysis.json`, 10,000 paired replicates, seed 2026 | Verified |
| Two-task stock-harness equivalence for all five models | `artifacts/controls` and `protocol/all_models_stock_equivalence.json` | Verified |
| Full stock StarCoder2 control: 2/164 on HE and HE+ | 164 retained records, hardened evaluator JSON, image identifier, and static comparisons | Verified |
| EvalPlus leaderboard StarCoder2 scores: 31.7% HE, 27.4% HE+ | Official leaderboard result data; row added in evalplus.github.io commit `838caf0` on 2024-02-29 | Verified against external source |
| Leaderboard values match StarCoder2 report | StarCoder2 technical report Table 9 (arXiv 2402.19173v1) | Verified against primary source |
| EvalPlus prompt-boundary history | evalplus/evalplus commits `3ff1e38` (2024-03-17) and `4df7001` (2024-08-03) | Verified against upstream repository |
| Prompt-newline ablation: StarCoder2 49/164 HE, 42/164 HE+; tau-b 1.0 [0.8, 1.0] | Five-model generations, hardened run 35235307019, `outcomes.jsonl`, `ablation-analysis.json` | Verified |
| Prompt-newline paired transitions: 46 HE fail-to-pass, 0 pass-to-fail; 40 HE+ fail-to-pass, 1 pass-to-fail | Primary and prompt-newline `outcomes.jsonl`, joined by model and task | Verified |
| 20-sample pass@1 and pass@5 for four conditions | 13,120 completions, hardened run 35411593164, `sampling-analysis.json` | Verified |
| Seeds 23 and 37 untriggered (closest pair 5.37 points) | `summary.json` seed_trigger block, computed from the same analysis | Verified |
| All four sampling runs uninterrupted | Generation logs contain no resume markers | Verified |
| Qwen ablations: 48.6% chat prompt, 24.4% 8-bit pass@1 | 6,560 completions, hardened run 35431439493, `summary.json` | Verified |
| Paired differences $+11.07$ and $-13.17$ exclude zero | `paired_difference_vs_reference` over the same 164 tasks | Verified |
| Each ablation took the intended path | Runners assert chat-template use and 8-bit loading at run time | Verified |
| No-newline-`def` ablation: 17/164 HE, 15/164 HE+ | 164 retained records, hardened evaluator JSON, run 35077128303, and summary JSON | Verified |
| Stock/optimized ablation equivalence | First 20 raw and sanitized records, byte-prefix comparison, and recorded hashes | Verified |
| Fourth factorial cell: 164 retained raw/sanitized records; 143 raw suffixes contain top-level definitions and 38 repeat the entry point | `factorial-continuation-analysis.json`, condition metadata, and checksums | Verified as text-only analysis |
| Fourth-cell hardened score: 50/164 HE and 43/164 HE+ | Evaluator output, image digest, successful workflow run 35492816775, and task-level transitions | Verified |
| Checkpoint identities and revisions | `protocol/published_targets.json` | Verified |
| BF16, RTX 4070, package and evaluator versions | hardware, package-freeze, and evaluator-image artifacts | Verified |
| Published scores | Qwen2.5-Coder technical report, Table 5 | Verified against primary source |
| StarCoder2 diagnostic | Retained completion artifacts and documented direct probe | Bounded, exploratory |

## Language and inference controls

- The title and abstract specify rank transfer to one disclosed pipeline, not an
  exact historical reproduction or general model-quality ranking.
- The result is phrased as failure to transfer under the declared condition;
  the archived JSON retains its historical `failed_to_reproduce` label.
- The manuscript identifies commit `1025978` as the pre-result specification
  and does not claim an independent preregistration record.
- Exact counts accompany rounded percentages.
- Task-bootstrap intervals are described as task-composition stability, not
  uncertainty about the fully enumerated benchmark or generation seeds.
- No latency, throughput, CPU, or cross-hardware result is claimed. Sampling,
  prompt, and quantization results are explicitly scoped to their measured
  checkpoints, conditions, and seeds.
- The newline and stop diagnostics are explicitly post hoc. Newline removal is
  reported as sufficient within the pinned pipeline, not as proof of the
  unpublished historical source configuration.
- The 2×2 generation factorial, hardened evaluation, and all-task
  repeated-definition classification are complete. Pre-truncation logits remain
  an optional deeper mechanism test rather than a missing score.
- The report identifies the 2024 target as historical rather than calling the
  selected models current state of the art.

## Citation review

References distinguish HumanEval, the EvalPlus paper, leaderboard and setup,
Qwen2.5-Coder, StarCoder2, DeepSeek-Coder, BigCodeBench, LiveCodeBench, and
empirical-reproducibility work. All links resolve to primary paper, project,
model-card, or repository pages. External percentages are identified by source
in Table 2.

## Open gates before venue submission

1. Obtain a second-person protocol-to-artifact and manuscript review.
2. Retain pre-truncation logits if the tokenizer-and-stop mechanism is to be
   promoted beyond an explanatory local counterfactual.
3. Author verifies final declarations and the anonymous attribution before
   submitting the completed FORGE draft and supplement. The current report
   revision still needs a matching archival release before final publication.

These items limit a venue-submission claim, but they do not invalidate the
checked-in primary result or this explicitly scoped technical report.

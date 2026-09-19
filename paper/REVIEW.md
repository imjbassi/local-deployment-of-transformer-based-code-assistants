# Manuscript review

Review date: 2026-09-19
Scope: internal evidence, LaTeX, citation, and rendering review of version 1.5

## Verdict

The manuscript is suitable as a transparent technical report of the completed
primary experiment and the post-hoc StarCoder2 stop-rule and five-model
prompt-newline ablations, and all preregistered secondary conditions. It is not
labeled peer reviewed. An independent second-person review remains the one open
publication gate.

The canonical source is `main.tex`, the bibliography is maintained in
`references.bib`, and the checked-in PDF is compiled from those files with
Tectonic.

## Build and rendering review

- Tectonic 0.17.0 completed the LaTeX and BibTeX passes successfully.
- The final log contains no overfull boxes, unresolved citations, unresolved
  references, or LaTeX errors.
- All six PDF pages were rendered with Poppler and inspected at 130 DPI.
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
| 20-sample pass@1 and pass@5 for four conditions | 13,120 completions, hardened run 35411593164, `sampling-analysis.json` | Verified |
| Seeds 23 and 37 untriggered (closest pair 5.37 points) | `summary.json` seed_trigger block, computed from the same analysis | Verified |
| All four sampling runs uninterrupted | Generation logs contain no resume markers | Verified |
| Qwen ablations: 48.6% chat prompt, 24.4% 8-bit pass@1 | 6,560 completions, hardened run 35431439493, `summary.json` | Verified |
| Paired differences $+11.07$ and $-13.17$ exclude zero | `paired_difference_vs_reference` over the same 164 tasks | Verified |
| Each ablation took the intended path | Runners assert chat-template use and 8-bit loading at run time | Verified |
| No-newline-`def` ablation: 17/164 HE, 15/164 HE+ | 164 retained records, hardened evaluator JSON, run 35077128303, and summary JSON | Verified |
| Stock/optimized ablation equivalence | First 20 raw and sanitized records, byte-prefix comparison, and recorded hashes | Verified |
| Checkpoint identities and revisions | `protocol/published_targets.json` | Verified |
| BF16, RTX 4070, package and evaluator versions | hardware, package-freeze, and evaluator-image artifacts | Verified |
| Published scores | Qwen2.5-Coder technical report, Table 5 | Verified against primary source |
| StarCoder2 diagnostic | Retained completion artifacts and documented direct probe | Bounded, exploratory |

## Language and inference controls

- The title and abstract specify a local deployment reproduction, not a general
  model-quality ranking.
- The result is phrased as failure to reproduce under the declared condition;
  it is not framed as proof that a published score is false.
- Exact counts accompany rounded percentages.
- The task bootstrap is not described as generation-seed uncertainty.
- No latency, throughput, CPU, pass@5, quantization, or preregistered
  secondary-condition result is claimed.
- Both ablations are explicitly post hoc. The prompt-newline result is reported
  as identifying the condition on which the primary decision depends; it does
  not replace that decision, and the report states that the code behind the
  published values is not public.
- The report identifies the 2024 target as historical rather than calling the
  selected models current state of the art.

## Citation review

References distinguish HumanEval, the EvalPlus paper, leaderboard and setup,
Qwen2.5-Coder, StarCoder2, and DeepSeek-Coder. All links resolve to official
paper, project, model-card, or repository pages. External percentages are
identified by source in Table 2.

## Open gates before venue submission

1. Obtain a second-person protocol-to-artifact and manuscript review.
2. Select a venue and adapt length, anonymization, formatting, and disclosure
   statements to its current author instructions.

These items limit a venue-submission claim, but they do not invalidate the
checked-in primary result or this explicitly scoped technical report.

# Manuscript review

Review date: 2026-09-16
Scope: internal evidence, LaTeX, citation, and rendering review of version 1.2

## Verdict

The manuscript is suitable as a transparent technical report of the completed
primary experiment and the post-hoc StarCoder2 stop-rule ablation. It is not
labeled peer reviewed or presented as a completed archival study. The planned
stochastic sensitivity condition, exact independent-pipeline reconstruction,
and an independent second-person review remain open publication gates.

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
| Independent EvalPlus StarCoder2 scores: 31.7% HE, 27.4% HE+ | Official leaderboard page and machine-readable result data, accessed 2026-09-16 | Verified against external source |
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
- No latency, throughput, CPU, pass@5, quantization, or secondary-condition
  result is claimed.
- The StarCoder2 ablation is explicitly post hoc; the exact stop effect is
  measured, while the residual independent-score gap is labeled unresolved.
- The report identifies the 2024 target as historical rather than calling the
  selected models current state of the art.

## Citation review

References distinguish HumanEval, the EvalPlus paper, leaderboard and setup,
Qwen2.5-Coder, StarCoder2, and DeepSeek-Coder. All links resolve to official
paper, project, model-card, or repository pages. External percentages are
identified by source in Table 2.

## Open gates before venue submission

1. Run the predeclared 20-sample sensitivity condition and any triggered seeds.
2. Reconstruct the independent EvalPlus StarCoder2 pipeline closely enough to
   locate the remaining 21.3-point HumanEval and 18.3-point HumanEval+ gaps.
3. Obtain a second-person protocol-to-artifact and manuscript review.
4. Deposit a versioned artifact bundle and report at a persistent identifier.
5. Select a venue and adapt length, anonymization, formatting, and disclosure
   statements to its current author instructions.

These items limit a venue-submission claim, but they do not invalidate the
checked-in primary result or this explicitly scoped technical report.

# Publication-readiness audit - 2026-09-22

## Verdict

The result supports a focused benchmarking/audit submission. The previous
package was not ready: its artifact was incomplete and insufficiently tested,
and several claims exceeded their verification. This revision corrects those
issues without changing the primary endpoint or regenerating model outputs.
Acceptance remains a reviewer judgment about novelty and significance.

## Findings and implemented changes

1. **Reproducibility blocker.** The anonymous ZIP omitted stock and stop-ablation
   evidence, generation scripts, protocol metadata, and LICENSE despite claiming
   a complete replication artifact. The old builder also selected compiled
   caches and retained obsolete nested checksums. Replaced it with an explicit
   text-file selection, included every retained control and all generation
   runners, preserved raw JSONL bytes and evaluator solution strings, added
   licenses and protocol text, and regenerated a single root manifest.
2. **Anonymity blocker.** Regex scanning of selected text files did not cover
   cached bytecode and escaped Windows paths. The new archive excludes binary
   caches, parses JSON metadata before redaction, scans every archive member,
   and records transformations. Scientific content is publicly searchable, so
   this is direct-identifier removal, not a guarantee of anonymity.
3. **Condition-description error.** The venue draft attributed the 143-definition
   count to the absence of interventions; it actually belongs to removal of
   both newline and stop. Corrected the condition, distinguished the primary
   3-pass cell from the separate 2-pass stock-provider control, and labeled
   table units explicitly.
4. **Mechanism overstatement.** The classifier uses line-start regular
   expressions, not an AST. Both versions now explain possible multiline-string
   matches and that standard-stop zeros are post-truncation observations.
   The canonical report no longer claims batching affects throughput only.
5. **Statistical and robustness presentation.** Added all five prompt-ablation
   counts, offsetting transitions, the existing 20-sample sensitivity results,
   prespecification limits, and related-work positioning to the short paper.
   An additional exact McNemar/Bonferroni sensitivity check finds the reversal
   remains supported (37 versus 1 discordant tasks; adjusted p about 1.14e-9).
   It is explicitly post hoc and does not replace the original bootstrap rule.
6. **Readiness and provenance overstatement.** Corrected stale status text,
   removed an unsupported claim of completed human verification from the AI
   disclosure, and distinguished the old v1.3.0 DOI from the current manuscript.

## Verification

- Recounted all primary greedy and factorial evaluator files; reconciled all
  820 primary model/task records. Headline scores are unchanged.
- Recomputed primary and no-newline rank analyses from a fresh extraction:
  tau-b 0.8 [0.6, 0.8] and 1.0 [0.8, 1.0].
- Built the anonymous package wheel from its extracted sources; all 31 included
  implementation tests passed. The repository's 39 tests also passed.
- Rebuilt the eight-page report and the IEEE draft (three main-text pages plus
  one references page); inspected the rendered pages.
- No generated Python was executed during this review. Functional scores rely
  on the previously retained hardened evaluator runs.

## Remaining decisions and limits

- **Independent review:** issue #1 has no independent reviewer response as of
  this audit. This is the project's chosen quality gate, not a stated FORGE
  requirement. This assistant's checks do not satisfy it.
- **Author submission checks:** approve the final text, AI disclosure,
  temporary anonymous attribution, conflicts and other submission declarations.
  Submit the paper and ZIP through the venue system. Nothing has been submitted.
- **Archival release:** archive the final accepted/reviewed revision with its
  matching artifacts; do not cite the earlier DOI as containing this revision.
- **Scientific scope:** five historical base models, one GPU/software stack,
  one benchmark, and post-hoc diagnostics limit generality. New benchmarks,
  more seeds, or a token/logit study could strengthen a broader paper, but are
  not needed for the currently bounded local pipeline claim. No novelty or
  acceptance guarantee follows from the large effect size.

Venue requirements checked against the official call:
https://conf.researchr.org/track/forge-2027/forge-2027-data-and-benchmarking-track

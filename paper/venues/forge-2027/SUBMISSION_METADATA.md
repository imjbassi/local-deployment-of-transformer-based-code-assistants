# FORGE 2027 submission metadata worksheet

Prepared for the FORGE 2027 Data and Benchmarking Track. This file is a
pre-submission worksheet, not evidence that a submission was made. Recheck the
official call and the HotCRP form immediately before upload.

## Paper fields

- **Track:** Data and Benchmarking Track — Benchmarking Paper
- **Title:** One Byte, One Rank Reversal: Auditing HumanEval Pipeline
  Sensitivity for Base Code Models
- **Keywords:** benchmark audit; HumanEval; code generation; reproducibility;
  local inference; prompt sensitivity
- **Paper:** `output/forge-2027-anonymous-draft.pdf`
- **Supplement:** `output/forge-2027-anonymous-artifact.zip`

### Abstract

Published benchmark tables are often reused as though model rankings were
properties of checkpoints alone. We test whether the HumanEval order of five
open base-model identifiers in the Qwen2.5-Coder report transfers to one fully
disclosed local pipeline. Each frozen checkpoint produced one greedy completion
for all 164 tasks in BF16 on a consumer GPU; EvalPlus 0.3.1 scored HumanEval and
HumanEval+ in a network-isolated container. The published order failed to
transfer: StarCoder2-3B scored 3/164 rather than the displayed 31.7%, reversing
its order with Qwen2.5-Coder-0.5B. Kendall's tau-b was 0.8 and the paired
StarCoder2-minus-Qwen difference was -21.95 percentage points (task-resampling
interval [-28.66, -15.85]). A stock EvalPlus control scored 2/164. In a post-hoc
counterfactual, deleting only the trailing newline appended to stripped
base-model prompts raised StarCoder2 to 49/164 and restored the five-model
order. A completed 2x2 newline-by-stop factorial scored its fourth cell at
50/164. The result shows that an apparently innocuous prompt byte can change a
base-model score by about 28 points and reverse a portable-looking rank.

## Contribution and artifact statements

- **Contribution:** a prespecified five-model rank-transfer audit, complete
  task-level evidence for the primary condition, and a post-hoc mechanism audit
  isolating a one-byte prompt boundary and its interaction with a stop rule.
- **Artifact availability during review:** upload the history-free anonymous
  ZIP through HotCRP. Do not use the author-owned repository or DOI as the
  anonymous artifact link.
- **Artifact contents:** immutable model revisions, protocol and environment
  metadata, retained raw and sanitized generations, hardened evaluator outputs,
  task-level analyses, checksums, source code, licenses, and reproduction
  instructions.
- **Ethics/data:** no human participants, personal data, or private datasets.
  Generated code is untrusted and must be evaluated only in the documented
  isolated container.
- **AI-use disclosure:** a generative AI assistant assisted with drafting,
  editing, code, and artifact checks. Automated checks reconcile reported
  counts with retained evaluator outputs. The author remains responsible for
  the content, citations, and final submission.
- **Licensing/provenance:** repository software is MIT-licensed; bundled or
  derived material retains its recorded upstream licensing and provenance in
  the supplement. The public v1.3.0 archive does not contain manuscript v1.9.

## Author decisions required before submission

These fields must be completed by the human author in the submission system;
they are deliberately not inferred here.

- [ ] Confirm the complete author list, order, affiliations, and contact author.
- [ ] Enter every author's conflicts of interest under the venue's current rule.
- [ ] Confirm originality and compliance with the simultaneous-submission rule.
- [ ] Disclose the public repository, technical report, and any preprint where
  the form or policy requires it; confirm that double-anonymous review remains
  permissible given the already-public material.
- [ ] Confirm every citation, license, model/dataset term, and AI-use statement.
- [ ] Confirm that the anonymous PDF and supplement contain no direct identity
  markers and accept the residual deanonymization risk from public prior work.
- [ ] Recheck the four-main-page plus one-reference-page limit and the official
  deadline (currently recorded as 15 November 2026, Anywhere on Earth).
- [ ] Designate the presenter/registrant and approve the final uploaded files.

No box above should be checked solely on the basis of an automated review.

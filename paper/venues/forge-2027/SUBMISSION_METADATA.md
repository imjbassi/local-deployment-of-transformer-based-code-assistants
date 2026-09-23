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

A trailing newline appended to stripped HumanEval prompts changed
StarCoder2-3B from 3/164 to 49/164 passes in our pinned EvalPlus 0.3.1 pipeline
and reversed a five-model ranking. We found this one-byte effect in a post-hoc
mechanism audit following a prespecified rank-transfer study; it establishes
sufficiency in this pipeline, not the unpublished historical configuration.
Each frozen checkpoint produced one greedy completion for all 164 tasks in BF16
on a consumer GPU, and a network-isolated container scored HumanEval and
HumanEval+. Under the stock boundary, StarCoder2 scored 3/164 rather than the
displayed 31.7%, reversing order with Qwen2.5-Coder-0.5B. Kendall's tau-b was
0.8 and the paired difference was -21.95 percentage points
([-28.66, -15.85]). Removing only the newline restored the displayed order;
the other four models moved by at most three tasks. A completed 2x2
newline-by-stop factorial scored its fourth cell at 50/164, showing that exact
prompt boundaries are part of a reproducible benchmark specification.

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
  the supplement. The matching public v1.9.0 archive is assigned version DOI
  <https://doi.org/10.5281/zenodo.22922348>.
- **Public repository/report disclosure:** confirmed. Disclose the public
  repository at
  <https://github.com/imjbassi/local-deployment-of-transformer-based-code-assistants>
  and the Zenodo concept DOI <https://doi.org/10.5281/zenodo.22800650> wherever
  the venue's policy or submission form requests prior/public versions.
- **Presenter and registrant:** Jaiveer Bassi.

## Author decisions required before submission

These fields must be completed by the human author in the submission system;
they are deliberately not inferred here.

- [x] Complete author list: Jaiveer Bassi, Independent Researcher, USA;
  corresponding author at `jaiveerbassi@yahoo.com`.
- [ ] Enter every author's conflicts of interest under the venue's current rule.
- [ ] Confirm originality and compliance with the simultaneous-submission rule.
- [x] Disclose the public repository and report where the form or policy
  requires it; the repository and concept DOI are named above.
- [ ] Confirm every citation, license, model/dataset term, and AI-use statement.
- [x] Confirm that the anonymous PDF and supplement contain no direct identity
  markers and accept the residual deanonymization risk from the disclosed
  public repository and report.
- [ ] Recheck the four-main-page plus one-reference-page limit and the official
  deadline (currently recorded as 15 November 2026, Anywhere on Earth).
- [x] Designate Jaiveer Bassi as presenter/registrant.
- [ ] Approve the final uploaded files.

No box above should be checked solely on the basis of an automated review.

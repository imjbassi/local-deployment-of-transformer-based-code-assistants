# FORGE 2027 Data and Benchmarking Track adaptation

Target: FORGE 2027 Data and Benchmarking Track.

Rationale: the track explicitly solicits benchmark audits, evaluation
methodologies, replications/reproductions, contradictory findings, reproducible
benchmarking infrastructure, and code-generation evidence. This paper's central
contribution is a benchmark-pipeline sensitivity audit, so this track is a more
direct fit than a general empirical software-engineering venue.

Official instructions:
<https://conf.researchr.org/track/forge-2027/forge-2027-data-and-benchmarking-track>

## Submission constraints (checked 2026-09-20)

- Deadline: 15 November 2026, Anywhere on Earth.
- Format: `IEEEtran`, `10pt,conference`, without `compsoc` or `compsocconf`.
- Limit: four main-text pages plus one references page.
- Review: double-anonymous.
- Submission system: <https://forge2027-benchmarking.hotcrp.com/>.
- Artifacts are encouraged and must also be anonymized for review.

## Adaptation decisions

- Working anonymous title: *One Byte, One Rank Reversal: Auditing HumanEval
  Pipeline Sensitivity for Base Code Models*. It differs from the public report
  title to reduce trivial deanonymization.
- Preserve the primary rank-transfer result and the completed 2x2
  newline-by-stop factorial; move extended sampling, quantization, and task-level
  tables to the anonymous supplement.
- Remove author names, affiliations, acknowledgments, DOI links, repository
  ownership, commit URLs tied to an account, and identifying artifact metadata.
- Refer to the public technical report and repository in the third person only
  if required for scholarly completeness; do not expose identity through URLs.
- Supply a history-free anonymous artifact archive. Exclude `.git`, absolute
  paths, user names, credentials, and model-generated code that is not needed for
  the claims retained in the four-page paper.
- Include this neutral disclosure without identifying the author: “A generative
  AI assistant was used to draft and edit text and code; the author verified all
  claims, citations, computations, and artifacts.”

## Release checklist

- [x] Condense the manuscript within the four-main-page plus one-reference-page
  maximum (the current draft uses two main pages and one reference page).
- [x] Build with the exact IEEE conference class and inspect every rendered page.
- [x] Run an anonymity search over PDF text, metadata, sources, and supplement.
- [x] Build and checksum a history-free anonymous artifact archive.
- [ ] Obtain the independent review in `paper/INDEPENDENT_REVIEW_PACKET.md`.
- [ ] Recheck the official instructions immediately before submission.

This directory records a selected venue and a concrete formatting/anonymization
specification. The canonical eight-page technical report remains the complete
archival version; it should not be uploaded as the double-anonymous submission.

The current draft is `output/forge-2027-anonymous-draft.pdf`, and the companion
archive is `output/forge-2027-anonymous-artifact.zip`. Build the paper from this
directory with:

```powershell
tectonic -X compile main.tex --outdir build --keep-logs
Copy-Item build/main.pdf output/forge-2027-anonymous-draft.pdf -Force
```

Build the artifact archive from the repository root with:

```powershell
.\paper\venues\forge-2027\build_anonymous_artifact.ps1
```

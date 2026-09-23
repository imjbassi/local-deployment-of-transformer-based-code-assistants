# Paper source and build

The checked-in PDF reports the completed five-model primary experiment, stock
control, post-hoc StarCoder2 diagnostics, five-model prompt-newline condition,
and completed sampling, prompt, and quantization sensitivity conditions. It is
a technical report, not a peer-reviewed publication. Manuscript version 1.9
is archived with its matching software and evidence as release v1.9.0 under
DOI `10.5281/zenodo.22926448`. It adds publication-review fixes, a multiplicity
sensitivity analysis, clearer classifier and batching limitations, and a
repaired review supplement. The completed fourth cell remains 50/164 HumanEval
and 43/164 HumanEval+.

## Contents

- `main.tex`: canonical LaTeX manuscript.
- `references.bib`: BibTeX bibliography.
- `build.ps1` and `build.sh`: reproducible Tectonic build entry points.
- `REVIEW.md`: claim-to-evidence and presentation review.
- `output/pdf/Do_Published_HumanEval_Rankings_Survive_Local_Deployment.pdf`:
  PDF compiled from `main.tex`.

## Build

Install [Tectonic](https://tectonic-typesetting.github.io/) and run from the
repository root:

```powershell
.\paper\build.ps1
```

On Linux or macOS:

```bash
./paper/build.sh
```

For visual review, render every page with Poppler:

```bash
mkdir -p tmp/pdfs
pdftoppm -png \
  paper/output/pdf/Do_Published_HumanEval_Rankings_Survive_Local_Deployment.pdf \
  tmp/pdfs/paper
```

The LaTeX source contains no derived benchmark logic. Values in the manuscript
must remain traceable to `artifacts/primary/primary-analysis.json`,
`artifacts/primary/outcomes.jsonl`,
`artifacts/controls/stop-ablation/summary.json`,
`artifacts/controls/prompt-newline-ablation/factorial-continuation-analysis.json`,
or a cited source.

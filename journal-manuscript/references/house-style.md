# Official IEEE Baseline Contract

Use this reference when the task needs the default IEEE manuscript contract beyond the short workflow in `SKILL.md`. This file describes the official IEEE journal-family LaTeX baseline centered on `IEEEtran`, aligned with the IEEE Author Center guidance that sends authors to the IEEE Template Selector (`https://template-selector.ieee.org/`) for Word or LaTeX article templates. The `paper/` paths below refer to the manuscript repository where the skill is being applied; they are not bundled inside this skill package itself.

## Expected Manuscript Paths

- `paper/main.tex`: primary manuscript and layout source of truth
- `paper/references.bib`: BibTeX database
- `paper/CAPTION_BANK.md`: caption wording reference
- `paper/tables/*.tex`: hand-maintained table templates
- `paper/tables/generated/*.tex`: generated table wrappers and active outputs
- `paper/README_PAPER.md`: paper directory notes and compile guidance
- `paper/_reference_pages/ref-page-3.png`, `ref-page-5.png`, `ref-page-6.png`: visual references for dense IEEE journal pages

If the active manuscript uses another root directory, resolve the equivalent files first and keep the same roles.

## Baseline Layout

The default IEEE paper is expected to follow the official IEEE journal-family LaTeX path:

- `\documentclass[journal]{IEEEtran}`
- `newtxtext,newtxmath` for text and math
- compact academic packages including `microtype`, `amsmath`, `bm`, `graphicx`, `booktabs`, `multirow`, `tabularx`, `cite`, `algorithm`, `algpseudocode`, `tikz`, and `hyperref`
- IEEE front matter with `\title`, `\author`, `\thanks`, `\markboth`, `\maketitle`, `abstract`, and `IEEEkeywords`

Current customizations worth preserving:

- `\algrenewcommand\algorithmicrequire{\textbf{Input:}}`
- `\algrenewcommand\algorithmicensure{\textbf{Output:}}`
- custom `Y` and `C` column types
- tightened float spacing:
  - `\textfloatsep = 7pt plus 1pt minus 2pt`
  - `\floatsep = 6pt plus 1pt minus 2pt`
  - `\intextsep = 6pt plus 1pt minus 2pt`
  - `\dbltextfloatsep = 7pt plus 1pt minus 2pt`
  - `\abovecaptionskip = 3pt plus 1pt minus 1pt`
  - `\belowcaptionskip = 0pt`

Do not replace these defaults casually with manual spacing patches unless the target journal truly requires different behavior.

## Section Scaffold

Default top-level section order for the local IEEE baseline:

1. `Introduction`
2. `Related Work`
3. `Methodology`
4. `Experiments`
5. `Conclusion and Discussion`
6. `References`

Preferred subsection map:

- `Related Work`
- `Methodology`
- `Experiments`

Treat this six-part flow as the default manuscript skeleton for this library, not as a universal IEEE law. Some IEEE journals merge `Related Work` into `Introduction`, rename `Experiments`, or split `Discussion` from `Conclusion`. When the target venue says otherwise, the venue wins.

## Writing And Caption Style

Observed baseline voice:

- formal, technical, and paper-centered
- claims are tied to mechanism, design choice, or evaluation
- notation is explained immediately after equations
- contributions are listed with an `enumerate` block in the introduction
- captions are compact, factual, and descriptive rather than promotional

Caption drafting rules:

- state what is shown
- state what varies across panels, rows, or conditions when relevant
- mention key metrics or symbols when needed
- avoid marketing language and unnecessary storytelling

## Figure Patterns

Expected figure behavior in `paper/main.tex`:

- the framework overview uses `figure*` across both columns
- most other figures use `\begin{figure}[!t]`
- some figures use `\IfFileExists{...}` so external PNG assets can override LaTeX fallbacks
- widths are chosen conservatively, such as `0.72\linewidth` or `0.97\textwidth`

If adding a figure:

1. Decide whether it truly needs full-width placement.
2. Reuse the existing `paper/figures/figN/` structure when possible.
3. Keep caption, label, and placement consistent with the manuscript.

## Table Patterns

Representative template behavior:

- `paper/tables/simulation_results_template.tex`
  - `\scriptsize`
  - `\setlength{\tabcolsep}{4pt}`
  - `booktabs`
  - metric headers with arrows such as `SR $\uparrow$`
- `paper/tables/scenario_suite_template.tex`
  - `\small`
  - `tabularx` with custom `Y` columns
  - compact row spacing via `\renewcommand{\arraystretch}{0.98}`
- `paper/tables/ablation_template.tex`
  - dense packed columns for ablation summaries
  - custom `m{}` columns and selective row shading

Generated table routing already used by the paper:

- comparison: `paper/tables/generated/publication_from_runs_comparison.tex`
- ablation: `paper/tables/generated/publication_from_runs_ablation.tex`
- scenario density: `paper/tables/generated/publication_from_runs_scenario_density.tex`

Do not delete wrapper or placeholder logic unless the user explicitly wants the manuscript simplified.

## Bibliography And Compile Flow

Bibliography footer:

- `\bibliographystyle{IEEEtran}`
- `\bibliography{references}`

Compile from `paper/`:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

If citations, labels, or references change, expect the full four-step compile cycle.

## Practical Editing Heuristics

- Start from local manuscript patterns before introducing new macros or environments.
- Keep edits narrow when only one section or one float is changing.
- If float placement needs adjustment, change the float first before touching global spacing.
- If the user wants a new paper based on the existing one, clone the structure and preamble from `paper/main.tex` rather than starting from a stock sample.
- If the user wants another journal style, keep this IEEE reference as the baseline and layer only the target journal's verified differences on top.

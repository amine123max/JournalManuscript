---
name: journal-manuscript
description: Use when the user wants to draft, expand, revise, or reformat a journal manuscript while preserving the established layout, section hierarchy, caption voice, figure and table conventions, citation style, and compile workflow of the target paper. This skill defaults to the official IEEE journal-family LaTeX baseline (`IEEEtran`) in the consuming workspace, but it can also absorb additional journal template requirements when the user is working against another journal class or submission guide.
---

# Journal Manuscript

## Overview

This skill keeps manuscript work aligned with the active journal template instead of drifting toward a generic LaTeX style. Its default baseline is the official IEEE journal-family LaTeX path centered on `IEEEtran` in the consuming workspace, and it can be extended with additional journal-specific rules for other publishers or submission templates.

## When To Use

Use this skill for requests such as:

- "Add a new subsection in the same journal manuscript style as the current paper"
- "Integrate updated experiment results into the manuscript without breaking the layout"
- "Rewrite this passage so it matches the tone and structure of `paper/main.tex`"
- "Add a figure, table, or algorithm while preserving journal float and caption conventions"
- "Adapt this manuscript from the current IEEE version to another journal template"
- "Start a new manuscript version based on this paper rather than a blank template"
- "Create a new IEEE, Elsevier, Springer, Frontiers, PLOS, Wiley, ACS, or AIP family manuscript scaffold in `paper/`"

Do not use this skill for simulation code, model training, or experiment automation unless the task directly changes the manuscript or paper-side assets.

## Working Method

1. If the user wants a new family-level manuscript scaffold, or `paper/main.tex` does not yet exist, initialize the workspace with `scripts/scaffold_family_manuscript.py --family <family-slug> --output-dir <workspace-root>` before drafting.
2. Open `paper/main.tex` in the active manuscript workspace first and treat it as the source of truth for style and structure.
3. If the workspace does not literally use `paper/`, resolve the equivalent manuscript-side files first and keep the same functional roles.
4. If the task touches citations, captions, figures, or tables, read only the relevant companion files under the manuscript root, especially `references.bib`, `CAPTION_BANK.md`, `tables/`, and `figures/`.
5. Determine the target journal profile before editing:
   - If the user is continuing the current paper and it is IEEE-based, or the venue is still undecided, use the official IEEE baseline documented in `references/house-style.md` together with the verified IEEE family profile under `references/journals/ieee/`.
   - If the user names another journal or template, inspect that class file, author guide, or manuscript source first and extract its concrete rules.
6. Preserve the current preamble, class, spacing, and float behavior unless the user explicitly requests a layout redesign.
7. Before replacing result tables, verify whether the manuscript already routes them through generated wrappers or placeholders.

## Editing Rules

- Keep the manuscript aligned with the target journal class and preserve the current package stack unless a new feature truly requires a new package.
- Match the existing voice: formal, precise, and mechanism-oriented. Prefer paper-centered phrasing such as "This paper..." or module-centered explanations.
- Keep the current section logic intact unless the user explicitly asks for restructuring.
- Use the citation and cross-reference conventions of the active journal template consistently.
- When introducing equations, define symbols immediately after the display.
- Prefer minimal, source-aware edits over manual spacing hacks. Avoid ad hoc `\vspace` unless there is no cleaner option and the result has been checked.
- Reuse existing figure, table, and caption patterns before introducing new formatting ideas.
- When adapting to a new journal, capture the differences explicitly: class file, front matter, abstract and keyword style, heading hierarchy, bibliography style, figure and table caption placement, and submission-specific metadata.

## Figures, Tables, And Algorithms

- For the default IEEE official baseline, prefer the float behavior already present in the active `paper/main.tex`: `[!t]` for standard single-column floats and `figure*` for true full-width overview figures.
- If a figure already uses `\IfFileExists{...}` with a LaTeX fallback, preserve that behavior.
- For result tables, prefer the generated files under `paper/tables/generated/` and keep wrapper or placeholder logic intact.
- For hand-authored tables, reuse the table templates in `paper/tables/` when working on the current IEEE paper, and derive new journal-specific table rules from the active template when the target journal differs.
- If the user adds pseudocode, remain compatible with the current `algorithm` and `algpseudocode` stack, including `Input:` and `Output:` labels.

## Validation

- After layout-sensitive edits, compile with the manuscript's actual toolchain. For the default IEEE official baseline, run `pdflatex main.tex`, `bibtex main`, `pdflatex main.tex`, and `pdflatex main.tex` from `paper/`.
- If float placement or references behave unexpectedly, compare against the current PDF and the page snapshots under `paper/_reference_pages/`.

## Reference Files

Open [references/house-style.md](references/house-style.md) for the default IEEE official baseline contract used by the skill. When the target is IEEE, also open [references/journals/ieee/profile.md](references/journals/ieee/profile.md) and `references/journals/ieee/verification.yaml` before relying on family-level defaults. Open [references/journal-profiles.md](references/journal-profiles.md) for the per-journal folder model, then use [references/journals/catalog.md](references/journals/catalog.md) to locate the relevant family or journal profile under `references/journals/<name>/profile.md`. When deciding whether a family baseline is suitable for scaffold generation, consult `references/journals/family-template-sharing-tiers.md`.

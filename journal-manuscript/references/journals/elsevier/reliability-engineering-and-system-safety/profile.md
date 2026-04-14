# Reliability Engineering and System Safety Profile

Use this profile when the target manuscript is intended for Reliability Engineering and System Safety.

## Official Basis

- Elsevier family baseline from Elsevier LaTeX author instructions
- Official Reliability Engineering and System Safety Guide for Authors

## Parent Template Family

- Parent family: Elsevier Family
- Start from: ../elsevier/profile.md

## Official Template Display

- Elsevier LaTeX instructions: `elsarticle.zip`
- Official guide page: https://www.sciencedirect.com/journal/reliability-engineering-and-system-safety/publish/guide-for-authors
- Downloaded guide file: `assets/official-templates/guides/reliability-engineering-and-system-safety/official-guide-source.html`
- Imported local package: `assets/official-templates/elsevier/elsarticle/elsarticle/`
- Selected display baseline: `elsarticle-template-num.tex`
- Guide alignment: Use the imported numeric Elsevier sample until the live guide indicates a different citation mode or journal-specific manuscript variant.

## Refined Format Notes

- Base class: `elsarticle` unless the journal guide says otherwise
- Expected authoring layout: single-column Elsevier manuscript with `frontmatter`
- Citation mode: verify from the current journal guide
- Front matter focus: reliability problem setting, model or algorithm, evaluation protocol, and risk or safety implications
- Publisher extras: declarations, data or code statements, and supplementary analysis appendices should be checked before submission

## Journal-Specific Emphasis

- Reliability analysis, safety engineering, risk modeling, maintenance optimization, and dependable intelligent systems

## Local Preview Tuning

- Inherit the Elsevier single-column preview baseline
- Keep the first page analytical and table-driven rather than visually decorative
- Leave room for declarations and reliability terminology

## Verification Status

- Official Elsevier template assets are imported locally, and the displayed manuscript uses the selected `elsarticle` sample shown above.
- Use `verification.yaml` together with the live Guide for Authors before calling the layout submission-ready.

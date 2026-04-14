# Aerospace Science and Technology Profile

Use this profile when the target manuscript is intended for Aerospace Science and Technology.

## Official Basis

- Elsevier family baseline from Elsevier LaTeX author instructions
- Official Aerospace Science and Technology Guide for Authors

## Parent Template Family

- Parent family: Elsevier Family
- Start from: ../elsevier/profile.md

## Official Template Display

- Elsevier LaTeX instructions: `elsarticle.zip`
- Official guide page: https://www.sciencedirect.com/journal/aerospace-science-and-technology/publish/guide-for-authors
- Imported local package: `assets/official-templates/elsevier/elsarticle/elsarticle/`
- Selected display baseline: `elsarticle-template-num.tex`
- Guide alignment: Use the imported numeric Elsevier sample until the live guide indicates a different citation mode or journal-specific manuscript variant.

## Refined Format Notes

- Base class: `elsarticle` unless the journal guide provides a different package
- Expected authoring layout: single-column Elsevier manuscript with `frontmatter`
- Citation mode: verify from the current guide because aerospace titles may vary
- Front matter focus: problem statement, aerospace platform or scenario, method, and validation evidence
- Figure and table handling: trajectory plots, block diagrams, and benchmark tables should be clear and uncluttered

## Journal-Specific Emphasis

- Aerospace systems, guidance, navigation, control, aerodynamics, and autonomous flight technologies

## Local Preview Tuning

- Inherit the Elsevier single-column preview baseline
- Favor system block diagrams and quantitative comparison tables
- Keep the first page technical and application-oriented

## Verification Status

- Official Elsevier template assets are imported locally, and the displayed manuscript uses the selected `elsarticle` sample shown above.
- Use `verification.yaml` together with the live Guide for Authors before calling the layout submission-ready.


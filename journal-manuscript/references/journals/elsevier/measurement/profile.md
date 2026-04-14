# Measurement Profile

Use this profile when the target manuscript is intended for Measurement.

## Official Basis

- Elsevier family baseline from Elsevier LaTeX author instructions
- Official Measurement Guide for Authors

## Parent Template Family

- Parent family: Elsevier Family
- Start from: ../elsevier/profile.md

## Official Template Display

- Elsevier LaTeX instructions: `elsarticle.zip`
- Official guide page: https://www.sciencedirect.com/journal/measurement/publish/guide-for-authors
- Downloaded guide file: `assets/official-templates/guides/measurement/official-guide-source.html`
- Imported local package: `assets/official-templates/elsevier/elsarticle/elsarticle/`
- Selected display baseline: `elsarticle-template-num.tex`
- Guide alignment: The Measurement guide points authors back to the Guide for Authors when no journal-specific template is available and illustrates numbered square-bracket citations.

## Refined Format Notes

- Base class: `elsarticle` unless the current guide says otherwise
- Expected authoring layout: single-column Elsevier manuscript with `frontmatter`
- Front matter focus: title, authors, affiliations, abstract, and keyword block
- Journal-guide signals to watch: article highlights and graphical abstract handling, plus measurement-focused figure clarity
- Citation mode: verify from the current guide because Elsevier titles can differ

## Journal-Specific Emphasis

- Measurement systems, instrumentation, calibration, uncertainty analysis, sensing workflows, and metrology applications

## Local Preview Tuning

- Inherit the Elsevier single-column preview baseline
- Keep a measurement-style figure placeholder and a compact metric table
- Preserve declaration space and frontmatter rhythm

## Verification Status

- Official Elsevier template assets are imported locally, and the displayed manuscript uses the selected `elsarticle` sample shown above.
- Use `verification.yaml` together with the live Guide for Authors before calling the layout submission-ready.

# Applied Soft Computing Profile

Use this profile when the target manuscript is intended for Applied Soft Computing.

## Official Basis

- Elsevier family baseline from Elsevier LaTeX author instructions
- Official Applied Soft Computing Guide for Authors

## Parent Template Family

- Parent family: Elsevier Family
- Start from: ../elsevier/profile.md

## Official Template Display

- Elsevier LaTeX instructions: `elsarticle.zip`
- Official guide page: https://www.sciencedirect.com/journal/applied-soft-computing/publish/guide-for-authors
- Imported local package: `assets/official-templates/elsevier/elsarticle/elsarticle/`
- Selected display baseline: `elsarticle-template-num.tex`
- Guide alignment: The Applied Soft Computing guide uses numbered square-bracket citations, so the numeric Elsevier sample is the closest imported official match.

## Refined Format Notes

- Base class: `elsarticle` unless the journal package says otherwise
- Expected authoring layout: single-column Elsevier manuscript with `frontmatter`
- Citation mode: verify from the live journal guide; Elsevier journals may be numeric or author-year
- Front matter focus: article title, authors, affiliations, abstract, and a short keyword list
- Publisher extras: declaration sections, supplementary files, and any optional highlight material should be checked before final submission

## Journal-Specific Emphasis

- Soft computing, intelligent systems, fuzzy systems, swarm methods, optimization, and applied AI

## Local Preview Tuning

- Inherit the Elsevier single-column preview baseline
- Keep a clear frontmatter feel and leave room for declaration sections
- Favor one method figure and one benchmark table on the first page

## Verification Status

- Official Elsevier template assets are imported locally, and the displayed manuscript uses the selected `elsarticle` sample shown above.
- Use `verification.yaml` together with the live Guide for Authors before calling the layout submission-ready.


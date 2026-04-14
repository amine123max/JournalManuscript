# Robotics Profile

Use this profile when the target manuscript is intended for Robotics.

## Official Basis

- MDPI family baseline from MDPI author instructions
- Official Robotics Instructions for Authors

## Parent Template Family

- Parent family: MDPI Family
- Start from: ../mdpi/profile.md

## Official Guide Display

- Official guide page: https://www.mdpi.com/journal/robotics/instructions
- Downloaded guide file: `assets/official-templates/guides/robotics/official-guide-source.pdf`
- Guide note: the Robotics instructions page is access-controlled in this environment, so the downloaded file is the official MDPI author layout style guide recorded in `verification.yaml`

## Refined Format Notes

- Base template anchor: MDPI journal manuscript package
- Expected authoring layout: single-column open-access manuscript with article-type metadata and declaration-rich end matter
- Front matter focus: article type, title, authors, affiliations, abstract, keywords, and corresponding-author metadata
- Common mandatory end sections: author contributions, funding, data availability, acknowledgments, and conflicts of interest
- Figures and tables: robotics pipeline figures, benchmark tables, and ablation or hardware summary tables should remain clear and explicit

## Journal-Specific Emphasis

- Robotics systems, manipulation, navigation, field robotics, multi-agent robotics, and embodied intelligence

## Local Preview Tuning

- Inherit the MDPI single-column preview baseline
- Keep declaration-heavy end matter visible
- Favor one robotics figure and one benchmark table on the first page

## Verification Status

- MDPI family conventions are available as a publisher baseline, but the journal-specific Robotics template path is still blocked locally.
- Do not label this journal official-template verified until the official MDPI template asset is added and `verification.yaml` no longer reports `blocked`.


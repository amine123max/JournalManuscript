# Elsevier Family Profile

Use this profile when the target manuscript follows the Elsevier Family template family.

## Official Basis

## Official Guide Display

- Official guide page: Custom journal placeholder
- Downloaded guide file: `assets/official-templates/guides/elsevier/official-guide-source.txt`
- Guide note: no official guide exists for the custom-journal placeholder
- Guide alignment: use this local guide file as the nearest official reference before calling the layout submission-ready

- Elsevier LaTeX author instructions and `elsarticle` guidance
- Official Guide for Authors page for the specific journal
- Imported official Elsevier template assets under `assets/official-templates/elsevier/`

## Refined Format Baseline

- Primary LaTeX anchor: `elsarticle` unless the journal provides a different package
- Imported package baseline: `elsarticle.zip` for standard journals and `els-cas-templates.zip` for CAS-family journals
- Typical authoring layout: single-column manuscript with `frontmatter`
- Front matter: title, authors, affiliations, abstract, keywords, and journal-dependent metadata
- Common publisher items: declarations, highlights, graphical abstract, supplementary files, and data statements
- References: numeric or author-year depending on the target journal's Guide for Authors
- Figures and tables: usually author-manuscript single-column placement, with publisher conversion at production time

## Check Before Editing

1. Exact class file and option set
2. Front matter structure
3. Abstract and keyword requirements
4. Figure and table placement rules
5. Citation and bibliography mode
6. Required end sections and declarations
7. Compile toolchain

## Safe Rule

Treat this file as a verified family baseline. For each concrete Elsevier journal, check which imported template sample best matches the guide for authors, then confirm whether citations are numeric or author-year and whether highlights, a graphical abstract, or declaration sections are required rather than optional.

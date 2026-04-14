# IEEE Family Profile

Use this profile when the target manuscript follows the IEEE Family template family.

## Official Basis

- IEEE Author Center journal article authoring tools and templates
- Official IEEE journal information-for-authors pages for the target venue

## Official Guide Display

- Official guide page: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/
- Official template download: https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip
- Downloaded guide file: `assets/official-templates/guides/ieee/official-guide-source.html`
- Local cached template package: `assets/official-templates/ieee/template-package/`
- Template basis: imported official IEEEtran package recorded in `verification.yaml`
- Local template package root: `assets/official-templates/ieee/template-package/`
- Primary sample manuscript: `assets/official-templates/ieee/template-package/bare_jrnl.tex`
- Guide alignment: use this local guide file together with the live author page before calling the layout submission-ready


## Refined Format Baseline

- Primary LaTeX anchor: `IEEEtran`
- Default article skeleton in this library: `Introduction`, `Related Work`, `Methodology`, `Experiments`, `Conclusion and Discussion`, and `References`
- Typical final layout: compact engineering journal presentation, commonly in two columns
- Front matter: title, author block, abstract, and `Index Terms` or journal-specific keyword section
- References: numeric IEEE citation style and IEEE bibliography conventions
- Figures and tables: compact floats, engineering captions, and restrained use of full-width material
- Common special items: multimedia, graphical abstract, data or code notes, and author biographies only when the specific journal requires them

## Check Before Editing

1. Exact class file and option set
2. Front matter structure
3. Abstract and keyword requirements
4. Figure and table placement rules
5. Citation and bibliography mode
6. Required end sections and declarations
7. Compile toolchain and whether the imported `bare_jrnl.tex` flow needs journal-specific section renaming or merging

## Safe Rule

Treat this file as a verified family baseline. For any specific IEEE journal, keep the IEEEtran structure and then tighten only the journal-specific differences such as page limits, article type, biography handling, supplementary-material rules, or section-name adjustments.

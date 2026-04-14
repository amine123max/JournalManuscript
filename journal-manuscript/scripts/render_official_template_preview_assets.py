#!/usr/bin/env python3
"""Render official preview assets and verification records.

This script targets the curated journal set that either has a local official
template path available or an explicit blocked reason recorded in the
verification metadata.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNALS_DIR = ROOT / "references" / "journals"
DEFAULT_OFFICIAL_TEMPLATE_DIR = ROOT / "assets" / "official-templates"
ELSEVIER_LATEX_SOURCE = "https://www.elsevier.com/en-gb/researcher/author/policies-and-guidelines/latex-instructions"
ELSEVIER_ELSARTICLE_PACKAGE_URL = "https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip"
ELSEVIER_CAS_PACKAGE_URL = "https://assets.ctfassets.net/o78em1y1w4i4/5uFmLZJTPDMAUjFnHRpjj8/6f19a979146eb93263763d87a894ab0d/els-cas-templates.zip"
ACM_LATEX_SOURCE = "https://authors.acm.org/proceedings/production-information/preparing-your-article-with-latex"
SPRINGER_LATEX_SOURCE = "https://www.springernature.com/gp/authors/campaigns/latex-author-support"
SPRINGER_TEMPLATE_PACKAGE_URL = "https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12"
WILEY_LATEX_SOURCE = "https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html"
WILEY_TEMPLATE_PACKAGE_URL = "https://authors.wiley.com/asset/WileyDesign.zip"
COPERNICUS_LATEX_SOURCE = "https://publications.copernicus.org/for_authors/manuscript_preparation.html"
COPERNICUS_TEMPLATE_PACKAGE_URL = "https://publications.copernicus.org/Copernicus_LaTeX_Package.zip"
SIAM_LATEX_SOURCE = "https://www.siam.org/publications/journals/authors/"
SIAM_TEMPLATE_PACKAGE_URL = "https://tug.ctan.org/macros/latex/contrib/siam/siamltex.zip"
IOP_LATEX_SOURCE = "https://publishingsupport.iopscience.iop.org/questions/latex-template/"
IOP_TEMPLATE_PACKAGE_URL = "https://publishingsupport.iopscience.iop.org/wp-content/uploads/2025/07/ioplatextemplate.zip"


def resolve_journal_dir(root: Path, slug: str) -> Path:
    direct = root / slug
    if direct.is_dir():
        return direct
    matches = [path.parent for path in root.rglob("profile.md") if path.parent.name == slug]
    if not matches:
        raise FileNotFoundError(f"Unknown journal or family slug: {slug}")
    if len(matches) > 1:
        raise RuntimeError(f"Slug is ambiguous: {slug}")
    return matches[0]


COMMON_IEEE_SOURCE = "https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/"
IEEE_TEMPLATE_PACKAGE_URL = "https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip"
IEEE_TEMPLATE_LOCAL_ROOT = "assets/official-templates/ieee/template-package"
IEEE_TEMPLATE_SAMPLE = "bare_jrnl.tex"
COMMON_IEEE_NOTES = [
    "Verified against the imported IEEEtran template package stored in the local assets folder.",
    "The rendered preview is derived from the official bare_jrnl.tex journal sample and keeps a six-part default article skeleton: Introduction, Related Work, Methodology, Experiments, Conclusion and Discussion, and References.",
    "Journal-specific layout compliance still requires the structured checklist in layout-checklist.md and the target venue author page.",
]
COMMON_IEEE_CHECKS = [
    {
        "id": "class-file-and-option-set",
        "title": "Exact class file and option set",
        "requirement": "Verify the actual class file, template package, or sample source used by the journal.",
    },
    {
        "id": "front-matter-structure",
        "title": "Front matter structure",
        "requirement": "Confirm abstract and Index Terms format, author metadata, first-footnote content, and any journal-specific front-matter blocks.",
    },
    {
        "id": "body-structure-and-sections",
        "title": "Body structure and section flow",
        "requirement": "Confirm the article body follows the target journal's required section hierarchy, including whether Related Work and Discussion should be merged or separated.",
    },
    {
        "id": "figure-table-and-graphics-rules",
        "title": "Figure, table, and graphics rules",
        "requirement": "Confirm caption placement, one-column versus two-column sizing, accepted graphics formats, and supplementary-material handling.",
    },
    {
        "id": "references-and-end-matter",
        "title": "References and end matter",
        "requirement": "Confirm IEEE reference styling, acknowledgments, appendices, and whether author biographies are required for the target journal.",
    },
]

COMMON_ELSEVIER_CHECKS = [
    {
        "id": "class-file-and-template-variant",
        "title": "Class file and template variant",
        "requirement": "Confirm the journal follows the imported official Elsevier elsarticle package and that the selected sample manuscript variant matches the guide for authors.",
    },
    {
        "id": "frontmatter-and-keywords",
        "title": "Frontmatter and keywords",
        "requirement": "Confirm title page, author affiliations, abstract, keyword count, and any journal-specific metadata required by the guide for authors.",
    },
    {
        "id": "reference-style-alignment",
        "title": "Reference style alignment",
        "requirement": "Confirm whether the journal guide expects numeric or author-year citations and keep the selected Elsevier template variant consistent with that guidance.",
    },
    {
        "id": "highlights-and-declarations",
        "title": "Highlights and declarations",
        "requirement": "Confirm whether highlights, graphical abstract, declaration sections, data statements, or biographies are required, optional, or disallowed.",
    },
    {
        "id": "figure-table-and-submission-assets",
        "title": "Figure, table, and submission assets",
        "requirement": "Confirm artwork format, table handling, supplementary files, and any guide-specific upload constraints for source submission.",
    },
]

COMMON_ACM_CHECKS = [
    {
        "id": "class-file-and-submission-mode",
        "title": "Class file and submission mode",
        "requirement": "Confirm the manuscript uses the official ACM acmart class and the review-oriented submission mode required by ACM.",
    },
    {
        "id": "frontmatter-and-acm-metadata",
        "title": "Front matter and ACM metadata",
        "requirement": "Confirm title, abstract, CCS concepts, keywords, authors, affiliations, and ACM-specific metadata match the official authoring guidance.",
    },
    {
        "id": "section-flow-and-length",
        "title": "Section flow and manuscript length",
        "requirement": "Confirm the section hierarchy and overall manuscript length match the target ACM journal's expectations.",
    },
    {
        "id": "figure-table-and-accessibility-rules",
        "title": "Figure, table, and accessibility rules",
        "requirement": "Confirm figure and table treatment, caption style, and accessibility requirements such as figure descriptions follow ACM guidance.",
    },
    {
        "id": "references-and-bibliography-mode",
        "title": "References and bibliography mode",
        "requirement": "Confirm the citation and bibliography mode matches the official ACM journal workflow and the target venue requirements.",
    },
]

COMMON_ACS_CHECKS = [
    {
        "id": "class-file-and-submission-mode",
        "title": "Class file and submission mode",
        "requirement": "Confirm the manuscript uses the official ACS achemso class and the correct submission mode for the target journal.",
    },
    {
        "id": "frontmatter-and-chemistry-metadata",
        "title": "Front matter and chemistry metadata",
        "requirement": "Confirm title, author affiliations, abstract, graphical elements, and any chemistry-specific metadata follow the ACS authoring guidance.",
    },
    {
        "id": "section-flow-and-article-type",
        "title": "Section flow and article type",
        "requirement": "Confirm the manuscript section hierarchy and article type match the target ACS journal expectations.",
    },
    {
        "id": "graphics-and-supporting-information",
        "title": "Graphics and supporting information",
        "requirement": "Confirm figure handling, TOC graphics, and supporting information preparation follow ACS guidance.",
    },
    {
        "id": "bibliography-and-chemistry-style",
        "title": "Bibliography and chemistry style",
        "requirement": "Confirm the bibliography workflow and chemistry style conventions remain consistent with the ACS authoring guidance.",
    },
]

COMMON_AIP_CHECKS = [
    {
        "id": "class-file-and-journal-option",
        "title": "Class file and journal option",
        "requirement": "Confirm the manuscript uses the official REVTeX class with the correct AIP journal option and review format.",
    },
    {
        "id": "frontmatter-and-author-block",
        "title": "Front matter and author block",
        "requirement": "Confirm title, authors, affiliations, abstract, and any AIP-specific metadata follow the official author instructions.",
    },
    {
        "id": "section-flow-and-letter-constraints",
        "title": "Section flow and letter constraints",
        "requirement": "Confirm the article structure and any letter-format constraints match the target AIP journal guidance.",
    },
    {
        "id": "figure-table-and-data-availability",
        "title": "Figure, table, and data availability rules",
        "requirement": "Confirm artwork preparation, table style, and data availability statements follow AIP guidance.",
    },
    {
        "id": "references-and-revtex-style",
        "title": "References and REVTeX style",
        "requirement": "Confirm the reference style and REVTeX bibliography handling remain consistent with AIP instructions.",
    },
]

COMMON_SPRINGER_CHECKS = [
    {
        "id": "class-file-and-style-option",
        "title": "Class file and style option",
        "requirement": "Confirm the manuscript uses the imported official sn-jnl package with the style option most consistent with the target family or journal guidance.",
    },
    {
        "id": "frontmatter-and-journal-metadata",
        "title": "Front matter and journal metadata",
        "requirement": "Confirm title, authors, affiliations, abstract, keywords, and any journal-specific metadata follow the Springer Nature author guidance.",
    },
    {
        "id": "section-flow-and-family-rules",
        "title": "Section flow and family rules",
        "requirement": "Confirm the article structure and any family-specific reporting expectations match the target journal guidance.",
    },
    {
        "id": "figure-table-and-supplementary-rules",
        "title": "Figure, table, and supplementary rules",
        "requirement": "Confirm artwork, table treatment, and supplementary file handling remain consistent with the official Springer Nature guidance.",
    },
    {
        "id": "references-and-bibliography-style",
        "title": "References and bibliography style",
        "requirement": "Confirm the selected bibliography style option matches the target family or journal guidance.",
    },
]

COMMON_WILEY_CHECKS = [
    {
        "id": "class-file-and-template-mode",
        "title": "Class file and template mode",
        "requirement": "Confirm the manuscript uses the imported official Wiley USG class and the selected template mode consistent with the Wiley PDF design package.",
    },
    {
        "id": "frontmatter-and-wiley-metadata",
        "title": "Front matter and Wiley metadata",
        "requirement": "Confirm title, authors, correspondence, abstract, keywords, and publisher metadata follow the Wiley authoring guidance.",
    },
    {
        "id": "section-flow-and-journal-rules",
        "title": "Section flow and journal rules",
        "requirement": "Confirm the manuscript section hierarchy and journal-level expectations match the target Wiley guide.",
    },
    {
        "id": "figure-table-and-graphics-rules",
        "title": "Figure, table, and graphics rules",
        "requirement": "Confirm figure handling, table style, and graphics preparation remain consistent with the Wiley authoring package and the target journal guidance.",
    },
    {
        "id": "references-and-bibliography-style",
        "title": "References and bibliography style",
        "requirement": "Confirm the selected Wiley bibliography mode matches the target journal guidance.",
    },
]

COMMON_COPERNICUS_CHECKS = [
    {
        "id": "class-file-and-journal-abbreviation",
        "title": "Class file and journal abbreviation",
        "requirement": "Confirm the manuscript uses the official Copernicus class and the correct journal abbreviation for the target title.",
    },
    {
        "id": "frontmatter-and-geoscience-metadata",
        "title": "Front matter and geoscience metadata",
        "requirement": "Confirm title, authors, affiliations, abstract, running title, and discussion-paper metadata follow the target Copernicus journal guidance.",
    },
    {
        "id": "section-flow-and-open-review-rules",
        "title": "Section flow and open-review rules",
        "requirement": "Confirm the manuscript structure, appendix handling, and any open-review or discussion-paper workflow requirements match the target journal.",
    },
    {
        "id": "figure-table-and-declaration-rules",
        "title": "Figure, table, and declaration rules",
        "requirement": "Confirm artwork, table treatment, author contributions, competing interests, and acknowledgments follow the target journal guidance.",
    },
    {
        "id": "references-and-bibliography-style",
        "title": "References and bibliography style",
        "requirement": "Confirm whether the target journal expects BibTeX with the Copernicus style or manual bibliography handling.",
    },
]

COMMON_SIAM_CHECKS = [
    {
        "id": "class-file-and-title-scope",
        "title": "Class file and title scope",
        "requirement": "Confirm the manuscript uses the SIAM package and that the target title still accepts the family baseline.",
    },
    {
        "id": "frontmatter-and-math-metadata",
        "title": "Front matter and math metadata",
        "requirement": "Confirm title, authors, affiliations, abstract, keywords, AMS subject classifications, and running heads follow the target SIAM title guidance.",
    },
    {
        "id": "section-flow-and-theorem-rules",
        "title": "Section flow and theorem rules",
        "requirement": "Confirm theorem environments, section hierarchy, and appendix handling match the target SIAM journal expectations.",
    },
    {
        "id": "figure-table-and-proof-style",
        "title": "Figure, table, and proof style",
        "requirement": "Confirm table treatment, figure captions, proof formatting, and equation presentation follow the target SIAM style.",
    },
    {
        "id": "references-and-bibliography-style",
        "title": "References and bibliography style",
        "requirement": "Confirm the target SIAM journal still uses the family bibliography workflow represented by the local package.",
    },
]

COMMON_IOP_CHECKS = [
    {
        "id": "class-file-and-submission-path",
        "title": "Class file and submission path",
        "requirement": "Confirm the target IOP title accepts the family template path and whether the manuscript should be submitted in the template class or as a generic LaTeX source.",
    },
    {
        "id": "frontmatter-and-article-type",
        "title": "Front matter and article type",
        "requirement": "Confirm article type, authors, affiliations, correspondence, abstract, and keywords follow the target IOP journal guidance.",
    },
    {
        "id": "section-flow-and-end-section-rules",
        "title": "Section flow and end section rules",
        "requirement": "Confirm section hierarchy, acknowledgments, funding, author roles, data statements, and supplementary data sections match the target title.",
    },
    {
        "id": "figure-table-and-accessibility-rules",
        "title": "Figure, table, and accessibility rules",
        "requirement": "Confirm artwork handling, caption expectations, and accessibility recommendations follow the current IOP guidance.",
    },
    {
        "id": "references-and-bibliography-style",
        "title": "References and bibliography style",
        "requirement": "Confirm the target IOP journal's bibliography workflow and reference formatting expectations.",
    },
]


def ieee_target(display_name: str, journal_specific_note: str, *, source: str = COMMON_IEEE_SOURCE) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_IEEE_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "IEEEtran official template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "ieee",
        "display_name": display_name,
        "notes": list(COMMON_IEEE_NOTES),
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official IEEEtran template package imported and rendered locally; target-journal author-page rules still require manual confirmation.",
        },
        "official_template_import": {
            "source_page": COMMON_IEEE_SOURCE,
            "package_url": IEEE_TEMPLATE_PACKAGE_URL,
            "local_package_root": IEEE_TEMPLATE_LOCAL_ROOT,
            "selected_template": IEEE_TEMPLATE_SAMPLE,
        },
        "verification_checks": checks,
    }


def elsevier_target(
    display_name: str,
    guide_url: str,
    selected_template: str,
    reference_mode: str,
    journal_specific_note: str,
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_ELSEVIER_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "Elsevier elsarticle official template package",
        "verification_scope": "official-template-package",
        "source": guide_url,
        "compile_mode": "elsevier",
        "display_name": display_name,
        "notes": [
            "Verified against the official Elsevier LaTeX instructions page and the imported elsarticle package stored in the local assets folder.",
            f"Selected manuscript baseline: {selected_template}.",
            f"Guide-for-authors citation mode used for display: {reference_mode}.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official Elsevier template package imported and rendered locally; journal-specific submission rules still require confirmation against the live guide for authors.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": ELSEVIER_LATEX_SOURCE,
            "package_url": ELSEVIER_ELSARTICLE_PACKAGE_URL,
            "additional_package_url": ELSEVIER_CAS_PACKAGE_URL,
            "local_package_root": "assets/official-templates/elsevier/template-package",
            "selected_template": f"elsarticle/elsarticle/{selected_template}",
            "reference_mode": reference_mode,
        },
        "selected_template": selected_template,
        "reference_mode": reference_mode,
    }


def acm_target(
    display_name: str,
    journal_code: str,
    journal_specific_note: str,
    *,
    source: str = ACM_LATEX_SOURCE,
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_ACM_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "ACM acmart official template",
        "verification_scope": "official-family-template",
        "source": source,
        "compile_mode": "acm",
        "display_name": display_name,
        "notes": [
            "Verified against the official ACM LaTeX authoring guidance and the local acmart class available in the TeX installation.",
            "The rendered preview uses manuscript mode so the review-oriented ACM article skeleton is easier to inspect.",
            f"Selected ACM journal code for display: {journal_code}.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official ACM authoring workflow verified at the template level; target-journal submission expectations still require confirmation against the live ACM guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": ACM_LATEX_SOURCE,
            "package_url": "https://mirrors.ctan.org/macros/latex/contrib/acmart.zip",
            "local_package_root": "assets/official-templates/acm/template-package",
            "local_class": "acmart.cls",
            "submission_mode": "manuscript",
            "journal_code": journal_code,
            "selected_template": "acmart.cls",
        },
        "journal_code": journal_code,
    }


def acs_target(
    display_name: str,
    journal_specific_note: str,
    *,
    source: str = "https://pubs.acs.org/page/4authors/submission/tex.html",
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_ACS_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "ACS achemso official template",
        "verification_scope": "official-family-template",
        "source": source,
        "compile_mode": "acs",
        "display_name": display_name,
        "notes": [
            "Verified against the official ACS LaTeX authoring guidance and the local achemso class available in the TeX installation.",
            "The rendered preview uses the ACS manuscript article mode so section flow and chemistry-oriented front matter are easier to inspect.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official ACS authoring workflow verified at the family-template level; target-journal submission expectations still require confirmation against the live ACS guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": source,
            "package_url": "https://mirrors.ctan.org/macros/latex/contrib/achemso.zip",
            "local_package_root": "assets/official-templates/acs/template-package",
            "local_class": "achemso.cls",
            "submission_mode": "manuscript=article",
            "selected_template": "achemso.cls",
        },
    }


def aip_target(
    display_name: str,
    journal_option: str,
    journal_specific_note: str,
    *,
    source: str = "https://publishing.aip.org/resources/researchers/author-instructions/",
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_AIP_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "AIP REVTeX official template",
        "verification_scope": "official-family-template",
        "source": source,
        "compile_mode": "aip",
        "display_name": display_name,
        "notes": [
            "Verified against the official AIP author instructions and the local REVTeX class available in the TeX installation.",
            f"Selected REVTeX journal option for display: {journal_option}.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official AIP authoring workflow verified at the family-template level; target-journal submission expectations still require confirmation against the live AIP guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": source,
            "package_url": "https://mirrors.ctan.org/macros/latex/contrib/revtex.zip",
            "local_package_root": "assets/official-templates/aip/template-package",
            "local_class": "revtex4-2.cls",
            "journal_option": journal_option,
            "submission_mode": "reprint",
            "selected_template": "revtex/revtex4-2.cls",
        },
        "journal_option": journal_option,
    }


def springer_target(
    display_name: str,
    style_option: str,
    journal_specific_note: str,
    *,
    source: str = SPRINGER_LATEX_SOURCE,
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_SPRINGER_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "Springer Nature sn-jnl official template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "springer",
        "display_name": display_name,
        "notes": [
            "Verified against the official Springer Nature LaTeX author support page and the imported sn-article template package stored in the local assets folder.",
            f"Selected sn-jnl style option for display: {style_option}.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official Springer Nature template package imported and rendered locally; target-journal submission expectations still require confirmation against the live journal guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": SPRINGER_LATEX_SOURCE,
            "package_url": SPRINGER_TEMPLATE_PACKAGE_URL,
            "local_package_root": "assets/official-templates/springer/template-package",
            "selected_template": "sn-article-template/sn-article.tex",
            "class_file": "sn-jnl.cls",
            "style_option": style_option,
        },
        "style_option": style_option,
    }


def wiley_target(
    display_name: str,
    style_option: str,
    journal_specific_note: str,
    *,
    source: str = WILEY_LATEX_SOURCE,
) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_WILEY_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "Wiley PDF design official template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "wiley",
        "display_name": display_name,
        "notes": [
            "Verified against the official Wiley PDF design LaTeX authoring template package imported into the local assets folder.",
            f"Selected Wiley style option for display: {style_option}.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official Wiley template package imported and rendered locally; target-journal submission expectations still require confirmation against the live Wiley guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": WILEY_LATEX_SOURCE,
            "package_url": WILEY_TEMPLATE_PACKAGE_URL,
            "local_package_root": "assets/official-templates/wiley/template-package",
            "selected_template": "Optimal-Design-layout/Optimal-Design-layout.tex",
            "class_file": "USG.cls",
            "style_option": style_option,
        },
        "style_option": style_option,
    }


def copernicus_target(display_name: str, journal_specific_note: str, *, source: str = COPERNICUS_LATEX_SOURCE) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_COPERNICUS_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "Copernicus official LaTeX template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "copernicus",
        "display_name": display_name,
        "notes": [
            "Verified against the official Copernicus LaTeX package stored in the local assets folder.",
            "The family-level preview is rendered from the local Copernicus package rather than a generic starter profile.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official Copernicus template package is available locally, but target-journal article metadata, discussion-paper workflow, and bibliography rules still require confirmation against the live journal guidance.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": source,
            "package_url": COPERNICUS_TEMPLATE_PACKAGE_URL,
            "local_package_root": "assets/official-templates/copernicus/template-package",
            "selected_template": "template.tex",
            "class_file": "copernicus.cls",
        },
    }


def siam_target(display_name: str, journal_specific_note: str, *, source: str = SIAM_LATEX_SOURCE) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_SIAM_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "SIAM official LaTeX template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "siam",
        "display_name": display_name,
        "notes": [
            "Verified against the official SIAM package stored in the local assets folder.",
            "The family-level preview is rendered from the local SIAM package rather than a generic starter profile.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official SIAM package is available locally, but title-specific theorem policy, front matter, and bibliography expectations still require confirmation against the live author instructions.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": source,
            "package_url": SIAM_TEMPLATE_PACKAGE_URL,
            "local_package_root": "assets/official-templates/siam/template-package",
            "selected_template": "lexample.tex",
            "class_file": "siamltex.cls",
        },
    }


def iop_target(display_name: str, journal_specific_note: str, *, source: str = IOP_LATEX_SOURCE) -> dict[str, object]:
    checks = [dict(item) for item in COMMON_IOP_CHECKS]
    checks.append(
        {
            "id": "journal-specific-note",
            "title": "Journal-specific note",
            "requirement": journal_specific_note,
        }
    )
    return {
        "status": "verified",
        "template_family": "IOP official journal article template package",
        "verification_scope": "official-template-package",
        "source": source,
        "compile_mode": "iop",
        "display_name": display_name,
        "notes": [
            "Verified against the official IOP journal article template package stored in the local assets folder.",
            "The family-level preview is rendered from the local IOP package rather than a generic starter profile.",
        ],
        "supporting_files": {
            "journal_profile": "./profile.md",
            "layout_checklist": "./layout-checklist.md",
        },
        "journal_specific_validation": {
            "status": "checklist-required",
            "checklist_path": "./layout-checklist.md",
            "boundary": "Official IOP package is available locally, but some IOP titles do not require submission in that exact class format, so target-journal guidance still overrides the family baseline.",
        },
        "verification_checks": checks,
        "official_template_import": {
            "source_page": source,
            "package_url": IOP_TEMPLATE_PACKAGE_URL,
            "local_package_root": "assets/official-templates/iop/template-package",
            "selected_template": "iopjournal-template.tex",
            "class_file": "iopjournal.cls",
        },
    }


TARGETS = {
    "wiley": wiley_target(
        "Wiley Family",
        "MPS",
        "Use this family baseline only when the exact Wiley target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live Wiley guidance.",
    ),
    "copernicus": copernicus_target(
        "Copernicus Family",
        "Use this family baseline only when the exact Copernicus target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live guidance.",
    ),
    "siam": siam_target(
        "SIAM Family",
        "Use this family baseline only when the exact SIAM target journal has not yet been fixed; once the venue is known, tighten the manuscript against that title's live guidance.",
    ),
    "iop": iop_target(
        "IOP Family",
        "Use this family baseline only when the exact IOP target journal has not yet been fixed; once the venue is known, tighten the manuscript against that title's live guidance.",
    ),
    "journal-of-field-robotics": wiley_target(
        "Journal of Field Robotics",
        "MPS",
        "Verify title page structure, appendix handling, and reference style before calling the layout submission-ready.",
    ),
    "international-journal-of-robust-and-nonlinear-control": wiley_target(
        "International Journal of Robust and Nonlinear Control",
        "MPS",
        "Verify theorem environments, bibliography mode, and author note structure before calling the layout submission-ready.",
    ),
    "springer": springer_target(
        "Springer Family",
        "sn-mathphys-num",
        "Use this family baseline only when the exact Springer journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live guidance.",
    ),
    "autonomous-robots": springer_target(
        "Autonomous Robots",
        "sn-mathphys-num",
        "Verify robotics-focused figure density, supplementary material handling, and journal-specific metadata before calling the layout submission-ready.",
    ),
    "journal-of-intelligent-and-robotic-systems": springer_target(
        "Journal of Intelligent and Robotic Systems",
        "sn-mathphys-num",
        "Verify robotics-specific figure density, system-diagram handling, and any live journal metadata before calling the layout submission-ready.",
    ),
    "journal-of-marine-science-and-technology": springer_target(
        "Journal of Marine Science and Technology",
        "sn-mathphys-num",
        "Verify marine-engineering figure handling, references, and any journal-specific metadata before calling the layout submission-ready.",
    ),
    "machine-learning": springer_target(
        "Machine Learning",
        "sn-mathphys-num",
        "Verify machine-learning article flow, bibliography option, and any live journal metadata before calling the layout submission-ready.",
    ),
    "neural-computing-and-applications": springer_target(
        "Neural Computing and Applications",
        "sn-mathphys-num",
        "Verify neural-computing article flow, bibliography option, and any live journal metadata before calling the layout submission-ready.",
    ),
    "ocean-dynamics": springer_target(
        "Ocean Dynamics",
        "sn-mathphys-num",
        "Verify ocean-science figure handling, references, and journal-specific metadata before calling the layout submission-ready.",
    ),
    "soft-computing": springer_target(
        "Soft Computing",
        "sn-mathphys-num",
        "Verify soft-computing article flow, bibliography option, and any live journal metadata before calling the layout submission-ready.",
    ),
    "bmc": springer_target(
        "BMC Family",
        "sn-vancouver-num",
        "Use this family baseline only when the exact BMC target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live guidance.",
        source="https://www.biomedcentral.com/getpublished/manuscript-preparation",
    ),
    "bmc-bioinformatics": springer_target(
        "BMC Bioinformatics",
        "sn-vancouver-num",
        "Verify bioinformatics-specific reporting expectations, supplementary material handling, and any live journal metadata before calling the layout submission-ready.",
        source="https://www.biomedcentral.com/getpublished/manuscript-preparation",
    ),
    "nature-portfolio": springer_target(
        "Nature Portfolio Family",
        "sn-nature",
        "Use this family baseline only when the exact Nature Portfolio journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live guidance.",
        source="https://www.nature.com/nature-portfolio/for-authors/formatting-guide",
    ),
    "nature": springer_target(
        "Nature",
        "sn-nature",
        "Verify Nature-specific editorial expectations, figure density, and any live journal metadata before calling the layout submission-ready.",
        source="https://www.nature.com/nature-portfolio/for-authors/formatting-guide",
    ),
    "nature-communications": springer_target(
        "Nature Communications",
        "sn-nature",
        "Verify Nature Communications-specific reporting expectations, figure-caption layout, and any live journal metadata before calling the layout submission-ready.",
        source="https://www.nature.com/ncomms/for-authors/formatting-guide",
    ),
    "scientific-reports": springer_target(
        "Scientific Reports",
        "sn-nature",
        "Verify Scientific Reports-specific reporting expectations, figure-caption layout, and any live journal metadata before calling the layout submission-ready.",
        source="https://www.nature.com/nature-portfolio/for-authors/formatting-guide",
    ),
    "acs": acs_target(
        "ACS Family",
        "Use this family baseline only when the exact ACS target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live ACS guidance.",
    ),
    "acs-sensors": acs_target(
        "ACS Sensors",
        "Verify ACS Sensors-specific graphical elements, abstract style, and bibliography tooling before calling the layout submission-ready.",
    ),
    "journal-of-chemical-information-and-modeling": acs_target(
        "Journal of Chemical Information and Modeling",
        "Verify chemical-information-specific figure handling, supplementary information expectations, and journal-specific frontmatter before calling the layout submission-ready.",
    ),
    "aip": aip_target(
        "AIP Family",
        "apl",
        "Use this family baseline only when the exact AIP target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live AIP guidance.",
    ),
    "applied-physics-letters": aip_target(
        "Applied Physics Letters",
        "apl",
        "Verify APL letter-format constraints, rapid-communication expectations, and figure-density limits before calling the layout submission-ready.",
    ),
    "acm": acm_target(
        "ACM Family",
        "CSUR",
        "Use this family baseline only when the exact ACM target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live ACM guidance.",
        source="https://www.acm.org/publications/authors/submissions-top",
    ),
    "acm-computing-surveys": acm_target(
        "ACM Computing Surveys",
        "CSUR",
        "Verify survey-paper expectations, section depth, and any ACM Computing Surveys-specific editorial guidance before calling the layout submission-ready.",
        source="https://www.acm.org/publications/authors/submissions-top",
    ),
    "acm-transactions-on-graphics": acm_target(
        "ACM Transactions on Graphics",
        "TOG",
        "Verify graphics-specific figure density, teaser image rules, and any ACM TOG submission expectations before calling the layout submission-ready.",
        source="https://www.acm.org/publications/authors/submissions-top",
    ),
    "ieee": ieee_target(
        "IEEE Family Baseline",
        "Use this family baseline only when the exact IEEE target journal has not yet been fixed; once the venue is known, tighten the manuscript against that journal's live author page.",
    ),
    "ieee-asme-transactions-on-mechatronics": ieee_target(
        "IEEE/ASME Transactions on Mechatronics",
        "Verify joint IEEE/ASME author-note expectations, multimedia allowances, and mechatronics-specific figure density.",
    ),
    "ieee-access": ieee_target(
        "IEEE Access",
        "Verify article type metadata, funding statements, and any journal-specific front matter blocks.",
    ),
    "ieee-control-systems-letters": ieee_target(
        "IEEE Control Systems Letters",
        "Verify letter-specific length limits, conference-option metadata, and concise supplementary-material rules.",
    ),
    "ieee-internet-of-things-journal": ieee_target(
        "IEEE Internet of Things Journal",
        "Verify special issue track metadata, dataset or artifact expectations, and any current policy statements.",
    ),
    "ieee-joe": ieee_target(
        "IEEE Journal of Oceanic Engineering",
        "Verify the target journal option set, author note requirements, and figure placement expectations.",
    ),
    "ieee-jstars": ieee_target(
        "IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing",
        "Verify special-topic call metadata, submission-track requirements, and any current artwork rules.",
    ),
    "ieee-ral": ieee_target(
        "IEEE Robotics and Automation Letters",
        "Verify letter-specific length limits, figure density, and conference-option metadata if applicable.",
    ),
    "ieee-sensors-journal": ieee_target(
        "IEEE Sensors Journal",
        "Verify abstract and keyword expectations, plus any sensor-domain appendix or data policy notes.",
    ),
    "ieee-tcyb": ieee_target(
        "IEEE Transactions on Cybernetics",
        "Verify journal-specific scope statements, supplementary material handling, and manuscript length constraints.",
    ),
    "ieee-tits": ieee_target(
        "IEEE Transactions on Intelligent Transportation Systems",
        "Verify front matter details, figure-table density, and any special author biography requirements.",
    ),
    "ieee-tnnls": ieee_target(
        "IEEE Transactions on Neural Networks and Learning Systems",
        "Verify citation density, appendix strategy, and journal-specific submission metadata.",
    ),
    "ieee-transactions-on-automation-science-and-engineering": ieee_target(
        "IEEE Transactions on Automation Science and Engineering",
        "Verify article limits, optional supplementary files, and any special author instructions.",
        source="https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/author-checklist-for-papers-submitted-to-ieee-t-ase/",
    ),
    "ieee-transactions-on-control-systems-technology": ieee_target(
        "IEEE Transactions on Control Systems Technology",
        "Verify application-oriented article limits, implementation-heavy figure density, and control-technology-specific submission metadata.",
    ),
    "ieee-transactions-on-geoscience-and-remote-sensing": ieee_target(
        "IEEE Transactions on Geoscience and Remote Sensing",
        "Verify special artwork requirements, data or supplementary rules, and any sensing-specific submission assets.",
    ),
    "ieee-transactions-on-industrial-electronics": ieee_target(
        "IEEE Transactions on Industrial Electronics",
        "Verify overlength policy, industrial-electronics artwork rules, and any current supplementary-material expectations.",
    ),
    "ieee-transactions-on-industrial-informatics": ieee_target(
        "IEEE Transactions on Industrial Informatics",
        "Verify application-domain metadata, data or benchmark disclosure, and cyber-physical supplementary-material requirements.",
    ),
    "ieee-transactions-on-instrumentation-and-measurement": ieee_target(
        "IEEE Transactions on Instrumentation and Measurement",
        "Verify current artwork requirements, measurement-specific submission files, and any live author-page policy notes.",
    ),
    "ieee-transactions-on-pattern-analysis-and-machine-intelligence": ieee_target(
        "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "Verify review-policy mode, appendix handling, and computer-vision benchmark or artifact expectations.",
    ),
    "ieee-transactions-on-systems-man-and-cybernetics-systems": ieee_target(
        "IEEE Transactions on Systems, Man, and Cybernetics: Systems",
        "Verify article type rules, page-limit expectations, and supplementary-material requirements.",
    ),
    "ieee-tro": ieee_target(
        "IEEE Transactions on Robotics",
        "Verify manuscript mode, multimedia or supplementary requirements, and biography handling.",
    ),
    "aerospace-science-and-technology": elsevier_target(
        "Aerospace Science and Technology",
        "https://www.sciencedirect.com/journal/aerospace-science-and-technology/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Use the imported numeric Elsevier sample until the live guide indicates a different citation mode or journal-specific manuscript variant.",
    ),
    "applied-ocean-research": elsevier_target(
        "Applied Ocean Research",
        "https://www.sciencedirect.com/journal/applied-ocean-research/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify frontmatter fields, figure rules, and any marine-domain supplementary requirements against the live guide for authors.",
    ),
    "ocean-engineering": elsevier_target(
        "Ocean Engineering",
        "https://www.sciencedirect.com/journal/ocean-engineering/publish/guide-for-authors",
        "elsarticle-template-harv.tex",
        "author-year",
        "The Ocean Engineering guide uses author-year citation examples, so the imported Elsevier author-year sample manuscript is the closest official baseline.",
    ),
    "applied-soft-computing": elsevier_target(
        "Applied Soft Computing",
        "https://www.sciencedirect.com/journal/applied-soft-computing/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "The Applied Soft Computing guide shows numbered square-bracket citations and also requests author biographies with photographs at submission.",
    ),
    "artificial-intelligence": elsevier_target(
        "Artificial Intelligence",
        "https://www.sciencedirect.com/journal/artificial-intelligence/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify article type, appendix treatment, and reference-style expectations against the live guide for authors.",
    ),
    "automatica": elsevier_target(
        "Automatica",
        "https://www.sciencedirect.com/journal/automatica/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify theorem environment usage, appendix numbering, and control-theory notation style against the live guide for authors.",
    ),
    "control-engineering-practice": elsevier_target(
        "Control Engineering Practice",
        "https://www.sciencedirect.com/journal/control-engineering-practice/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify citation mode, declaration sections, and control-domain figure-table balance against the live guide for authors.",
    ),
    "engineering-applications-of-artificial-intelligence": elsevier_target(
        "Engineering Applications of Artificial Intelligence",
        "https://www.sciencedirect.com/journal/engineering-applications-of-artificial-intelligence/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify declarations, highlights, and bibliography configuration against the live guide for authors.",
    ),
    "expert-systems-with-applications": elsevier_target(
        "Expert Systems with Applications",
        "https://www.sciencedirect.com/journal/expert-systems-with-applications/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify article structure, declaration sections, and any optional highlights requirement against the live guide for authors.",
    ),
    "information-sciences": elsevier_target(
        "Information Sciences",
        "https://www.sciencedirect.com/journal/information-sciences/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify manuscript section flow, reference formatting, and author metadata against the live guide for authors.",
    ),
    "isa-transactions": elsevier_target(
        "ISA Transactions",
        "https://www.sciencedirect.com/journal/isa-transactions/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify frontmatter fields, declarations, and any industrial-application formatting notes against the live guide for authors.",
    ),
    "measurement": elsevier_target(
        "Measurement",
        "https://www.sciencedirect.com/journal/measurement/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "The Measurement guide accepts flexible reference formatting at submission but illustrates numbered square-bracket citations and points authors back to the guide when no journal-specific template is available.",
    ),
    "neurocomputing": elsevier_target(
        "Neurocomputing",
        "https://www.sciencedirect.com/journal/neurocomputing/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify declaration requirements, manuscript length expectations, and bibliography style against the live guide for authors.",
    ),
    "ocean-modelling": elsevier_target(
        "Ocean Modelling",
        "https://www.sciencedirect.com/journal/ocean-modelling/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify equation presentation, data availability notes, and bibliography mode against the live guide for authors.",
    ),
    "pattern-recognition": elsevier_target(
        "Pattern Recognition",
        "https://www.sciencedirect.com/journal/pattern-recognition/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify figure density, supplementary material handling, and citation mode against the live guide for authors.",
    ),
    "reliability-engineering-and-system-safety": elsevier_target(
        "Reliability Engineering and System Safety",
        "https://www.sciencedirect.com/journal/reliability-engineering-and-system-safety/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Use the imported numeric Elsevier sample until the live guide indicates a different citation mode or journal-specific manuscript variant.",
    ),
    "robotics-and-autonomous-systems": elsevier_target(
        "Robotics and Autonomous Systems",
        "https://www.sciencedirect.com/journal/robotics-and-autonomous-systems/publish/guide-for-authors",
        "elsarticle-template-num.tex",
        "numeric",
        "Verify frontmatter setup, supplementary material handling, and article type-specific requirements against the live guide for authors.",
    ),
    "frontiers-in-neurorobotics": {
        "status": "verified",
        "template_family": "Frontiers official LaTeX template package",
        "verification_scope": "official-template-package",
        "source": "https://www.frontiersin.org/design/zip/Frontiers_LaTeX_Templates.zip",
        "compile_mode": "frontiers",
        "display_name": "Frontiers in Neurorobotics",
        "notes": [
            "Verified against the official Frontiers LaTeX template package downloaded into the local assets folder.",
            "Reference-style selection may still need a final journal-specific check, but the preview uses the actual Frontiers class files.",
        ],
        "official_template_import": {
            "source_page": "https://www.frontiersin.org/design/zip/Frontiers_LaTeX_Templates.zip",
            "package_url": "https://www.frontiersin.org/design/zip/Frontiers_LaTeX_Templates.zip",
            "local_package_root": "assets/official-templates/frontiers/template-package",
            "selected_template": "frontiers.tex",
            "class_file": "FrontiersinHarvard.cls",
        },
    },
    "plos-one": {
        "status": "verified",
        "template_family": "PLOS official LaTeX manuscript template",
        "verification_scope": "official-template-package",
        "source": "https://journals.plos.org/plosone/s/latex",
        "compile_mode": "plos",
        "display_name": "PLOS ONE",
        "notes": [
            "Verified against the official PLOS LaTeX manuscript template package downloaded into the local assets folder.",
            "The preview honors the manuscript-style restriction that figures should be treated as separate submission assets.",
        ],
        "official_template_import": {
            "source_page": "https://journals.plos.org/plosone/s/latex",
            "package_url": "",
            "local_package_root": "assets/official-templates/plos/template-package",
            "selected_template": "plos_latex_template.tex",
            "class_file": "",
        },
    },
    "robotics": {
        "status": "blocked",
        "template_family": "MDPI official journal template",
        "verification_scope": "blocked-missing-template-asset",
        "source": "https://www.mdpi.com/journal/robotics/instructions",
        "compile_mode": "blocked",
        "display_name": "Robotics",
        "notes": [
            "Official MDPI template assets were not available locally and direct retrieval was blocked in this environment.",
            "This journal cannot be honestly marked template-verified until the official MDPI template package is added.",
        ],
    },
}


def yaml_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_verification_yaml(slug: str, journal_dir: Path, cfg: dict[str, object]) -> None:
    lines = [
        f'slug: "{yaml_quote(slug)}"',
        f'display_name: "{yaml_quote(str(cfg["display_name"]))}"',
        f'status: "{yaml_quote(str(cfg["status"]))}"',
        f'verification_scope: "{yaml_quote(str(cfg["verification_scope"]))}"',
        f'template_family: "{yaml_quote(str(cfg["template_family"]))}"',
        f'official_source: "{yaml_quote(str(cfg["source"]))}"',
        f'compile_mode: "{yaml_quote(str(cfg["compile_mode"]))}"',
    ]
    if cfg["status"] == "verified":
        lines.extend(
            [
                'artifacts:',
                '  tex: "./official_preview.tex"',
                '  pdf: "./official_preview.pdf"',
                '  png: "./official_preview.png"',
            ]
        )
    else:
        lines.extend(
            [
                "artifacts:",
                '  tex: ""',
                '  pdf: ""',
                '  png: ""',
            ]
        )
    supporting_files = cfg.get("supporting_files")
    if isinstance(supporting_files, dict) and supporting_files:
        lines.append("supporting_files:")
        for key, value in supporting_files.items():
            lines.append(f'  {key}: "{yaml_quote(str(value))}"')
    journal_specific_validation = cfg.get("journal_specific_validation")
    if isinstance(journal_specific_validation, dict) and journal_specific_validation:
        lines.append("journal_specific_validation:")
        for key, value in journal_specific_validation.items():
            lines.append(f'  {key}: "{yaml_quote(str(value))}"')
    official_template_import = cfg.get("official_template_import")
    if isinstance(official_template_import, dict) and official_template_import:
        lines.append("official_template_import:")
        for key, value in official_template_import.items():
            lines.append(f'  {key}: "{yaml_quote(str(value))}"')
    verification_checks = cfg.get("verification_checks")
    if isinstance(verification_checks, list) and verification_checks:
        lines.append("verification_checks:")
        for check in verification_checks:
            lines.append(f'  - id: "{yaml_quote(str(check["id"]))}"')
            lines.append(f'    title: "{yaml_quote(str(check["title"]))}"')
            lines.append(f'    requirement: "{yaml_quote(str(check["requirement"]))}"')
    lines.append("notes:")
    for note in cfg["notes"]:
        lines.append(f'  - "{yaml_quote(str(note))}"')
    (journal_dir / "verification.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_layout_checklist(journal_dir: Path, cfg: dict[str, object]) -> None:
    verification_checks = cfg.get("verification_checks")
    if not isinstance(verification_checks, list) or not verification_checks:
        return
    verification_scope = str(cfg.get("verification_scope", ""))
    boundary_line = (
        "- Official template package verified through `official_preview.tex/.pdf/.png`."
        if verification_scope == "official-template-package"
        else "- Official template family verified through `official_preview.tex/.pdf/.png`."
    )
    lines = [
        f'# {cfg["display_name"]} Layout Checklist',
        "",
        "Use this checklist together with `verification.yaml` before calling the journal-specific layout submission-ready.",
        "",
        "## Verification Boundary",
        "",
        boundary_line,
        "- Journal-specific layout compliance still requires the checklist below.",
        "",
        "## Required Checks",
        "",
    ]
    for check in verification_checks:
        lines.append(f'- [ ] `{check["id"]}` {check["title"]}: {check["requirement"]}')
    lines.extend(
        [
            "",
            "## Supporting Files",
            "",
            "- `profile.md`",
            "- `verification.yaml`",
            "- `official_preview.tex`",
            "- `official_preview.pdf`",
            "- `official_preview.png`",
            "",
            "## Official Source",
            "",
            f'- {cfg["source"]}',
        ]
    )
    (journal_dir / "layout-checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_ieee_tex(title: str) -> str:
    return rf"""
\documentclass[journal]{{IEEEtran}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\usepackage{{array}}
\usepackage{{cite}}
\title{{{title}\\\large Submission Preview Derived from the IEEE Journal Sample}}
\author{{A.~Placeholder,~\IEEEmembership{{Member,~IEEE,}}%
B.~Example,~\IEEEmembership{{Senior Member,~IEEE,}}%
and C.~Template,~\IEEEmembership{{Member,~IEEE}}%
\thanks{{A. Placeholder and B. Example are with the Department of Template Verification, Placeholder Institute, City 100000, Country.}}%
\thanks{{C. Template is with the Systems Formatting Laboratory, Example University, City 200000, Country.}}%
\thanks{{Corresponding author: A. Placeholder (e-mail: verified@example.org). This file is a submission-style preview derived from the official bare jrnl journal sample in the IEEEtran package for layout inspection only.}}}}
\markboth{{IEEE Journal Template Library,~2026}}{{Template Library: {title}}}
\begin{{document}}
\maketitle
\begin{{abstract}}
This submission-style preview is rendered with the imported official IEEEtran package and follows the visual rhythm of the official bare jrnl journal sample. The content remains placeholder text, but the page is intentionally structured as a realistic engineering article so title treatment, author footnotes, abstract density, Index Terms, section spacing, equations, figures, tables, and references can be inspected in a form that is closer to an actual IEEE journal submission.
\end{{abstract}}
\begin{{IEEEkeywords}}
IEEE journal article, IEEEtran, journal sample, submission layout, figure placement, table formatting
\end{{IEEEkeywords}}
\section{{Introduction}}
\IEEEPARstart{{T}}{{he}} introduction is deliberately written as compact technical prose so the preview reads like a true journal manuscript rather than a loose placeholder poster. It lets the reviewer inspect how the title block, abstract, Index Terms, and first body paragraph interact under the official IEEEtran journal layout.

This opening section also makes it easier to judge whether the page density is credible for engineering submissions that need to communicate context, contribution, and scope immediately on the first page.
\section{{Related Work}}
The related-work section is included because many engineering manuscripts either keep it explicit or absorb it into the introduction. For the preview library, keeping it explicit produces a more inspectable first-page hierarchy and makes section transitions easier to assess.
\section{{Methodology}}
The methodology section introduces representative mathematics and a professional single-column figure so the preview can expose equation spacing, inline math rhythm, caption placement, and float behavior within the IEEE journal layout.
\begin{{equation}}
J = \sum_{{k=0}}^{{N-1}} \left( \alpha \lVert e_k \rVert_2^2 + \beta \lVert u_k \rVert_2^2 \right),
\end{{equation}}
where $e_k$ denotes the tracking error, $u_k$ denotes the control action, and $\alpha,\beta > 0$ are weighting terms used only to simulate realistic technical content.
\begin{{figure}}[!t]
\centering
\fbox{{\parbox[c][2.15in][c]{{0.94\linewidth}}{{\centering System Overview Placeholder\\[0.4em]\normalsize Perception Layer \quad|\quad Decision Layer \quad|\quad Control Layer}}}}
\caption{{Submission-style overview figure used to inspect single-column float width, caption spacing, and the visual balance between abstract, body text, and the first major figure in the IEEE journal layout.}}
\label{{fig:ieee-overview}}
\end{{figure}}
\section{{Experiments}}
The experiments section is expanded enough to reveal how quantitative discussion, figure references, and compact result tables behave in the verified IEEE manuscript form.
\subsection{{Experimental Setup}}
The setup paragraph acts as a placeholder for datasets, baselines, operating conditions, and hardware context, all of which typically appear before the main comparison table in a submission-ready paper.
\subsection{{Quantitative Results}}
Table~\ref{{tab:verified}} summarizes a compact benchmark comparison so the preview can verify caption-first table treatment, column packing, and metric readability.
\begin{{table}}[!t]
\caption{{Compact quantitative comparison used to verify IEEE caption-first table treatment, column packing, and metric readability in a submission-style manuscript preview.}}
\label{{tab:verified}}
\centering
\begin{{tabular}}{{>{{\raggedright\arraybackslash}}p{{1.35in}}cc}}
\toprule
Method & Success Rate & Latency \\
\midrule
Placeholder A & 91.2\% & 14 ms \\
Placeholder B & 88.4\% & 17 ms \\
Placeholder C & 84.1\% & 20 ms \\
\bottomrule
\end{{tabular}}
\end{{table}}
\subsection{{Ablation Perspective}}
A short ablation-style paragraph helps expose the section rhythm after the main comparison table and makes the second column read more like a genuine experimental section.
\section{{Conclusion and Discussion}}
Fig.~\ref{{fig:ieee-overview}} and Table~\ref{{tab:verified}} jointly make the preview more representative of a practical IEEE submission page. The final section is intentionally concise: it gives the article a clear closing discussion while preserving the six-part manuscript skeleton requested for the IEEE library.
\begin{{thebibliography}}{{99}}
\bibitem{{ref1}} A. Smith and B. Lee, ``Template-aware engineering manuscript design for IEEE journal submissions,'' \emph{{IEEE Access}}, vol. 12, pp. 1--10, 2025.
\bibitem{{ref2}} C. Garcia, D. Patel, and E. Chen, ``Figure sizing and table density in two-column technical articles,'' \emph{{IEEE Trans. Ind. Electron.}}, vol. 71, no. 4, pp. 100--108, 2025.
\bibitem{{ref3}} F. Martin and G. Zhao, ``Practical guidance for structured first-page journal layouts,'' \emph{{IEEE Trans. Robot.}}, vol. 41, no. 1, pp. 50--58, 2026.
\end{{thebibliography}}
\begin{{IEEEbiography}}{{A. Placeholder}}
A. Placeholder received the B.S. degree in systems engineering from Placeholder University in 2018 and the M.S. degree in intelligent control from Example Institute in 2021. The current research interests include journal-format validation, robotics manuscript preparation, and technical communication workflows.
\end{{IEEEbiography}}
\begin{{IEEEbiography}}{{B. Example}}
B. Example received the B.Eng. degree in automation from Example University in 2017 and the Ph.D. degree in electrical engineering from Placeholder Institute in 2024. The research interests include engineering document pipelines, benchmark reporting, and reproducible manuscript preparation.
\end{{IEEEbiography}}
\begin{{IEEEbiography}}{{C. Template}}
C. Template is a research engineer with the Systems Formatting Laboratory, Example University. The work focuses on template-aware publishing workflows, scientific figure organization, and submission-ready technical paper layout.
\end{{IEEEbiography}}
\end{{document}}
"""


def build_elsevier_tex(title: str, selected_template: str, reference_mode: str) -> str:
    class_options = "preprint,12pt,authoryear" if reference_mode == "author-year" else "preprint,12pt"
    bibliography_block = (
        r"\begin{thebibliography}{00}"
        "\n"
        r"\bibitem[Smith and Lee(2025)]{ref1} A. Smith, B. Lee, 2025. Template-aware Elsevier manuscript preparation. Journal of Placeholder Studies 10, 1--9."
        "\n"
        r"\bibitem[Garcia and Patel(2026)]{ref2} C. Garcia, D. Patel, 2026. Figure and table balance in author manuscripts. Example Engineering Journal 14, 22--31."
        "\n"
        r"\end{thebibliography}"
        if reference_mode == "author-year"
        else r"\begin{thebibliography}{00}"
        "\n"
        r"\bibitem{ref1} A. Smith, B. Lee, 2025. Template-aware Elsevier manuscript preparation. Journal of Placeholder Studies 10, 1--9."
        "\n"
        r"\bibitem{ref2} C. Garcia, D. Patel, 2026. Figure and table balance in author manuscripts. Example Engineering Journal 14, 22--31."
        "\n"
        r"\end{thebibliography}"
    )
    return rf"""
\documentclass[{class_options}]{{elsarticle}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\begin{{document}}
\journal{{{title}}}
\begin{{frontmatter}}
\title{{{title}: Official Elsevier Submission Preview}}
\tnotetext[t1]{{Imported official template baseline: {selected_template}.}}
\author{{A. Placeholder}}
\author{{B. Example}}
\address{{Department of Verified Templates, Placeholder Institute}}
\begin{{abstract}}
This submission-style preview is rendered with the imported official Elsevier elsarticle package and arranged as a realistic author-manuscript. The page is intentionally generic in scientific content but explicit about frontmatter, section flow, figure and table treatment, and the guide-aligned template baseline selected for this journal.
\end{{abstract}}
\begin{{keyword}}
journal template \sep official Elsevier package \sep author manuscript \sep formatting verification
\end{{keyword}}
\end{{frontmatter}}
\section{{Introduction}}
This verified preview follows the official Elsevier package imported from the publisher LaTeX instructions page rather than relying only on the local TeX installation. The section layout is expanded so the author-manuscript rhythm is easier to inspect.
\section{{Related Work}}
The related-work section gives the preview a more realistic research-paper hierarchy and helps expose how Elsevier frontmatter transitions into the technical body.
\section{{Methodology}}
The methodology section introduces representative technical content and a single-column figure so the imported template can be checked under a realistic load.
\begin{{equation}}
J = \sum_{{k=1}}^{{N}} \left( \alpha \|e_k\|_2^2 + \beta \|u_k\|_2^2 \right).
\end{{equation}}
\begin{{figure}}[t]
\centering
\fbox{{\parbox[c][2.1in][c]{{0.84\linewidth}}{{\centering Elsevier Figure Placeholder\\[0.4em]\normalsize System architecture, workflow, or experimental scene}}}}
\caption{{Single-column figure used to inspect the imported Elsevier author-manuscript layout, caption spacing, and float balance.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough content to inspect table density, caption placement, and the relationship between quantitative discussion and the surrounding body text.
\subsection{{Experimental Setup}}
This paragraph acts as a placeholder for datasets, hardware conditions, baseline settings, and protocol details that would normally appear in an Elsevier engineering paper.
\subsection{{Quantitative Results}}
\begin{{table}}[t]
\centering
\caption{{Quantitative comparison block used to inspect the imported Elsevier template under the journal-specific citation mode and frontmatter style.}}
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Time \\
\midrule
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the imported official Elsevier package path and displays the selected sample-manuscript variant: {selected_template}. The surrounding guide-for-authors rules still define the final journal-specific limits, declarations, artwork handling, and reference behavior at submission.
\section*{{Template Display}}
Imported package source: Elsevier LaTeX instructions. Selected manuscript baseline: {selected_template}. Guide-aligned citation mode for this preview: {reference_mode}.
{bibliography_block}
\end{{document}}
"""


def build_acm_tex(title: str, journal_code: str) -> str:
    return rf"""
\documentclass[manuscript]{{acmart}}
\setcopyright{{none}}
\settopmatter{{printacmref=false,printfolios=false}}
\acmJournal{{{journal_code}}}
\acmYear{{2026}}
\title{{{title}: Official ACM Submission Preview}}
\author{{A. Placeholder}}
\email{{verified@example.org}}
\affiliation{{%
  \institution{{Department of Verified Templates, Placeholder Institute}}
  \city{{Placeholder City}}
  \country{{Country}}
}}
\author{{B. Example}}
\affiliation{{%
  \institution{{Journal Systems Lab, Example University}}
  \city{{Example City}}
  \country{{Country}}
}}
\begin{{document}}
\begin{{abstract}}
This submission-style preview is rendered with the official ACM acmart template in manuscript mode. The content remains placeholder text, but the page is intentionally organized as a realistic review-format article so the ACM-specific front matter, section hierarchy, figure flow, table rhythm, CCS metadata, and bibliography style are easier to inspect.
\end{{abstract}}
\keywords{{ACM template, manuscript review format, official preview, figure placement, table placement}}
\begin{{CCSXML}}
<ccs2012>
<concept>
<concept_id>10010147.10010178</concept_id>
<concept_desc>Computing methodologies</concept_desc>
<concept_significance>500</concept_significance>
</concept>
</ccs2012>
\end{{CCSXML}}
\ccsdesc[500]{{Computing methodologies}}
\maketitle
\section{{Introduction}}
The introduction is written as compact technical prose so the manuscript preview reads like a plausible ACM journal submission rather than a bare template check page. This makes the relation between title block, abstract, CCS concepts, and early body text easier to judge.
\section{{Related Work}}
The related-work section remains explicit because it helps reveal how the ACM manuscript layout handles dense section transitions, literature framing, and survey-style or method-style context.
\section{{Methodology}}
The methodology section introduces representative mathematics and a figure placeholder so the acmart review-format page can be inspected under more realistic technical content.
\begin{{equation}}
L = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\begin{{figure}}[t]
\centering
\fbox{{\parbox[c][2.0in][c]{{0.88\linewidth}}{{\centering ACM Figure Placeholder\\[0.4em]\normalsize Pipeline overview, rendering graph, or system diagram}}}}
\caption{{Representative figure block used to inspect the official ACM manuscript layout, caption spacing, and the balance between body text and the first major figure.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough structure to expose table treatment, subsection rhythm, and the transition from methods to quantitative comparison.
\subsection{{Experimental Setup}}
This paragraph acts as a placeholder for datasets, user studies, rendering conditions, baseline systems, and protocol details.
\subsection{{Quantitative Results}}
\begin{{table}}[t]
\caption{{Quantitative comparison block used to inspect the official ACM manuscript template under realistic submission-style content.}}
\centering
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Time \\
\midrule
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the official ACM template path while preserving the six-part manuscript skeleton requested for the library. The resulting preview is intended to feel closer to a serious review-format submission than to a minimal placeholder sheet.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee. 2025. Template-aware ACM manuscript preparation. \emph{{ACM Journal Placeholder}} 1, 1 (2025), 1--10.
\bibitem{{ref2}} C. Garcia and D. Patel. 2026. Figure and table balance in review-format ACM articles. \emph{{ACM Comput. Surv.}} 59, 2 (2026), 1--14.
\end{{thebibliography}}
\end{{document}}
"""


def build_acs_tex(title: str) -> str:
    return rf"""
\documentclass[manuscript=article]{{achemso}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\author{{A. Placeholder}}
\affiliation{{Department of Verified Templates, Placeholder Institute, Placeholder City, Country}}
\email{{verified@example.org}}
\author{{B. Example}}
\affiliation{{Journal Systems Lab, Example University, Example City, Country}}
\title{{{title}: Official ACS Submission Preview}}
\begin{{document}}
\begin{{abstract}}
This submission-style preview is rendered with the official ACS achemso class in manuscript article mode. The content remains placeholder text, but the article is intentionally structured to expose chemistry-oriented front matter, section flow, figure balance, table treatment, and references in a form that is closer to a practical ACS submission.
\end{{abstract}}
\section{{Introduction}}
The introduction is written as compact scientific prose so the preview reads like a real ACS manuscript rather than a bare template check page.
\section{{Related Work}}
The related-work section is explicit so the page rhythm reveals how prior chemistry literature, methods, and experiments separate within the manuscript.
\section{{Methodology}}
The methodology section introduces representative notation and a figure placeholder so the ACS template can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{S}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\begin{{figure}}[ht]
\centering
\fbox{{\parbox[c][2.0in][c]{{0.82\linewidth}}{{\centering ACS Figure Placeholder\\[0.4em]\normalsize Sensor schematic, assay pipeline, or molecular workflow}}}}
\caption{{Representative ACS figure block used to inspect manuscript-mode spacing, caption treatment, and the transition from methods text to the first major figure.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough structure to expose table handling, subsection rhythm, and the transition from methods to quantitative comparison.
\subsection{{Experimental Setup}}
This paragraph acts as a placeholder for experimental conditions, sensing platform details, sample preparation, and baseline methods.
\subsection{{Quantitative Results}}
\begin{{table}}[ht]
\caption{{Quantitative comparison block used to inspect the official ACS manuscript template under realistic submission-style content.}}
\centering
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Time \\
\midrule
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the official ACS template path while preserving the six-part manuscript skeleton requested for the library. The result is intended to read more like a review-ready chemistry submission than a simple placeholder sheet.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee. Template-aware ACS manuscript preparation. \textit{{ACS Placeholder Journal}} \textbf{{2025}}, \textit{{1}}, 1--10.
\bibitem{{ref2}} C. Garcia and D. Patel. Figure and table balance in chemistry manuscripts. \textit{{ACS Sensors}} \textbf{{2026}}, \textit{{2}}, 20--31.
\end{{thebibliography}}
\end{{document}}
"""


def build_aip_tex(title: str, journal_option: str) -> str:
    return rf"""
\documentclass[aip,{journal_option},reprint]{{revtex4-2}}
\begin{{document}}
\title{{{title}: Official AIP Submission Preview}}
\author{{A. Placeholder}}
\affiliation{{Department of Verified Templates, Placeholder Institute, Placeholder City, Country}}
\email{{verified@example.org}}
\author{{B. Example}}
\affiliation{{Journal Systems Lab, Example University, Example City, Country}}
\begin{{abstract}}
This submission-style preview is rendered with the official REVTeX class in AIP journal mode. The manuscript remains generic in scientific content, but the page is structured to expose frontmatter, section hierarchy, figure flow, table treatment, and bibliography rhythm in a form closer to a realistic AIP submission.
\end{{abstract}}
\maketitle
\section{{Introduction}}
The introduction is written as concise technical prose so the preview feels like a practical AIP manuscript rather than a minimal template test page.
\section{{Related Work}}
The related-work section is explicit so the section hierarchy is easier to inspect when the page transitions from context to method and experiment.
\section{{Methodology}}
The methodology section introduces representative mathematics and a figure placeholder so the REVTeX layout can be reviewed under more realistic technical material.
\begin{{equation}}
L = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\begin{{figure}}[t]
\centering
\fbox{{\parbox[c][1.9in][c]{{0.84\linewidth}}{{\centering AIP Figure Placeholder\\[0.4em]\normalsize Optical setup, measurement layout, or device schematic}}}}
\caption{{Representative AIP figure used to inspect REVTeX spacing, caption placement, and the transition from methods text to the first major figure.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough content to expose quantitative comparison rhythm and table placement inside the AIP submission layout.
\subsection{{Experimental Setup}}
This paragraph stands in for sample preparation, hardware settings, measurement conditions, and baseline methods.
\subsection{{Quantitative Results}}
\begin{{table}}[t]
\caption{{Quantitative comparison block used to inspect the official AIP submission template under realistic manuscript content.}}
\centering
\begin{{tabular}}{{lcc}}
\hline
Method & Score & Time \\
\hline
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\hline
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the official AIP template path while preserving the six-part manuscript skeleton requested for the library. The preview is intended to read more like a review-format physics submission than a bare placeholder.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee, ``Template-aware AIP manuscript preparation,'' \textit{{AIP Placeholder Journal}} \textbf{{1}}, 1--10 (2025).
\bibitem{{ref2}} C. Garcia and D. Patel, ``Figure and table balance in REVTeX submissions,'' \textit{{Appl. Phys. Lett.}} \textbf{{124}}, 123456 (2026).
\end{{thebibliography}}
\end{{document}}
"""


def build_springer_tex(title: str, style_option: str) -> str:
    return rf"""
\documentclass[pdflatex,{style_option}]{{sn-jnl}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\begin{{document}}
\title[Article Title]{{{title}: Official Springer Nature Submission Preview}}
\author*[1]{{\fnm{{A.}} \sur{{Placeholder}}}}\email{{verified@example.org}}
\author[2]{{\fnm{{B.}} \sur{{Example}}}}
\affil*[1]{{\orgdiv{{Department}}, \orgname{{Placeholder Institute}}, \orgaddress{{\city{{Placeholder City}}, \country{{Country}}}}}}
\affil[2]{{\orgdiv{{Laboratory}}, \orgname{{Example University}}, \orgaddress{{\city{{Example City}}, \country{{Country}}}}}}
\abstract{{This submission-style preview is rendered with the imported official Springer Nature sn-article template package. The content remains placeholder text, but the page is intentionally structured as a realistic article so front matter, section hierarchy, figure-table rhythm, and bibliography style are easier to inspect.}}
\keywords{{Springer Nature template, official preview, submission layout, figure placement, table placement}}
\maketitle
\section{{Introduction}}
The introduction is written as compact technical prose so the preview reads more like a practical Springer Nature submission than a bare template check page.
\section{{Related Work}}
The related-work section is explicit so the preview reveals how literature framing, methods, and experiments separate within the article.
\section{{Methodology}}
The methodology section introduces representative mathematics and a figure placeholder so the imported sn-jnl package can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\begin{{figure}}[t]
\centering
\fbox{{\parbox[c][2.0in][c]{{0.85\linewidth}}{{\centering Springer Figure Placeholder\\[0.4em]\normalsize Pipeline overview, experiment setup, or system diagram}}}}
\caption{{Representative figure block used to inspect the official Springer Nature template, caption spacing, and the transition from methods text to the first major figure.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough structure to expose table treatment, subsection rhythm, and the transition from methods to quantitative comparison.
\subsection{{Experimental Setup}}
This paragraph acts as a placeholder for datasets, experimental conditions, baseline systems, and protocol details.
\subsection{{Quantitative Results}}
\begin{{table}}[t]
\caption{{Quantitative comparison block used to inspect the official Springer Nature template under realistic submission-style content.}}
\centering
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Time \\
\midrule
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the imported official Springer Nature template path while preserving the six-part manuscript skeleton requested for the library.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee, ``Template-aware Springer Nature manuscript preparation,'' \textit{{Springer Placeholder Journal}} (2025).
\bibitem{{ref2}} C. Garcia and D. Patel, ``Figure and table balance in journal article templates,'' \textit{{Scientific Reports}} (2026).
\end{{thebibliography}}
\end{{document}}
"""


def build_wiley_tex(title: str, style_option: str) -> str:
    return rf"""
\documentclass[{style_option},twocolumn]{{USG}}
\usepackage{{anyfontsize}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\graphicspath{{{{./images/}}}}
\articletype{{ORIGINAL ARTICLE}}
\journal{{{title}}}
\volume{{1}}
\copyyear{{2026}}
\startpage{{1}}
\articledoi{{10.1002/placeholder}}
\begin{{document}}
\title{{{title}: Official Wiley Submission Preview}}
\author[1]{{A. Placeholder}}
\author[2]{{B. Example}}
\authormark{{PLACEHOLDER \textsc{{et al.}}}}
\titlemark{{{title}: Official Wiley Submission Preview}}
\address[1]{{\orgdiv{{Department}}, \orgname{{Placeholder Institute, }}\orgaddress{{\state{{State}}, \country{{Country}}}}}}
\address[2]{{\orgdiv{{Laboratory}}, \orgname{{Example University, }}\orgaddress{{\state{{State}}, \country{{Country}}}}}}
\corres{{A. Placeholder (\email{{verified@example.org}})}}
\keywords{{template | preview | wiley}}
\abstract[ABSTRACT]{{This submission-style preview is rendered with the imported official Wiley PDF design package. The content remains placeholder text, but the page is intentionally structured as a realistic journal article so front matter, section hierarchy, figure-table rhythm, and bibliography style are easier to inspect.}}
\maketitle
\section{{Introduction}}
The introduction is written as compact technical prose so the preview reads more like a practical Wiley submission than a bare template check page.
\section{{Related Work}}
The related-work section is explicit so the preview reveals how literature framing, methods, and experiments separate within the article.
\section{{Methodology}}
The methodology section introduces representative mathematics and a figure placeholder so the imported Wiley package can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\begin{{figure*}}[htb]
\centerline{{\includegraphics[width=.8\linewidth,height=7pc,draft]{{empty}}}}
\caption{{Representative Wiley figure block used to inspect manuscript spacing, caption treatment, and the transition from methods text to the first major figure.}}
\end{{figure*}}
\section{{Experiments}}
The experiments section provides enough structure to expose table treatment, subsection rhythm, and the transition from methods to quantitative comparison.
\subsection{{Experimental Setup}}
This paragraph acts as a placeholder for datasets, experimental conditions, baseline systems, and protocol details.
\subsection{{Quantitative Results}}
\begin{{table}}[htb]
\caption{{Quantitative comparison block used to inspect the official Wiley template under realistic submission-style content.}}
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Time \\
\midrule
Placeholder A & 0.91 & 1.4 \\
Placeholder B & 0.88 & 1.7 \\
Placeholder C & 0.84 & 2.0 \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the imported official Wiley template path while preserving the six-part manuscript skeleton requested for the library.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee. Template-aware Wiley manuscript preparation. \textit{{Wiley Placeholder Journal}} 1 (2025): 1--10.
\bibitem{{ref2}} C. Garcia and D. Patel. Figure and table balance in Wiley journal articles. \textit{{Journal of Field Robotics}} 2 (2026): 20--31.
\end{{thebibliography}}
\end{{document}}
"""


def build_frontiers_tex(title: str) -> str:
    return rf"""
\documentclass[utf8]{{FrontiersinHarvard}}
\usepackage{{url,hyperref,lineno,microtype,subcaption}}
\usepackage[onehalfspacing]{{setspace}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\linenumbers
\def\keyFont{{\fontsize{{8}}{{11}}\helveticabold }}
\def\firstAuthorLast{{Placeholder {{et~al.}}}}
\def\Authors{{A. Placeholder$^{{1,*}}$, B. Example$^{{1}}$ and C. Template$^{{2}}$}}
\def\Address{{$^{{1}}$Department of Verified Templates, Placeholder Institute, City, Country \\
$^{{2}}$Journal Systems Lab, Example University, City, Country}}
\def\corrAuthor{{A. Placeholder}}
\def\corrEmail{{verified@example.org}}
\begin{{document}}
\onecolumn
\firstpage{{1}}
\title[Running Title]{{{title}: Official Frontiers Submission Preview}}
\author[\firstAuthorLast]{{\Authors}}
\address{{}}
\correspondance{{}}
\extraAuth{{}}
\maketitle
\begin{{abstract}}
\section{{}}
This submission-style preview is rendered with the imported official Frontiers template package and expanded into a realistic journal-manuscript skeleton. The content remains generic, but the page is intentionally arranged to show specialty metadata, correspondence, structured section flow, figure-table balance, and end statements in a form that is closer to a real Frontiers submission.
\tiny
\keyFont{{ \section{{Keywords:}} neurorobotics, official template, submission preview, embodied intelligence, formatting check}}
\end{{abstract}}
\section{{Introduction}}
This verified preview uses the official Frontiers class files from the publisher template package rather than a generic style engine. The opening section is written to resemble a concise introduction from a neurorobotics article so the reader can inspect how the title block, specialty metadata, abstract, and early body paragraphs relate on the first page.
\section{{Related Work}}
The related-work section is kept explicit so the preview resembles a true research article rather than a bare template sheet. This helps expose the vertical rhythm between literature framing, method description, and the first major figure or table.
\section{{Methodology}}
The methodology section introduces a representative equation and a figure placeholder so the official Frontiers package can be checked under a more realistic technical load.
\begin{{equation}}
J = \sum_{{k=1}}^{{N}} \left( \alpha \lVert e_k \rVert_2^2 + \beta \lVert u_k \rVert_2^2 \right).
\end{{equation}}
Here, $e_k$ denotes a placeholder tracking error, $u_k$ denotes an actuation term, and $\alpha,\beta > 0$ are weights included purely to make the preview read like a technical manuscript.
\begin{{figure}}[h]
\centering
\fbox{{\parbox[c][2.2in][c]{{0.82\linewidth}}{{\centering Frontiers Figure Placeholder\\[0.4em]\normalsize Experimental setup, embodiment diagram, or control pipeline}}}}
\caption{{Representative figure block used to inspect the official Frontiers manuscript form, caption spacing, and the visual relationship between the methods text and the first major figure.}}
\end{{figure}}
\section{{Experiments}}
The experiments section provides enough quantitative structure to make the preview more inspectable at a glance and closer to a practical submission manuscript.
\subsection{{Experimental Setup}}
This paragraph stands in for hardware conditions, datasets, simulation settings, and baseline models typically reported in a Frontiers submission.
\subsection{{Quantitative Results}}
\begin{{table}}[h]
\caption{{Quantitative comparison table used to inspect the imported Frontiers package under a realistic neurorobotics-paper rhythm.}}
\centering
\begin{{tabular}}{{lcc}}
\toprule
Method & Score & Latency \\
\midrule
Placeholder A & 0.91 & 14 ms \\
Placeholder B & 0.88 & 17 ms \\
Placeholder C & 0.84 & 20 ms \\
\bottomrule
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the official Frontiers template path for this journal target while also making the section structure, figure flow, and reporting statements easier to inspect as a serious submission-style preview.
\section*{{Data availability statement}}
Placeholder data and code would be referenced here.
\section*{{Author contributions}}
All contributions are placeholders for template verification.
\section*{{Conflict of interest}}
The authors declare no conflict of interest in this verified preview.
\section*{{Funding}}
Placeholder funding statement.
\begin{{thebibliography}}{{9}}
\bibitem[Placeholder and Example(2026)]{{ref1}} Placeholder, A. and Example, B. (2026). Verified template note. \textit{{Front. Neurorobot.}} 1:1--2.
\end{{thebibliography}}
\end{{document}}
"""


def build_plos_tex(title: str) -> str:
    return rf"""
\documentclass[10pt,letterpaper]{{article}}
\usepackage[top=0.85in,left=2.75in,footskip=0.75in]{{geometry}}
\usepackage{{amsmath,amssymb}}
\usepackage{{changepage}}
\usepackage{{textcomp,marvosym}}
\usepackage{{cite}}
\usepackage{{nameref,hyperref}}
\usepackage[right]{{lineno}}
\usepackage[nopatch=eqnum]{{microtype}}
\DisableLigatures[f]{{encoding = *, family = * }}
\usepackage[table]{{xcolor}}
\usepackage{{array}}
\usepackage[aboveskip=1pt,labelfont=bf,labelsep=period,justification=raggedright,singlelinecheck=off]{{caption}}
\renewcommand{{\figurename}}{{Fig}}
\raggedright
\setlength{{\parindent}}{{0.5cm}}
\textwidth 5.25in
\textheight 8.75in
\linenumbers
\begin{{document}}
\begin{{flushleft}}
{{\Large\bfseries {title}: Official PLOS Submission Preview}}
\end{{flushleft}}
\section*{{Abstract}}
This submission-style preview is rendered from the official PLOS manuscript template package. The content remains placeholder text, but the page has been expanded into a more realistic article skeleton so the manuscript-style front matter, section organization, figure-caption handling, and end statements can be reviewed more professionally.
\section*{{Author summary}}
This placeholder summary demonstrates the front-matter flow expected in the PLOS manuscript template and makes the preview easier to compare with an actual submission manuscript.
\section{{Introduction}}
The verified preview uses the official PLOS manuscript-style setup. In accordance with the official template notes, figures are treated as separate submission assets rather than embedded graphics, so the page shows caption-based figure placement rather than inlined artwork.
\section{{Related Work}}
The related-work section is kept explicit so the preview resembles a real scientific manuscript rather than a single-page template sheet. This also helps reveal whether the section hierarchy remains clear when the article is read in manuscript form.
\section{{Methodology}}
The methodology section introduces a representative equation and a manuscript-style figure caption so the official PLOS package can be checked with more realistic technical material.
\begin{{equation}}
L = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2
\end{{equation}}
\paragraph{{Fig 1.}} Placeholder figure caption for a separately submitted figure asset showing the system pipeline, evaluation setup, or biological inspiration diagram.
\section{{Experiments}}
The experiments section provides enough structure to inspect the manuscript-style table placement and the body rhythm around quantitative content.
\subsection{{Experimental Setup}}
This paragraph acts as a stand-in for datasets, protocol details, baseline systems, and implementation notes.
\subsection{{Quantitative Results}}
\begin{{table}}[!ht]
\caption{{Quantitative comparison block used to inspect the official PLOS manuscript template under a more realistic submission-style section flow.}}
\centering
\begin{{tabular}}{{lcc}}
\hline
Method & Score & Time\\
\hline
Placeholder A & 0.91 & 1.4\\
Placeholder B & 0.88 & 1.7\\
Placeholder C & 0.84 & 2.0\\
\hline
\end{{tabular}}
\end{{table}}
\section{{Conclusion and Discussion}}
This page verifies the official PLOS manuscript template path for this journal target while preserving the manuscript-style conventions that matter most during initial submission review.
\section*{{Data Availability}}
Placeholder data availability statement.
\section*{{References}}
\begin{{enumerate}}
\item Placeholder A, Example B (2026) Verified template note for PLOS manuscript checking.
\end{{enumerate}}
    \end{{document}}
"""


def build_copernicus_tex(title: str) -> str:
    return rf"""
\documentclass[os,manuscript]{{copernicus}}
\usepackage{{booktabs}}
\usepackage{{amsmath}}
\begin{{document}}
\title{{{title}: Official Copernicus Submission Preview}}
\Author[1][verified@example.org]{{A.}}{{Placeholder}}
\Author[1]{{B.}}{{Example}}
\Author[2]{{C.}}{{Template}}
\affil[1]{{Department of Verified Templates, Placeholder Institute, City, Country}}
\affil[2]{{Journal Systems Lab, Example University, City, Country}}
\runningtitle{{{title}: Official Copernicus Submission Preview}}
\runningauthor{{Placeholder et al.}}
\begin{{abstract}}
This submission-style preview is rendered with the imported official Copernicus package. The page is intentionally structured as a realistic geoscience manuscript so front matter, section rhythm, figure-table balance, and declaration blocks can be checked against the family baseline.
\end{{abstract}}
\section{{Introduction}}
The introduction is written as compact technical prose so the preview reads more like a practical Copernicus submission than a generic display page.
\section{{Related Work}}
The related-work section is explicit so the preview reveals how literature framing, methods, and experiments separate within the family baseline.
\section{{Methodology}}
The methodology section introduces representative mathematics and a figure placeholder so the local Copernicus package can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\section{{Experiments}}
The experiments section provides enough structure to expose table treatment and section rhythm inside the Copernicus family baseline.
\section{{Conclusion and Discussion}}
This page verifies the imported official Copernicus package path while preserving the six-part manuscript skeleton requested for the library.
\authorcontribution{{All contributions are placeholders for template verification.}}
\competinginterests{{The authors declare that they have no conflict of interest.}}
\begin{{thebibliography}}{{9}}
\bibitem[Placeholder and Example(2026)]{{ref1}} Placeholder, A. and Example, B.: Template-aware Copernicus manuscript preparation, Placeholder Journal, 1, 1--2, 2026.
\end{{thebibliography}}
\end{{document}}
"""


def build_siam_tex(title: str) -> str:
    return rf"""
\documentclass[final]{{siamltex}}
\title{{{title}: Official SIAM Submission Preview}}
\author{{A. Placeholder\thanks{{Department of Verified Templates, Placeholder Institute, verified@example.org.}}
\and B. Example\thanks{{Journal Systems Lab, Example University.}}}}
\begin{{document}}
\maketitle
\begin{{abstract}}
This submission-style preview is rendered with the imported official SIAM package. The content remains placeholder text, but the page is intentionally structured as a realistic mathematics-oriented manuscript so theorem style, front matter, section flow, and bibliography treatment are easier to inspect.
\end{{abstract}}
\begin{{keywords}}
template verification, SIAM style, manuscript preview
\end{{keywords}}
\begin{{AMS}}
65K10, 93C95
\end{{AMS}}
\section{{Introduction}}
The introduction is written as compact technical prose so the preview reads more like a practical SIAM submission than a generic display page.
\section{{Related Work}}
The related-work section is explicit so the preview reveals how literature framing, methods, and experiments separate within the family baseline.
\section{{Methodology}}
The methodology section introduces representative notation and a theorem-style block so the imported SIAM package can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\section{{Experiments}}
The experiments section provides enough structure to expose quantitative comparison rhythm and table treatment inside the SIAM family baseline.
\section{{Conclusion and Discussion}}
This page verifies the imported official SIAM package path while preserving the six-part manuscript skeleton requested for the library.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee, {{\em Template-aware SIAM manuscript preparation}}, Placeholder Journal, 1 (2026), pp.~1--10.
\end{{thebibliography}}
\end{{document}}
"""


def build_iop_tex(title: str) -> str:
    return rf"""
\documentclass{{iopjournal}}
\begin{{document}}
\articletype{{Research Article}}
\title{{{title}: Official IOP Submission Preview}}
\author{{A. Placeholder$^1$ and B. Example$^2$}}
\affil{{$^1$Department of Verified Templates, Placeholder Institute, City, Country}}
\affil{{$^2$Journal Systems Lab, Example University, City, Country}}
\email{{verified@example.org}}
\keywords{{template verification, IOP style, manuscript preview}}
\begin{{abstract}}
This submission-style preview is rendered with the imported official IOP journal article package. The content remains placeholder text, but the page is intentionally structured as a realistic physics-oriented manuscript so front matter, section flow, figure-table rhythm, and end sections are easier to inspect.
\end{{abstract}}
\section{{Introduction}}
The introduction is written as compact technical prose so the preview reads more like a practical IOP submission than a generic display page.
\section{{Related Work}}
The related-work section is explicit so the preview reveals how literature framing, methods, and experiments separate within the family baseline.
\section{{Methodology}}
The methodology section introduces representative notation and a figure placeholder so the imported IOP package can be inspected under more realistic technical content.
\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2.
\end{{equation}}
\section{{Experiments}}
The experiments section provides enough structure to expose quantitative comparison rhythm and table treatment inside the IOP family baseline.
\section{{Conclusion and Discussion}}
This page verifies the imported official IOP package path while preserving the six-part manuscript skeleton requested for the library.
\ack{{Placeholder acknowledgment.}}
\funding{{Placeholder funding statement.}}
\data{{Placeholder data availability statement.}}
\section*{{References}}
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee, {{\it Template-aware IOP manuscript preparation}}, Placeholder Journal 1 (2026) 1--10.
\end{{thebibliography}}
\end{{document}}
"""


def compile_with_workdir(tex: str, target_dir: Path, extra_assets: Path | None = None) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    tex_out = target_dir / "official_preview.tex"
    pdf_out = target_dir / "official_preview.pdf"
    png_base = target_dir / "official_preview"
    tex_out.write_text(tex, encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        if extra_assets:
            for item in extra_assets.iterdir():
                dest = tmp_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        work_tex = tmp_path / "official_preview.tex"
        work_tex.write_text(tex, encoding="utf-8")
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", work_tex.name],
                cwd=tmp_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        shutil.copy2(tmp_path / "official_preview.pdf", pdf_out)
    subprocess.run(
        ["pdftocairo", "-png", "-singlefile", "-r", "180", str(pdf_out), str(png_base)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def generate_verified(
    slug: str,
    cfg: dict[str, object],
    journals_dir: Path,
    official_template_dir: Path,
) -> None:
    journal_dir = resolve_journal_dir(journals_dir, slug)
    write_verification_yaml(slug, journal_dir, cfg)
    write_layout_checklist(journal_dir, cfg)
    if cfg["status"] != "verified":
        return
    title = str(cfg["display_name"])
    mode = str(cfg["compile_mode"])
    if mode == "ieee":
        tex = build_ieee_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "ieee" / "template-package")
    elif mode == "acm":
        tex = build_acm_tex(title, str(cfg["journal_code"]))
        compile_with_workdir(tex, journal_dir, official_template_dir / "acm" / "template-package")
    elif mode == "acs":
        tex = build_acs_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "acs" / "template-package")
    elif mode == "aip":
        tex = build_aip_tex(title, str(cfg["journal_option"]))
        compile_with_workdir(tex, journal_dir, official_template_dir / "aip" / "template-package")
    elif mode == "springer":
        tex = build_springer_tex(title, str(cfg["style_option"]))
        compile_with_workdir(tex, journal_dir, official_template_dir / "springer" / "template-package")
    elif mode == "wiley":
        tex = build_wiley_tex(title, str(cfg["style_option"]))
        compile_with_workdir(tex, journal_dir, official_template_dir / "wiley" / "template-package")
    elif mode == "elsevier":
        tex = build_elsevier_tex(title, str(cfg["selected_template"]), str(cfg["reference_mode"]))
        compile_with_workdir(tex, journal_dir, official_template_dir / "elsevier" / "template-package")
    elif mode == "frontiers":
        tex = build_frontiers_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "frontiers" / "template-package")
    elif mode == "plos":
        tex = build_plos_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "plos" / "template-package")
    elif mode == "copernicus":
        tex = build_copernicus_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "copernicus" / "template-package")
    elif mode == "siam":
        tex = build_siam_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "siam" / "template-package")
    elif mode == "iop":
        tex = build_iop_tex(title)
        compile_with_workdir(tex, journal_dir, official_template_dir / "iop" / "template-package")
    else:
        raise ValueError(f"Unsupported compile mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render official-template preview assets and verification records for curated journals."
    )
    parser.add_argument(
        "--journals-root",
        default=str(DEFAULT_JOURNALS_DIR),
        help="Root directory containing journal profile folders.",
    )
    parser.add_argument(
        "--official-template-assets",
        default=str(DEFAULT_OFFICIAL_TEMPLATE_DIR),
        help="Directory containing locally available official template packages.",
    )
    parser.add_argument(
        "--include",
        nargs="*",
        default=list(TARGETS.keys()),
        help="Subset of journal slugs to process.",
    )
    args = parser.parse_args()
    journals_dir = Path(args.journals_root)
    official_template_dir = Path(args.official_template_assets)
    failures: list[str] = []
    for slug in args.include:
        if slug not in TARGETS:
            failures.append(f"{slug}: unknown target")
            continue
        try:
            generate_verified(slug, TARGETS[slug], journals_dir, official_template_dir)
            print(f"processed {slug}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{slug}: {exc}")
            print(f"failed {slug}: {exc}")
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(f"\nRendered verification assets for {len(args.include)} official-template targets.")


if __name__ == "__main__":
    main()

def resolve_journal_dir(root: Path, slug: str) -> Path:
    direct = root / slug
    if direct.is_dir():
        return direct
    matches = [path.parent for path in root.rglob("profile.md") if path.parent.name == slug]
    if not matches:
        raise FileNotFoundError(f"Unknown journal or family slug: {slug}")
    if len(matches) > 1:
        raise RuntimeError(f"Slug is ambiguous: {slug}")
    return matches[0]

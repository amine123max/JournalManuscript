#!/usr/bin/env python3
"""Render standardized official_preview assets for non-verified journal profile folders.

The generated `official_preview.tex/.pdf/.png` files provide conservative layout
references for the profile library. They are intentionally non-authoritative
and should not be used to claim official-template compliance on their own.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNALS_DIR = ROOT / "references" / "journals"


def resolve_profile_dir(root: Path, slug: str) -> Path:
    direct = root / slug
    if direct.is_dir():
        return direct
    matches = [path.parent for path in root.rglob("profile.md") if path.parent.name == slug]
    if not matches:
        raise FileNotFoundError(f"Unknown journal or family slug: {slug}")
    if len(matches) > 1:
        raise RuntimeError(f"Slug is ambiguous: {slug}")
    return matches[0]


@dataclass
class LayoutConfig:
    page_size: str = "a4paper"
    columns: int = 1
    title_align: str = "center"
    title_size: str = "LARGE"
    abstract_box: bool = False
    show_keywords: bool = True
    keywords_label: str = "Keywords"
    figure_caption_top: bool = False
    table_caption_top: bool = True
    reference_style: str = "numeric"
    show_highlights: bool = False
    show_graphical_abstract: bool = False
    show_article_type: bool = False
    show_significance: bool = False
    show_data_availability: bool = False
    show_author_contributions: bool = False
    show_competing_interests: bool = False
    show_ccs: bool = False
    show_theorem: bool = False
    show_specialty: bool = False
    show_correspondence: bool = False
    show_declarations: bool = False
    show_frontmatter_note: bool = False
    running_header: str = ""
    body_font_cmd: str = r"\small"
    accent_color: str = "black"
    subtitle: str = ""
    notes: list[str] = field(default_factory=list)


FAMILY_CONFIGS: dict[str, LayoutConfig] = {
    "ieee": LayoutConfig(
        page_size="letterpaper",
        columns=2,
        title_align="center",
        title_size="Large",
        show_keywords=True,
        keywords_label="Index Terms",
        reference_style="numeric",
        running_header="IEEE-style journal preview",
        accent_color="blue!45!black",
        subtitle="Compact two-column engineering manuscript",
    ),
    "elsevier": LayoutConfig(
        columns=1,
        title_align="left",
        abstract_box=False,
        show_keywords=True,
        show_highlights=True,
        show_graphical_abstract=True,
        show_declarations=True,
        reference_style="numeric",
        accent_color="orange!55!black",
        subtitle="Frontmatter-heavy publisher format",
    ),
    "springer": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_declarations=True,
        reference_style="numeric",
        accent_color="teal!60!black",
        subtitle="Journal package with structured front matter",
    ),
    "mdpi": LayoutConfig(
        columns=1,
        title_align="center",
        abstract_box=True,
        show_article_type=True,
        show_keywords=True,
        show_data_availability=True,
        show_author_contributions=True,
        show_competing_interests=True,
        reference_style="numeric",
        accent_color="red!65!black",
        subtitle="Metadata-rich open-access journal layout",
    ),
    "nature-portfolio": LayoutConfig(
        columns=1,
        title_align="left",
        title_size="huge",
        show_keywords=False,
        show_significance=True,
        reference_style="numeric",
        accent_color="black",
        subtitle="Editorialized high-impact science manuscript",
    ),
    "wiley": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_declarations=True,
        reference_style="author-year",
        accent_color="purple!65!black",
        subtitle="Publisher template with declarations and metadata",
    ),
    "taylor-francis": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        reference_style="author-year",
        accent_color="cyan!55!black",
        subtitle="Journal manuscript with review-copy style influences",
    ),
    "sage": LayoutConfig(
        columns=1,
        title_align="left",
        show_keywords=True,
        reference_style="author-year",
        accent_color="green!45!black",
        subtitle="Publisher-specific title page and citation conventions",
    ),
    "frontiers": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_specialty=True,
        show_correspondence=True,
        show_data_availability=True,
        show_competing_interests=True,
        reference_style="numeric",
        accent_color="magenta!55!black",
        subtitle="Specialty-led open-access submission format",
    ),
    "plos": LayoutConfig(
        columns=1,
        title_align="left",
        show_keywords=False,
        show_data_availability=True,
        show_author_contributions=True,
        show_competing_interests=True,
        reference_style="numeric",
        accent_color="green!60!black",
        subtitle="Open-science layout with reporting statements",
    ),
    "acs": LayoutConfig(
        columns=2,
        title_align="center",
        show_graphical_abstract=True,
        show_keywords=True,
        reference_style="numeric",
        accent_color="blue!60!black",
        subtitle="Chemistry-style two-column article layout",
    ),
    "aip": LayoutConfig(
        columns=2,
        title_align="center",
        show_keywords=False,
        reference_style="numeric",
        accent_color="gray!70!black",
        subtitle="Physics journal with compact two-column presentation",
    ),
    "iop": LayoutConfig(
        columns=2,
        title_align="center",
        show_keywords=False,
        reference_style="numeric",
        accent_color="blue!55!black",
        subtitle="Physics and measurement-oriented journal layout",
    ),
    "acm": LayoutConfig(
        columns=2,
        title_align="center",
        show_keywords=True,
        show_ccs=True,
        reference_style="author-year",
        accent_color="red!55!black",
        subtitle="Computing article format with CCS metadata",
    ),
    "oxford": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        reference_style="author-year",
        accent_color="blue!45!black",
        subtitle="Academic press journal format with classic metadata",
    ),
    "cambridge": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        reference_style="author-year",
        show_theorem=True,
        accent_color="brown!55!black",
        subtitle="Traditional journal layout with formal sectioning",
    ),
    "aaas": LayoutConfig(
        columns=1,
        title_align="left",
        title_size="huge",
        show_keywords=False,
        show_significance=True,
        reference_style="numeric",
        accent_color="black",
        subtitle="Editorial science-journal preview sheet",
    ),
    "siam": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_theorem=True,
        reference_style="numeric",
        accent_color="blue!70!black",
        subtitle="Mathematics and optimization manuscript format",
    ),
    "copernicus": LayoutConfig(
        columns=1,
        title_align="left",
        show_keywords=True,
        show_declarations=True,
        reference_style="author-year",
        accent_color="cyan!70!black",
        subtitle="Geoscience manuscript with open-review lineage",
    ),
    "royal-society": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_data_availability=True,
        reference_style="numeric",
        accent_color="purple!55!black",
        subtitle="Open-science format with publication statements",
    ),
    "nas": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=False,
        show_significance=True,
        reference_style="numeric",
        accent_color="red!50!black",
        subtitle="Broad-science format with significance framing",
    ),
    "cell-press": LayoutConfig(
        columns=1,
        title_align="left",
        title_size="huge",
        show_keywords=False,
        show_article_type=True,
        show_graphical_abstract=True,
        reference_style="numeric",
        accent_color="black",
        subtitle="Editorial life-science manuscript preview",
    ),
    "optica-publishing": LayoutConfig(
        columns=2,
        title_align="center",
        show_keywords=True,
        reference_style="numeric",
        accent_color="blue!65!black",
        subtitle="Optics-oriented two-column journal format",
    ),
    "hindawi": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_declarations=True,
        show_data_availability=True,
        reference_style="numeric",
        accent_color="orange!65!black",
        subtitle="Template with publisher statements and metadata",
    ),
    "bmc": LayoutConfig(
        columns=1,
        title_align="left",
        show_keywords=True,
        show_data_availability=True,
        show_author_contributions=True,
        show_competing_interests=True,
        reference_style="author-year",
        accent_color="teal!65!black",
        subtitle="Biomedical manuscript with structured declarations",
    ),
    "de-gruyter": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        reference_style="author-year",
        accent_color="gray!65!black",
        subtitle="Academic press manuscript with classic metadata",
    ),
    "emerald": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        reference_style="author-year",
        accent_color="green!55!black",
        subtitle="Applied journal format with article metadata",
    ),
    "custom-journal": LayoutConfig(
        columns=1,
        title_align="center",
        show_keywords=True,
        show_declarations=True,
        reference_style="numeric",
        accent_color="black",
        subtitle="Starter preview for a custom or unknown journal",
    ),
}


JOURNAL_OVERRIDES: dict[str, dict[str, object]] = {
    "ieee-asme-transactions-on-mechatronics": {
        "subtitle": "Mechatronics journal with integrated systems and control emphasis"
    },
    "ieee-control-systems-letters": {
        "subtitle": "Letter-style control journal with concise IEEE presentation"
    },
    "ieee-ral": {"subtitle": "Letter-style robotics manuscript preview"},
    "ieee-transactions-on-control-systems-technology": {
        "subtitle": "Control-technology journal with implementation-focused IEEE layout"
    },
    "ieee-transactions-on-industrial-electronics": {
        "subtitle": "Industrial-electronics journal in dense IEEE two-column style"
    },
    "ieee-transactions-on-industrial-informatics": {
        "subtitle": "Industrial-informatics journal with cyber-physical systems focus"
    },
    "ieee-transactions-on-automation-science-and-engineering": {
        "subtitle": "Automation systems journal in compact IEEE two-column style"
    },
    "ieee-transactions-on-systems-man-and-cybernetics-systems": {
        "subtitle": "Systems and cybernetics journal in IEEE two-column style"
    },
    "ieee-transactions-on-geoscience-and-remote-sensing": {
        "subtitle": "Remote-sensing journal in IEEE two-column style"
    },
    "ieee-jstars": {"subtitle": "Applied earth-observation journal in IEEE two-column style"},
    "ieee-transactions-on-instrumentation-and-measurement": {
        "subtitle": "Instrumentation journal in IEEE two-column style"
    },
    "ieee-internet-of-things-journal": {
        "subtitle": "Connected-systems journal in IEEE two-column style"
    },
    "ieee-transactions-on-pattern-analysis-and-machine-intelligence": {
        "subtitle": "Computer-vision and machine-intelligence journal in IEEE format"
    },
    "acm-computing-surveys": {"columns": 2, "subtitle": "Survey-style computing article preview"},
    "acm-transactions-on-graphics": {"columns": 2, "subtitle": "Graphics journal article preview"},
    "applied-soft-computing": {"subtitle": "Elsevier AI journal with frontmatter and declarations"},
    "measurement": {"subtitle": "Measurement journal with instrumentation-focused frontmatter"},
    "reliability-engineering-and-system-safety": {
        "subtitle": "Reliability journal with analytical first-page structure"
    },
    "aerospace-science-and-technology": {
        "subtitle": "Aerospace systems journal with engineering frontmatter"
    },
    "neural-computing-and-applications": {
        "subtitle": "Springer learning-systems journal preview"
    },
    "soft-computing": {"subtitle": "Springer soft-computing journal preview"},
    "ocean-dynamics": {"subtitle": "Springer marine-science journal preview"},
    "frontiers-in-neurorobotics": {
        "subtitle": "Frontiers specialty journal with open-science sections"
    },
    "robotics": {"subtitle": "MDPI robotics journal with declaration-rich metadata"},
    "machines": {"subtitle": "MDPI engineering journal with declaration-rich metadata"},
    "nature": {"subtitle": "Flagship editorial science article preview"},
    "nature-communications": {"subtitle": "Broad open-access science article preview"},
    "scientific-reports": {"show_keywords": True, "subtitle": "Open-access science article preview"},
    "plos-one": {"show_keywords": True, "subtitle": "PLOS-style article with open-science sections"},
    "science": {"subtitle": "AAAS flagship science article preview"},
    "science-robotics": {"subtitle": "AAAS robotics article preview"},
    "pnas": {"show_significance": True, "subtitle": "PNAS-style article with significance statement"},
    "journal-of-fluid-mechanics": {"show_theorem": True, "subtitle": "Mechanics journal with equation-heavy layout"},
    "siam-journal-on-control-and-optimization": {
        "show_theorem": True,
        "subtitle": "Optimization journal preview with theorem block",
    },
    "sensors": {"subtitle": "Sensor journal article with declarations"},
    "journal-of-marine-science-and-engineering": {"subtitle": "Marine engineering journal preview"},
    "ocean-engineering": {"subtitle": "Marine engineering article preview"},
}


def slug_to_title(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def read_profile_kind(profile_path: Path) -> tuple[str, str, str]:
    text = profile_path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)\s+Profile\s*$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else slug_to_title(profile_path.parent.name)
    family_match = re.search(r"^- Parent family:\s*(.+)$", text, re.MULTILINE)
    start_match = re.search(r"^- Start from:\s*\.\./([^/]+)/profile\.md$", text, re.MULTILINE)
    if family_match and start_match:
        return "journal", title, start_match.group(1).strip()
    return "family", title, profile_path.parent.name


def build_layout(profile_slug: str, kind: str, family_slug: str, title: str) -> LayoutConfig:
    base = FAMILY_CONFIGS.get(family_slug, FAMILY_CONFIGS["custom-journal"])
    config = LayoutConfig(**base.__dict__)
    config.notes = list(base.notes)
    config.notes.append("Simulated preview built from the local starter profile library.")
    config.notes.append("Use the official template to finalize submission-ready formatting.")
    config.subtitle = config.subtitle or f"Preview mockup for {title}"
    if kind == "family":
        config.show_article_type = True
        config.subtitle = f"Family baseline preview for {title}"
    overrides = JOURNAL_OVERRIDES.get(profile_slug, {})
    for key, value in overrides.items():
        setattr(config, key, value)
    return config


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def reference_block(style: str) -> str:
    if style == "author-year":
        return (
            r"\textbf{References.} "
            r"Smith and Lee (2024) Journal template adaptation. "
            r"\textit{Placeholder Journal} 12(3):101--114. "
            r"Garcia et al. (2025) Figure and table policy notes. "
            r"\textit{Template Review Letters} 4(1):1--9."
        )
    return (
        r"\textbf{References.} [1] A. Smith and B. Lee, "
        r"``Journal template adaptation,'' \textit{Placeholder Journal}, 2024. "
        r"[2] C. Garcia \textit{et al.}, ``Figure and table policy notes,'' 2025."
    )


def declaration_lines(config: LayoutConfig) -> list[str]:
    lines: list[str] = []
    if config.show_significance:
        lines.append(r"\textbf{Significance.} This placeholder preview emphasizes how a short editorial statement may appear near the front matter.")
    if config.show_specialty:
        lines.append(r"\textbf{Specialty Section.} Robotics and Autonomous Systems.")
    if config.show_correspondence:
        lines.append(r"\textbf{Correspondence.} corresponding.author@example.org")
    if config.show_data_availability:
        lines.append(r"\textbf{Data Availability.} Placeholder data and code would be linked here.")
    if config.show_author_contributions:
        lines.append(r"\textbf{Author Contributions.} Conceptualization, analysis, writing, and review are listed here as placeholders.")
    if config.show_competing_interests:
        lines.append(r"\textbf{Competing Interests.} The authors declare no competing interests in this simulated preview.")
    if config.show_declarations:
        lines.append(r"\textbf{Declarations.} Funding, ethics, and supplementary-material notices can appear in this area.")
    return lines


def build_ieee_preview_tex(title: str, profile_slug: str, kind: str, config: LayoutConfig) -> str:
    journal_focus = "Family baseline" if kind == "family" else "Specific journal profile"
    safe_title = latex_escape(title)
    safe_slug = latex_escape(profile_slug)
    safe_subtitle = latex_escape(config.subtitle)
    safe_focus = latex_escape(journal_focus)
    note_lines = list(config.notes)
    note_lines.insert(0, f"{title}: {config.subtitle}")
    note_lines.insert(1, f"Profile slug: {profile_slug} | Scope: {journal_focus}")
    note_text = " ".join(latex_escape(note) for note in note_lines)

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
\title{{{safe_title}\\\large Structured IEEE Journal Profile Preview}}
\author{{A. Placeholder, B. Example, and C. Template%
\thanks{{{safe_subtitle}.}}%
\thanks{{{note_text}}}}}
\begin{{document}}
\maketitle
\begin{{abstract}}
This IEEE profile preview uses a six-part engineering-paper skeleton so the page can be inspected as a realistic manuscript rather than as a loose formatting mockup. The text remains generic, but the layout now exposes how abstract, Index Terms, section hierarchy, figure placement, table placement, and references behave under the IEEE journal form.
\end{{abstract}}
\begin{{IEEEkeywords}}
IEEE profile preview, structured manuscript, abstract layout, figure placement, table placement
\end{{IEEEkeywords}}
\section{{Introduction}}
\IEEEPARstart{{T}}{{his}} profile preview is intended to show how a compact IEEE manuscript reads when the first page carries real section logic instead of isolated placeholder blocks. It gives the viewer a more honest way to judge title density, paragraph flow, and early technical framing.
\section{{Related Work}}
The related-work section is kept explicit in the preview library because it makes hierarchy and vertical rhythm easier to inspect. It also helps distinguish context-setting material from the method section that follows.
\section{{Methodology}}
The methodology section combines a short mathematical expression with a professional single-column figure placeholder so equation spacing, caption rhythm, and float placement can all be checked inside the two-column IEEE layout.
\begin{{equation}}
L = \sum_{{i=1}}^{{M}} \left( w_i \lVert y_i - \hat{{y}}_i \rVert_2^2 \right),
\end{{equation}}
where $y_i$ and $\hat{{y}}_i$ denote reference and estimated outputs, and $w_i$ denotes a placeholder weighting coefficient.
\begin{{figure}}[!t]
\centering
\fbox{{\parbox[c][2.0in][c]{{0.94\linewidth}}{{\centering Figure Placeholder\\[0.4em]\normalsize Architecture panel, sensing panel, or control pipeline}}}}
\caption{{Structured IEEE profile figure used to inspect caption spacing, one-column width, and how the first major float sits within the article body.}}
\label{{fig:profile-preview}}
\end{{figure}}
\section{{Experiments}}
The experiments section is expanded to make the preview easier to inspect at a glance and to provide a more realistic location for a compact quantitative table.
\begin{{table}}[!t]
\caption{{Quantitative summary for the {safe_focus.lower()} view of {safe_title}, arranged to inspect IEEE caption-first table treatment and metric readability.}}
\label{{tab:profile-preview}}
\centering
\begin{{tabular}}{{>{{\raggedright\arraybackslash}}p{{1.3in}}cc}}
\toprule
Method & Score & Latency \\
\midrule
Placeholder A & 0.91 & 14 ms \\
Placeholder B & 0.88 & 17 ms \\
Placeholder C & 0.84 & 20 ms \\
\bottomrule
\end{{tabular}}
\end{{table}}
Table~\ref{{tab:profile-preview}} and Fig.~\ref{{fig:profile-preview}} jointly make the preview page feel closer to a technical manuscript and less like a poster panel.
\section{{Conclusion and Discussion}}
{latex_escape(config.subtitle)}. Profile slug: {safe_slug}. Scope: {safe_focus}. Use the official journal instructions before submission, but use this preview to inspect whether the page already has the expected IEEE manuscript rhythm.
\begin{{thebibliography}}{{9}}
\bibitem{{ref1}} A. Smith and B. Lee, ``Journal template adaptation,'' \emph{{Placeholder Journal}}, 2024.
\bibitem{{ref2}} C. Garcia \emph{{et al.}}, ``Figure and table policy notes,'' 2025.
\bibitem{{ref3}} M. Turner and H. Wang, ``Structured two-column manuscript previews for engineering journals,'' 2026.
\end{{thebibliography}}
\end{{document}}
"""


def build_tex(title: str, profile_slug: str, family_slug: str, kind: str, config: LayoutConfig) -> str:
    body_columns_start = r"\begin{multicols}{2}" if config.columns == 2 else ""
    body_columns_end = r"\end{multicols}" if config.columns == 2 else ""
    title_begin = r"\begin{center}" if config.title_align == "center" else r"\begin{flushleft}"
    title_end = r"\end{center}" if config.title_align == "center" else r"\end{flushleft}"
    article_type = (
        r"\noindent{\color{" + config.accent_color + r"}\bfseries Article Type:} Placeholder Research Article\par\vspace{0.4em}"
        if config.show_article_type
        else ""
    )
    highlights = (
        r"\noindent\textbf{Highlights.} "
        r"Template-aware placeholder layout. "
        r"Figure and table spacing preview. "
        r"Journal-specific front-matter simulation.\par\vspace{0.5em}"
        if config.show_highlights
        else ""
    )
    graphical_abstract = (
        r"\noindent\textbf{Graphical Abstract.}\par"
        r"\begin{center}"
        r"\fcolorbox{black!55}{gray!12}{\begin{minipage}[c][2.4cm][c]{0.86\linewidth}\centering Graphical abstract placeholder\end{minipage}}"
        r"\end{center}\vspace{0.4em}"
        if config.show_graphical_abstract and config.columns == 1
        else ""
    )
    keywords = (
        r"\noindent\textbf{" + latex_escape(config.keywords_label) + r":} "
        r"placeholder manuscript, journal layout, figure slot, table slot, references.\par\vspace{0.6em}"
        if config.show_keywords
        else ""
    )
    ccs = (
        r"\noindent\textbf{CCS Concepts.} Computing methodologies; Applied computing; Document preparation.\par\vspace{0.4em}"
        if config.show_ccs
        else ""
    )
    declarations = "\n".join(r"\noindent " + line + r"\par" for line in declaration_lines(config))
    theorem_block = (
        r"\vspace{0.5em}\noindent\fcolorbox{black!55}{gray!8}{\parbox{0.96\linewidth}{"
        r"\textbf{Theorem 1.} Placeholder theorem-style block used to preview theorem-heavy journal layouts."
        r"}}\par\vspace{0.5em}"
        if config.show_theorem
        else ""
    )
    abstract_text = (
        "This simulated first-page preview uses placeholder text, a placeholder figure, and a placeholder table "
        "to visualize how a manuscript may look under the selected journal profile. "
        "The content is intentionally generic so attention stays on spacing, title treatment, abstract presentation, "
        "caption location, and the overall page rhythm."
    )
    if config.abstract_box:
        abstract_block = (
            r"\fcolorbox{black!45}{gray!8}{\begin{minipage}{0.96\linewidth}"
            r"\textbf{Abstract.} " + latex_escape(abstract_text) + r"\end{minipage}}\par\vspace{0.6em}"
        )
    else:
        abstract_block = r"\noindent\textbf{Abstract.} " + latex_escape(abstract_text) + r"\par\vspace{0.6em}"
    figure_caption = (
        r"\textbf{Figure 1.} Placeholder figure caption showing the expected caption style and relative spacing."
    )
    table_caption = (
        r"\textbf{Table 1.} Placeholder table caption showing metric labels and compact journal spacing."
    )
    figure_block = (
        (r"\noindent" + figure_caption + r"\par" if config.figure_caption_top else "")
        + r"\begin{center}"
        + r"\fcolorbox{black!60}{gray!10}{\begin{minipage}[c][2.25cm][c]{0.93\linewidth}"
        + r"\centering\Large Image Placeholder\\[0.4em]\normalsize Simulated figure area"
        + r"\end{minipage}}"
        + r"\end{center}"
        + (r"\noindent" + figure_caption + r"\par" if not config.figure_caption_top else "")
        + r"\vspace{0.5em}"
    )
    table_block = (
        (r"\noindent" + table_caption + r"\par" if config.table_caption_top else "")
        + r"\begin{center}"
        + "\n"
        + r"\begin{tabular}{lccc}"
        + "\n"
        + r"\toprule"
        + "\n"
        + r"Method & Score & Error & Time\\"
        + "\n"
        + r"\midrule"
        + "\n"
        + r"Placeholder A & 0.91 & 0.08 & 1.4\\"
        + "\n"
        + r"Placeholder B & 0.88 & 0.11 & 1.7\\"
        + "\n"
        + r"Placeholder C & 0.84 & 0.15 & 2.0\\"
        + "\n"
        + r"\bottomrule"
        + "\n"
        + r"\end{tabular}"
        + r"\end{center}"
        + (r"\noindent" + table_caption + r"\par" if not config.table_caption_top else "")
        + r"\vspace{0.5em}"
    )
    note_lines = r"\\ ".join(latex_escape(note) for note in config.notes)
    journal_focus = "Family baseline" if kind == "family" else "Specific journal profile"
    safe_title = latex_escape(title)
    safe_slug = latex_escape(profile_slug)
    safe_family = latex_escape(family_slug)
    safe_subtitle = latex_escape(config.subtitle)
    note_block = (
        r"\fcolorbox{black!45}{gray!6}{\begin{minipage}{0.98\linewidth}"
        + "\n"
        + r"\footnotesize "
        + note_lines
        + "\n"
        + r"\end{minipage}}"
    )

    return rf"""
\documentclass[10pt,{config.page_size}]{{article}}
\usepackage[margin=0.65in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{microtype}}
\usepackage{{multicol}}
\usepackage{{booktabs}}
\usepackage{{array}}
\usepackage{{amsmath}}
\usepackage[table]{{xcolor}}
\usepackage{{graphicx}}
\usepackage{{tikz}}
\usepackage{{hyperref}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.35em}}
\pagestyle{{empty}}
\definecolor{{accent}}{{named}}{{black}}
\begin{{document}}
{title_begin}
{{\{config.title_size}\bfseries {safe_title}}}\par
\vspace{{0.25em}}
{{\small Journal Manuscript Preview Library}}\par
\vspace{{0.15em}}
{{\footnotesize {safe_subtitle}}}\par
\vspace{{0.2em}}
{{\footnotesize Profile slug: {safe_slug} \quad Family: {safe_family} \quad Scope: {journal_focus}}}
{title_end}
\vspace{{0.2em}}
{article_type}
{highlights}
{graphical_abstract}
\noindent\textbf{{Authors.}} A. Placeholder, B. Example, and C. Template\par
\noindent\textbf{{Affiliations.}} Department of Simulated Formatting, Placeholder Institute\par
\noindent\textbf{{Contact.}} preview@example.org\par
\vspace{{0.4em}}
{abstract_block}
{keywords}
{ccs}
{body_columns_start}
{config.body_font_cmd}
\section*{{1. Introduction}}
This placeholder article body is intentionally structured as a compact submission-style manuscript so the rendered page is easier to inspect as a serious journal preview. The opening section focuses on how the title block, abstract, keywords, and first paragraphs combine into an overall page rhythm that resembles a practical submission rather than a poster-like mockup.

\section*{{2. Related Work}}
The related-work section is included even in starter previews because it makes the hierarchy more realistic and helps the reader judge whether literature framing, method description, and experimental content are clearly separated.

\section*{{3. Methodology}}
The methodology section introduces representative technical material so the preview can expose equation spacing, paragraph density, caption rhythm, and the visual balance of the first major figure.

\begin{{equation}}
\mathcal{{L}} = \sum_{{i=1}}^{{M}} w_i \left\| y_i - \hat{{y}}_i \right\|_2^2,
\end{{equation}}
where $y_i$ denotes a placeholder reference output, $\hat{{y}}_i$ denotes the estimated output, and $w_i$ denotes a weighting coefficient included only to simulate realistic notation.

{theorem_block}
{figure_block}

\section*{{4. Experiments}}
The experiments section is expanded so the preview can show a more realistic transition from methodology to quantitative evidence. This makes the resulting PNG materially easier to inspect for spacing, float handling, and table readability.
\textbf{{Experimental setup.}} This paragraph stands in for datasets, hardware conditions, baseline models, and protocol notes that are typically required before the main comparison table appears.

{table_block}

\textbf{{Quantitative discussion.}} The surrounding text exists to make the table feel integrated into a real manuscript page instead of floating as an isolated placeholder. It also lets the preview expose line lengths, caption spacing, and how the figure-table pair reads at a glance.

\section*{{5. Conclusion and Discussion}}
The final section is intentionally brief but still substantial enough to reveal whether the page closes cleanly after the main figure and table. The content remains generic by design, while the structure aims to make cross-journal layout comparison faster and more trustworthy.

{body_columns_end}
{declarations}
\section*{{6. References}}
\vspace{{0.5em}}
\noindent {reference_block(config.reference_style)}\par
\vspace{{0.6em}}
{note_block}
\end{{document}}
"""


def compile_preview(tex: str, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    tex_path = target_dir / "official_preview.tex"
    pdf_path = target_dir / "official_preview.pdf"
    png_base = target_dir / "official_preview"
    tex_path.write_text(tex, encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        work_tex = tmp_path / "official_preview.tex"
        work_tex.write_text(tex, encoding="utf-8")
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", str(work_tex.name)],
                cwd=tmp_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        shutil.copy2(tmp_path / "official_preview.pdf", pdf_path)
    subprocess.run(
        ["pdftocairo", "-png", "-singlefile", "-r", "180", str(pdf_path), str(png_base)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def generate_for_profile(profile_path: Path) -> None:
    verification_path = profile_path.parent / "verification.yaml"
    if verification_path.exists():
        verification_text = verification_path.read_text(encoding="utf-8")
        if 'status: "verified"' in verification_text:
            return
    kind, title, family_slug = read_profile_kind(profile_path)
    profile_slug = profile_path.parent.name
    config = build_layout(profile_slug, kind, family_slug, title)
    if family_slug == "ieee":
        tex = build_ieee_preview_tex(title, profile_slug, kind, config)
    else:
        tex = build_tex(title, profile_slug, family_slug, kind, config)
    compile_preview(tex, profile_path.parent)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render standardized official_preview assets for non-verified journal profile folders."
    )
    parser.add_argument(
        "--root",
        default=str(DEFAULT_JOURNALS_DIR),
        help="Root directory containing journal profile folders.",
    )
    parser.add_argument(
        "--include",
        nargs="*",
        default=[],
        help="Optional folder names to render. Defaults to every profile folder.",
    )
    args = parser.parse_args()
    root = Path(args.root)
    profile_paths = sorted(root.rglob("profile.md"))
    if args.include:
        profile_paths = [resolve_profile_dir(root, slug) / "profile.md" for slug in args.include]
    if not profile_paths:
        raise SystemExit("No profile.md files were found.")
    failures: list[str] = []
    for profile_path in profile_paths:
        try:
            generate_for_profile(profile_path)
            print(f"generated {profile_path.parent.name}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{profile_path.parent.name}: {exc}")
            print(f"failed {profile_path.parent.name}: {exc}")
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(f"\nRendered starter preview assets for {len(profile_paths)} profiles.")


if __name__ == "__main__":
    main()


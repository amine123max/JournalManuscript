#!/usr/bin/env python3
"""Create a family-level manuscript scaffold in the target workspace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

BUILD_ARTIFACT_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pag",
    ".run.xml",
    ".synctex.gz",
    ".toc",
    ".zip",
}
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    "PDF examples",
    "doc",
    "downloads",
    "thumbnails",
}
CITE_PATTERN = re.compile(
    r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)?(?:\[[^\]]*\]\s*)?\{([^}]+)\}"
)
BIB_KEY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)")


@dataclass(frozen=True)
class FamilyScaffoldConfig:
    family: str
    display_name: str
    source_root: Path
    sample_tex: Path
    official_source: str
    template_basis: str | None = None
    package_url: str | None = None
    bibliography_style: str | None = None
    sample_bib: Path | None = None
    materialize_command: tuple[str, ...] = ()


FAMILY_CONFIGS: dict[str, FamilyScaffoldConfig] = {
    "ieee": FamilyScaffoldConfig(
        family="ieee",
        display_name="IEEE Family",
        source_root=Path("assets/official-templates/ieee/template-package"),
        sample_tex=Path("bare_jrnl.tex"),
        official_source="https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/",
        package_url="https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip",
        bibliography_style="IEEEtran",
    ),
    "elsevier": FamilyScaffoldConfig(
        family="elsevier",
        display_name="Elsevier Family",
        source_root=Path("assets/official-templates/elsevier/elsarticle/elsarticle"),
        sample_tex=Path("elsarticle-template-num.tex"),
        official_source="https://www.elsevier.com/en-gb/researcher/author/policies-and-guidelines/latex-instructions",
        package_url="https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip",
        bibliography_style="elsarticle-num",
        materialize_command=("latex", "-interaction=nonstopmode", "elsarticle.ins"),
    ),
    "springer": FamilyScaffoldConfig(
        family="springer",
        display_name="Springer Family",
        source_root=Path(
            "assets/official-templates/springer/template-package/sn-article-template"
        ),
        sample_tex=Path("sn-article.tex"),
        official_source="https://www.springernature.com/gp/authors/campaigns/latex-author-support",
        package_url="https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12",
        sample_bib=Path("sn-bibliography.bib"),
    ),
    "frontiers": FamilyScaffoldConfig(
        family="frontiers",
        display_name="Frontiers Family",
        source_root=Path("assets/official-templates/frontiers"),
        sample_tex=Path("frontiers.tex"),
        official_source="https://www.frontiersin.org/design/zip/Frontiers_LaTeX_Templates.zip",
        package_url="https://www.frontiersin.org/design/zip/Frontiers_LaTeX_Templates.zip",
        sample_bib=Path("test.bib"),
    ),
    "plos": FamilyScaffoldConfig(
        family="plos",
        display_name="PLOS Family",
        source_root=Path("assets/official-templates/plos"),
        sample_tex=Path("plos_latex_template.tex"),
        official_source="https://journals.plos.org/plosone/s/latex",
        package_url="https://journals.plos.org/plosone/s/latex",
        sample_bib=Path("plos_bibtex_sample.bib"),
    ),
    "wiley": FamilyScaffoldConfig(
        family="wiley",
        display_name="Wiley Family",
        source_root=Path(
            "assets/official-templates/wiley/template-package/Optimal-Design-layout"
        ),
        sample_tex=Path("Optimal-Design-layout.tex"),
        official_source="https://authorservices.wiley.com/author-resources/Journal-Authors/Prepare/LaTeX/index.html",
        package_url="https://authors.wiley.com/asset/WileyDesign.zip",
        sample_bib=Path("wileyNJD-Chicago.bib"),
    ),
    "acs": FamilyScaffoldConfig(
        family="acs",
        display_name="ACS Family",
        source_root=Path("assets/official-templates/acs/template-package"),
        sample_tex=Path("achemso/achemso-demo.tex"),
        official_source="https://pubs.acs.org/page/4authors/submission/tex.html",
        package_url="https://mirrors.ctan.org/macros/latex/contrib/achemso.zip",
    ),
    "aip": FamilyScaffoldConfig(
        family="aip",
        display_name="AIP Family",
        source_root=Path("assets/official-templates/aip/template-package/revtex"),
        sample_tex=Path("sample/aip/aiptemplate.tex"),
        official_source="https://publishing.aip.org/resources/researchers/author-instructions/",
        package_url="https://mirrors.ctan.org/macros/latex/contrib/revtex.zip",
        sample_bib=Path("sample/aip/aipsamp.bib"),
    ),
    "oxford": FamilyScaffoldConfig(
        family="oxford",
        display_name="Oxford Family",
        source_root=Path(
            "assets/official-templates/oxford/journal-downloads/bioinformatics/template-package"
        ),
        sample_tex=Path("oup-authoring-template.tex"),
        official_source="https://academic.oup.com/journals/pages/authors/preparing_your_manuscript",
        template_basis=(
            "Representative family baseline derived from the cached Bioinformatics "
            "OUP template package."
        ),
        package_url="https://mirrors.ctan.org/macros/latex/contrib/oup-authoring-template.zip",
        sample_bib=Path("reference.bib"),
    ),
    "cambridge": FamilyScaffoldConfig(
        family="cambridge",
        display_name="Cambridge Family",
        source_root=Path(
            "assets/official-templates/cambridge/journal-downloads/journal-of-fluid-mechanics/template-package"
        ),
        sample_tex=Path("FLMguide.tex"),
        official_source="https://www.cambridge.org/core/services/authors/journals/journal-layout-and-templates",
        template_basis=(
            "Representative family baseline derived from the cached Journal of Fluid "
            "Mechanics Cambridge template package."
        ),
        package_url="https://www.cambridge.org/core/services/aop-file-manager/file/6336d49bb048e80011023dc6/JFM-FLM-AUTemplate.zip",
        sample_bib=Path("jfm.bib"),
    ),
    "sage": FamilyScaffoldConfig(
        family="sage",
        display_name="SAGE Family",
        source_root=Path(
            "assets/official-templates/sage/journal-downloads/transactions-of-the-institute-of-measurement-and-control/template-package"
        ),
        sample_tex=Path("Sage_LaTeX_Guidelines.tex"),
        official_source="https://journals.sagepub.com/author-instructions",
        template_basis=(
            "Representative family baseline derived from the cached Transactions of "
            "the Institute of Measurement and Control SAGE template package."
        ),
        package_url="https://uk.sagepub.com/sites/default/files/sage_latex_template_4.zip",
    ),
    "optica-publishing": FamilyScaffoldConfig(
        family="optica-publishing",
        display_name="Optica Publishing Group Family",
        source_root=Path(
            "assets/official-templates/optica-publishing/journal-downloads/applied-optics/template-package"
        ),
        sample_tex=Path("Optica-template.tex"),
        official_source="https://opg.optica.org/submit/templates/default.cfm",
        template_basis=(
            "Representative family baseline derived from the cached Applied Optics "
            "Optica template package."
        ),
        package_url="https://opg.optica.org/resources/author/templates/latex-universal-template.zip",
        sample_bib=Path("sample.bib"),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a family-level manuscript scaffold that matches the selected "
            "publisher template baseline."
        )
    )
    parser.add_argument("--family", required=True, help="Family slug to scaffold.")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Workspace directory where the scaffold should be created.",
    )
    parser.add_argument(
        "--paper-dir-name",
        default="paper",
        help="Name of the paper directory to create under the output workspace.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing paper directory.",
    )
    return parser.parse_args()


def available_family_configs() -> dict[str, FamilyScaffoldConfig]:
    return {
        slug: config
        for slug, config in FAMILY_CONFIGS.items()
        if (ROOT / config.source_root).exists()
    }


def supported_families_text() -> str:
    return ", ".join(sorted(available_family_configs()))


def read_text_with_fallback(path: Path) -> str:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
        return True
    name = path.name
    if name.endswith(".synctex.gz"):
        return True
    return path.suffix.lower() in BUILD_ARTIFACT_SUFFIXES


def is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def copy_tree_filtered(source_root: Path, destination_root: Path) -> None:
    stack = [source_root]
    while stack:
        current = stack.pop()
        for source in sorted(current.iterdir(), key=lambda path: path.name.lower()):
            relative = source.relative_to(source_root)
            if should_skip(relative):
                continue
            if is_reparse_point(source):
                continue
            target = destination_root / relative
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                stack.append(source)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def normalize_bibliography(text: str, config: FamilyScaffoldConfig) -> str:
    updated = text
    updated = re.sub(
        r"\\bibliography\{[^}]+\}",
        lambda _: r"\bibliography{references}",
        updated,
    )

    if config.family in {"ieee", "elsevier"}:
        bibliography_commands = ["\\bibliography{references}"]
        if config.bibliography_style:
            bibliography_commands.insert(
                0, f"\\bibliographystyle{{{config.bibliography_style}}}"
            )
        replacement = "\n".join(bibliography_commands)
        updated, count = re.subn(
            r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
            lambda _: replacement,
            updated,
            count=1,
            flags=re.DOTALL,
        )
        if count == 0 and "\\bibliography{references}" not in updated:
            updated = re.sub(
                r"\\end\{document\}",
                lambda _: replacement + "\n\n\\end{document}",
                updated,
                count=1,
            )
    elif "\\bibliography{references}" not in updated:
        updated = re.sub(
            r"\\end\{document\}",
            lambda _: "\\bibliography{references}\n\n\\end{document}",
            updated,
            count=1,
        )
    return updated


def extract_citation_keys(text: str) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for match in CITE_PATTERN.finditer(text):
        for raw_key in match.group(1).split(","):
            key = raw_key.strip().lstrip("*")
            if not key or key in seen:
                continue
            seen.add(key)
            keys.append(key)
    return keys


def extract_existing_bib_keys(text: str) -> set[str]:
    return {match.group(1).strip() for match in BIB_KEY_PATTERN.finditer(text)}


def placeholder_bib_entry(key: str) -> str:
    safe_key = key or "placeholder2026"
    return "\n".join(
        [
            f"@article{{{safe_key},",
            "  author = {Template Author},",
            f"  title = {{{safe_key} placeholder reference}},",
            "  journal = {Template Journal},",
            "  year = {2026}",
            "}",
            "",
        ]
    )


def load_or_create_bibliography(
    config: FamilyScaffoldConfig,
    paper_dir: Path,
    main_tex: str,
) -> None:
    references_path = paper_dir / "references.bib"
    if config.sample_bib:
        source_bib = ROOT / config.source_root / config.sample_bib
        references_text = source_bib.read_text(encoding="utf-8")
    else:
        references_text = ""

    cited_keys = extract_citation_keys(main_tex)
    existing_keys = extract_existing_bib_keys(references_text)
    missing_keys = [key for key in cited_keys if key not in existing_keys]

    if not references_text.strip() and not cited_keys:
        missing_keys = ["placeholder2026"]

    if references_text and not references_text.endswith("\n"):
        references_text += "\n"
    if missing_keys:
        references_text += "".join(placeholder_bib_entry(key) for key in missing_keys)

    references_path.write_text(references_text, encoding="utf-8")


def write_caption_bank(paper_dir: Path, family: str) -> None:
    content = "\n".join(
        [
            "# Caption Bank",
            "",
            f"- Family baseline: `{family}`",
            "- Keep captions factual, compact, and manuscript-oriented.",
            "- Note what is shown, what varies, and what the reader should compare.",
            "",
            "## Figure Caption Starters",
            "",
            "- Overview of the proposed framework and its main processing stages.",
            "- Qualitative comparison across representative operating conditions.",
            "- Sensitivity of the method to key configuration parameters.",
            "",
            "## Table Caption Starters",
            "",
            "- Quantitative comparison against representative baselines.",
            "- Ablation study showing the contribution of each design component.",
            "- Dataset or scenario summary used in the evaluation pipeline.",
            "",
        ]
    )
    (paper_dir / "CAPTION_BANK.md").write_text(content, encoding="utf-8")


def write_readme_paper(
    config: FamilyScaffoldConfig,
    paper_dir: Path,
    *,
    materialization_note: str,
) -> None:
    lines = [
        "# Paper Workspace Notes",
        "",
        f"- Family scaffold: `{config.family}` ({config.display_name})",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Source template root: `{config.source_root.as_posix()}`",
        f"- Sample entry used: `{config.sample_tex.as_posix()}`",
        f"- Official guide page: {config.official_source}",
        (
            f"- Template basis: {config.template_basis}"
            if config.template_basis
            else "- Template basis: reusable family-wide official package root."
        ),
        "",
        "## Expected Files",
        "",
        "- `main.tex`: active manuscript entry file",
        "- `references.bib`: bibliography database",
        "- `CAPTION_BANK.md`: caption drafting notes",
        "- `figures/`: manuscript figures",
        "- `tables/`: manuscript tables",
        "- `tables/generated/`: generated table outputs",
        "",
        "## Compile",
        "",
        "```powershell",
        "pdflatex main.tex",
        "bibtex main",
        "pdflatex main.tex",
        "pdflatex main.tex",
        "```",
        "",
        "## Skill Usage",
        "",
        f"- Family baseline prompt: `Use $journal-manuscript with journal={config.family} task=\"Turn this family scaffold into a clean manuscript draft.\"`",
        f"- Journal-specific refinement prompt: `Use $journal-manuscript with journal=<journal-slug> task=\"Tighten this family scaffold toward the target journal.\"`",
        "",
        "## Notes",
        "",
        "- `main.tex` keeps the official sample structure as the writing baseline. Replace vendor demo prose section by section instead of rewriting everything in one pass.",
        f"- Official template download: {config.package_url or config.official_source}",
        f"- {materialization_note}",
        "",
    ]
    (paper_dir / "README_PAPER.md").write_text("\n".join(lines), encoding="utf-8")


def write_family_manifest(config: FamilyScaffoldConfig, paper_dir: Path) -> None:
    payload = {
        "family": config.family,
        "display_name": config.display_name,
        "source_root": config.source_root.as_posix(),
        "sample_tex": config.sample_tex.as_posix(),
        "official_source": config.official_source,
        "template_basis": config.template_basis
        or "reusable family-wide official package root",
        "package_url": config.package_url or config.official_source,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (paper_dir / "family-scaffold.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def ensure_workspace_dirs(paper_dir: Path) -> None:
    (paper_dir / "figures").mkdir(parents=True, exist_ok=True)
    (paper_dir / "tables").mkdir(parents=True, exist_ok=True)
    (paper_dir / "tables" / "generated").mkdir(parents=True, exist_ok=True)
    (paper_dir / "_reference_pages").mkdir(parents=True, exist_ok=True)
    (paper_dir / "figures" / "README.md").write_text(
        "# Figures\n\nPlace manuscript figures for the active family scaffold here.\n",
        encoding="utf-8",
    )
    (paper_dir / "tables" / "README.md").write_text(
        "# Tables\n\nPlace hand-authored table files for the active family scaffold here.\n",
        encoding="utf-8",
    )
    (paper_dir / "tables" / "generated" / "README.md").write_text(
        "# Generated Tables\n\nPlace generated table outputs here when the manuscript workflow needs them.\n",
        encoding="utf-8",
    )


def materialize_template_assets(
    config: FamilyScaffoldConfig, paper_dir: Path
) -> str:
    if not config.materialize_command:
        return "No extra template materialization step was required."

    executable = shutil.which(config.materialize_command[0])
    if executable is None:
        return (
            f"Optional materialization step skipped because `{config.materialize_command[0]}` "
            "is not available in this environment."
        )

    command = [executable, *config.materialize_command[1:]]
    try:
        subprocess.run(
            command,
            cwd=paper_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return (
            f"Materialized additional template assets by running "
            f"`{' '.join(config.materialize_command)}`."
        )
    except subprocess.CalledProcessError as exc:
        return (
            f"Materialization step `{' '.join(config.materialize_command)}` failed "
            f"with exit code {exc.returncode}; source files were still copied."
        )


def scaffold_family(config: FamilyScaffoldConfig, paper_dir: Path) -> None:
    source_root = ROOT / config.source_root
    copy_tree_filtered(source_root, paper_dir)

    copied_sample = paper_dir / config.sample_tex
    main_tex = read_text_with_fallback(copied_sample)
    main_tex = normalize_bibliography(main_tex, config)
    main_tex = (
        f"% Family scaffold generated from {config.display_name}\n"
        "% Replace vendor sample prose progressively while preserving the template structure.\n\n"
        + main_tex
    )
    (paper_dir / "main.tex").write_text(main_tex, encoding="utf-8")

    if copied_sample.exists() and copied_sample != paper_dir / "main.tex":
        copied_sample.unlink()

    if config.sample_bib:
        copied_bib = paper_dir / config.sample_bib
        if copied_bib.exists() and copied_bib != paper_dir / "references.bib":
            copied_bib.unlink()

    ensure_workspace_dirs(paper_dir)
    write_caption_bank(paper_dir, config.family)
    load_or_create_bibliography(config, paper_dir, main_tex)
    materialization_note = materialize_template_assets(config, paper_dir)
    write_readme_paper(config, paper_dir, materialization_note=materialization_note)
    write_family_manifest(config, paper_dir)


def main() -> None:
    args = parse_args()
    family = args.family.strip().lower()
    available_configs = available_family_configs()
    config = available_configs.get(family)
    if config is None:
        if family in FAMILY_CONFIGS:
            raise SystemExit(
                f"Family scaffold assets for `{family}` are not installed in this package. "
                f"Available families: {supported_families_text()}"
            )
        raise SystemExit(
            f"Unsupported family scaffold: {family}. Supported families: {supported_families_text()}"
        )

    output_dir = Path(args.output_dir).expanduser().resolve()
    paper_dir = output_dir / args.paper_dir_name
    if paper_dir.exists():
        if not args.force:
            raise SystemExit(
                f"Target paper directory already exists: {paper_dir}. Use --force to replace it."
            )
        shutil.rmtree(paper_dir)
    paper_dir.mkdir(parents=True, exist_ok=True)

    scaffold_family(config, paper_dir)
    print(f"created family scaffold at {paper_dir}")


if __name__ == "__main__":
    main()

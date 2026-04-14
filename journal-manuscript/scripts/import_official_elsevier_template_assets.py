#!/usr/bin/env python3
"""Import official Elsevier LaTeX template assets into the repository.

This script downloads the official Elsevier LaTeX instruction packages used by
the journal-profile library and extracts them under
`assets/official-templates/elsevier/`.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSET_ROOT = ROOT / "assets" / "official-templates" / "elsevier"

ELSEVIER_LATEX_SOURCE = "https://www.elsevier.com/en-gb/researcher/author/policies-and-guidelines/latex-instructions"
PACKAGE_SPECS = [
    {
        "name": "elsarticle",
        "url": "https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip",
        "archive_name": "elsarticle.zip",
        "extract_dir": "elsarticle",
    },
    {
        "name": "els-cas-templates",
        "url": "https://assets.ctfassets.net/o78em1y1w4i4/5uFmLZJTPDMAUjFnHRpjj8/6f19a979146eb93263763d87a894ab0d/els-cas-templates.zip",
        "archive_name": "els-cas-templates.zip",
        "extract_dir": "els-cas-templates",
    },
]


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def extract(archive_path: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)


def write_readme(asset_root: Path) -> None:
    readme = asset_root / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Elsevier Official Template Assets",
                "",
                "These assets are imported from Elsevier's official LaTeX instructions page:",
                "",
                f"- Source page: {ELSEVIER_LATEX_SOURCE}",
                "",
                "## Imported Packages",
                "",
                "- `elsarticle.zip`: official Elsevier journal article package used for standard author manuscripts.",
                "- `els-cas-templates.zip`: official Elsevier CAS single-column and double-column package bundle for journals that use the CAS family.",
                "",
                "## Local Paths",
                "",
                "- `assets/official-templates/elsevier/elsarticle/elsarticle/`",
                "- `assets/official-templates/elsevier/els-cas-templates/els-cas-templates/`",
                "",
                "## Current Display Mapping",
                "",
                "- `ocean-engineering`: `elsarticle-template-harv.tex`",
                "- `applied-soft-computing`: `elsarticle-template-num.tex`",
                "- `measurement`: `elsarticle-template-num.tex`",
                "",
                "Use the target journal's live Guide for Authors together with these imported assets before calling a manuscript submission-ready.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and extract official Elsevier LaTeX template assets."
    )
    parser.add_argument(
        "--asset-root",
        default=str(DEFAULT_ASSET_ROOT),
        help="Destination root for imported Elsevier template assets.",
    )
    args = parser.parse_args()
    asset_root = Path(args.asset_root)
    downloads_dir = asset_root / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    for spec in PACKAGE_SPECS:
        archive_path = downloads_dir / spec["archive_name"]
        extract_dir = asset_root / spec["extract_dir"]
        print(f"downloading {spec['name']}")
        download(spec["url"], archive_path)
        print(f"extracting {spec['name']}")
        extract(archive_path, extract_dir)

    write_readme(asset_root)
    print("Elsevier official template assets imported successfully.")


if __name__ == "__main__":
    main()

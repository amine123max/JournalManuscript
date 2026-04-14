#!/usr/bin/env python3
"""Build a slim journal-manuscript skill bundle for selected journals or families."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from scaffold_family_manuscript import FAMILY_CONFIGS


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "dist"
JOURNALS_DIR = ROOT / "references" / "journals"
SCAFFOLD_READY_FAMILIES = tuple(sorted(FAMILY_CONFIGS))
REPO_FILES = [
    Path("LICENSE"),
]

CORE_FILES = [
    Path("SKILL.md"),
    Path("agents/README.md"),
    Path("agents/anthropic.yaml"),
    Path("agents/gemini.yaml"),
    Path("agents/local-llm.yaml"),
    Path("agents/openai.yaml"),
    Path("agents/openrouter.yaml"),
    Path("agents/provider-portability.yaml"),
    Path("agents/shared-journal-loading.yaml"),
    Path("references/house-style.md"),
    Path("references/journal-profiles.md"),
    Path("references/journals/family-template-sharing-tiers.md"),
    Path("references/journals/family-template-sharing-tiers.yaml"),
    Path("scripts/README.md"),
    Path("scripts/export_selective_skill_bundle.py"),
    Path("scripts/scaffold_family_manuscript.py"),
]

ASSET_PATTERNS = [
    re.compile(r"`(assets/official-templates/[^`]+)`"),
    re.compile(r'"(assets/official-templates/[^"]+)"'),
    re.compile(r"(assets/official-templates/[A-Za-z0-9._/\-]+)"),
]
PARENT_FAMILY_PATTERN = re.compile(r"Start from:\s+\.\./([^/]+)/profile\.md")
HEADING_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class ProfileRecord:
    slug: str
    display_name: str
    profile_dir: Path


def relative_profile_dir(profile_dir: Path) -> Path:
    return profile_dir.relative_to(ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export a slim journal-manuscript skill bundle that contains only "
            "the selected journal or family profiles and template assets."
        )
    )
    parser.add_argument(
        "--journal",
        action="append",
        default=[],
        help="Journal slug to include. May be repeated.",
    )
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        help=(
            "Family slug to include. A family export also includes all child "
            "journal profiles that inherit from that family. May be repeated."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the slim bundle folder should be created.",
    )
    parser.add_argument(
        "--bundle-name",
        default="",
        help="Optional custom name for the generated bundle folder.",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Also create a zip archive next to the generated bundle folder.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing bundle folder or archive of the same name.",
    )
    return parser.parse_args()


def unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def resolve_profile_dir(slug: str) -> Path:
    direct = JOURNALS_DIR / slug
    if direct.is_dir():
        return direct
    matches = [path.parent for path in JOURNALS_DIR.rglob("profile.md") if path.parent.name == slug]
    if not matches:
        raise FileNotFoundError(f"Unknown journal or family slug: {slug}")
    if len(matches) > 1:
        raise FileNotFoundError(f"Ambiguous journal or family slug: {slug}")
    return matches[0]


def profile_dir_for(slug: str) -> Path:
    profile_dir = resolve_profile_dir(slug)
    profile_path = profile_dir / "profile.md"
    if not profile_path.is_file():
        raise FileNotFoundError(f"Missing profile.md for slug: {slug}")
    return profile_dir


def extract_display_name(profile_dir: Path, slug: str) -> str:
    text = (profile_dir / "profile.md").read_text(encoding="utf-8")
    match = HEADING_PATTERN.search(text)
    if not match:
        return slug
    heading = match.group(1).strip()
    if heading.endswith(" Profile"):
        return heading[: -len(" Profile")]
    return heading


def extract_parent_family_slug(profile_dir: Path) -> str | None:
    text = (profile_dir / "profile.md").read_text(encoding="utf-8")
    match = PARENT_FAMILY_PATTERN.search(text)
    if not match:
        return None
    return match.group(1).strip()


def collect_profile_record(slug: str) -> ProfileRecord:
    profile_dir = profile_dir_for(slug)
    return ProfileRecord(
        slug=slug,
        display_name=extract_display_name(profile_dir, slug),
        profile_dir=profile_dir,
    )


def child_journal_records_for_family(family_slug: str) -> list[ProfileRecord]:
    family_dir = resolve_profile_dir(family_slug)
    children: list[ProfileRecord] = []
    for profile_dir in sorted(path.parent for path in JOURNALS_DIR.rglob("profile.md") if path.parent != family_dir):
        slug = profile_dir.name
        if extract_parent_family_slug(profile_dir) != family_slug:
            continue
        children.append(
            ProfileRecord(
                slug=slug,
                display_name=extract_display_name(profile_dir, slug),
                profile_dir=profile_dir,
            )
        )
    return children


def extract_asset_paths_from_text(text: str) -> list[Path]:
    matches: set[str] = set()
    for pattern in ASSET_PATTERNS:
        for raw_match in pattern.findall(text):
            cleaned = raw_match.strip().rstrip("/")
            if cleaned:
                matches.add(cleaned)
    return [Path(item) for item in sorted(matches)]


def referenced_assets_for_profile(
    profile_dir: Path,
    *,
    guides_only: bool,
) -> tuple[list[Path], list[str]]:
    discovered: list[Path] = []
    missing: list[str] = []
    for file_name in ("profile.md", "verification.yaml"):
        candidate = profile_dir / file_name
        if not candidate.is_file():
            continue
        for asset_path in extract_asset_paths_from_text(
            candidate.read_text(encoding="utf-8")
        ):
            asset_text = asset_path.as_posix()
            if guides_only and "/guides/" not in asset_text:
                continue
            source = ROOT / asset_path
            if source.exists():
                discovered.append(asset_path)
            else:
                missing.append(asset_text)
    return unique_relative_paths(discovered), sorted(set(missing))


def unique_relative_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    ordered: list[Path] = []
    for path in paths:
        key = path.as_posix()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def default_bundle_name(journals: list[str], families: list[str]) -> str:
    parts = journals + [f"family-{slug}" for slug in families if slug not in journals]
    if not parts:
        return "journal-manuscript-slim"
    if len(parts) > 3:
        tail = "-".join(parts[:3]) + "-and-more"
    else:
        tail = "-".join(parts)
    return f"journal-manuscript-{tail}"


def prepare_bundle_root(bundle_root: Path, *, force: bool) -> None:
    if bundle_root.exists():
        if not force:
            raise FileExistsError(
                f"Bundle output already exists: {bundle_root}. Use --force to replace it."
            )
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True, exist_ok=True)


def windows_safe_path(path: Path) -> str:
    resolved = str(path.resolve())
    if resolved.startswith("\\\\?\\") or resolved.startswith("\\\\"):
        return resolved
    if Path(resolved).is_absolute():
        return "\\\\?\\" + resolved
    return resolved


def copy_relative_path(relative_path: Path, destination_root: Path) -> None:
    source = ROOT / relative_path
    destination = destination_root / relative_path
    if source.is_dir():
        shutil.copytree(
            windows_safe_path(source),
            windows_safe_path(destination),
            dirs_exist_ok=True,
        )
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(windows_safe_path(source), windows_safe_path(destination))


def copy_repo_relative_path(relative_path: Path, destination_root: Path) -> None:
    source = REPO_ROOT / relative_path
    destination = destination_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(windows_safe_path(source), windows_safe_path(destination))


def write_bundle_manifest(
    bundle_root: Path,
    *,
    journals: list[ProfileRecord],
    families: list[ProfileRecord],
    asset_paths: list[Path],
    missing_assets: list[str],
) -> None:
    scaffold_ready_family_slugs = [
        record.slug for record in families if record.slug in SCAFFOLD_READY_FAMILIES
    ]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bundle_type": "journal-manuscript-slim",
        "included_journals": [
            {
                "slug": record.slug,
                "display_name": record.display_name,
                "relative_path": relative_profile_dir(record.profile_dir).as_posix(),
            }
            for record in journals
        ],
        "included_families": [
            {
                "slug": record.slug,
                "display_name": record.display_name,
                "relative_path": relative_profile_dir(record.profile_dir).as_posix(),
            }
            for record in families
        ],
        "included_scaffold_ready_families": scaffold_ready_family_slugs,
        "included_asset_paths": [path.as_posix() for path in asset_paths],
        "missing_asset_references": missing_assets,
    }
    (bundle_root / "bundle-manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_bundle_readmes(
    bundle_root: Path,
    *,
    journals: list[ProfileRecord],
    families: list[ProfileRecord],
) -> None:
    journal_lines = [
        f"- `{relative_profile_dir(record.profile_dir).relative_to(Path('references/journals')).as_posix()}/`: {record.display_name} (`slug: {record.slug}`)"
        for record in journals
    ] or ["- none"]
    family_lines = [
        f"- `{relative_profile_dir(record.profile_dir).relative_to(Path('references/journals')).as_posix()}/`: {record.display_name} (`slug: {record.slug}`)"
        for record in families
    ] or ["- none"]
    scaffold_lines = [
        f"- `{record.slug}`: one-click `paper/` scaffold available via `python journal-manuscript/scripts/scaffold_family_manuscript.py --family {record.slug} --output-dir <workspace>`"
        for record in families
        if record.slug in SCAFFOLD_READY_FAMILIES
    ] or ["- none in this package"]

    english = [
        "# Journal Manuscript Minimal Package",
        "",
        "This package is a minimal distribution for a selected journal or publisher family.",
        "",
        "It contains the installable `journal-manuscript/` skill package, the included family and journal profiles, and the required guide or template assets referenced by those profiles.",
        "",
        "## Included Journals",
        "",
        *journal_lines,
        "",
        "## Included Families",
        "",
        *family_lines,
        "",
        "## Family Scaffold Support",
        "",
        *scaffold_lines,
        "",
        "## Installation",
        "",
        "Copy the inner `journal-manuscript/` folder into your Codex skills directory:",
        "",
        "- Windows: `C:\\Users\\<username>\\.codex\\skills\\journal-manuscript`",
        "- macOS/Linux: `~/.codex/skills/journal-manuscript`",
        "",
        "The installed package includes native Codex/OpenAI support plus compatibility configs for Claude, Gemini, OpenRouter, and local LLM wrappers under `journal-manuscript/agents/`.",
        "",
        "License: MIT. See `LICENSE` at the package root.",
        "",
        "This package supports only the journals and family profiles listed above.",
        "",
        "See `bundle-manifest.json` for the exact exported scope.",
        "",
        "Generated by `journal-manuscript/scripts/export_selective_skill_bundle.py`.",
        "",
    ]
    chinese = [
        "# Journal Manuscript 最小精简包",
        "",
        "这个包是面向指定期刊或出版社 family 的最小分发单元。",
        "",
        "它包含可安装的 `journal-manuscript/` skill 包、当前包内包含的 family 与 journal profile，以及这些 profile 所引用的 guide 或模板资产。",
        "",
        "## 已包含的期刊",
        "",
        *journal_lines,
        "",
        "## 已包含的家族",
        "",
        *family_lines,
        "",
        "## Family 脚手架支持",
        "",
        *scaffold_lines,
        "",
        "## 安装方式",
        "",
        "将内部的 `journal-manuscript/` 文件夹复制到你的 Codex skill 目录：",
        "",
        "- Windows：`C:\\Users\\<你的用户名>\\.codex\\skills\\journal-manuscript`",
        "- macOS/Linux：`~/.codex/skills/journal-manuscript`",
        "",
        "安装后的包同时包含原生 Codex/OpenAI 配置，以及 `journal-manuscript/agents/` 下的 Claude、Gemini、OpenRouter 和本地 LLM 包装层兼容配置。",
        "",
        "协议：MIT。请查看包根目录下的 `LICENSE`。",
        "",
        "这个包只支持上面列出的期刊和 family profile。",
        "",
        "精确导出范围请查看 `bundle-manifest.json`。",
        "",
        "由 `journal-manuscript/scripts/export_selective_skill_bundle.py` 生成。",
        "",
    ]
    (bundle_root / "README.md").write_text("\n".join(english), encoding="utf-8")
    (bundle_root / "README.zh-CN.md").write_text(
        "\n".join(chinese), encoding="utf-8"
    )


def write_subset_journal_docs(
    destination_root: Path,
    *,
    journals: list[ProfileRecord],
    families: list[ProfileRecord],
) -> None:
    journals_dir = destination_root / "references" / "journals"
    journals_dir.mkdir(parents=True, exist_ok=True)

    family_lines = [
        f"- `{relative_profile_dir(record.profile_dir).relative_to(Path('references/journals')).as_posix()}/`: {record.display_name}"
        for record in families
    ] or ["- none"]
    journal_lines = [
        f"- `{relative_profile_dir(record.profile_dir).relative_to(Path('references/journals')).as_posix()}/`: {record.display_name}"
        for record in journals
    ] or ["- none"]

    catalog_lines = [
        "# Journal Profile Catalog",
        "",
        "This is a slim catalog generated for a selective journal-manuscript bundle.",
        "",
        "## Included Family Profiles",
        "",
        *family_lines,
        "",
        "## Included Journal Profiles",
        "",
        *journal_lines,
        "",
        "Use the full repository if you need additional journals or publisher families.",
        "",
    ]
    readme_lines = [
        "# Journal Folders",
        "",
        "This slim bundle keeps only the profiles needed for the selected journals.",
        "",
        "## Included Families",
        "",
        *family_lines,
        "",
        "## Included Journals",
        "",
        *journal_lines,
        "",
        "If a journal is missing, rebuild the bundle from the full repository with the needed slug.",
        "",
    ]
    (journals_dir / "catalog.md").write_text(
        "\n".join(catalog_lines), encoding="utf-8"
    )
    (journals_dir / "README.md").write_text(
        "\n".join(readme_lines), encoding="utf-8"
    )


def create_zip_archive(bundle_root: Path, *, force: bool) -> Path:
    archive_path = bundle_root.with_suffix(".zip")
    if archive_path.exists():
        if not force:
            raise FileExistsError(
                f"Archive already exists: {archive_path}. Use --force to replace it."
            )
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(bundle_root.rglob("*")):
            handle.write(path, path.relative_to(bundle_root.parent))
    return archive_path


def required_scaffold_assets_for_families(family_slugs: list[str]) -> list[Path]:
    required: list[Path] = []
    for slug in family_slugs:
        config = FAMILY_CONFIGS.get(slug)
        if not config:
            continue
        required.append(config.source_root)
    return unique_relative_paths(required)


def main() -> None:
    args = parse_args()
    requested_journals = unique_preserve(args.journal)
    requested_families = unique_preserve(args.family)
    if not requested_journals and not requested_families:
        raise SystemExit("Select at least one --journal or --family slug.")

    journal_records_by_slug: dict[str, ProfileRecord] = {}
    family_records_by_slug: dict[str, ProfileRecord] = {}
    included_profile_dirs: list[Path] = []
    asset_paths: list[Path] = []
    missing_assets: list[str] = []

    for slug in requested_families:
        family_record = collect_profile_record(slug)
        family_records_by_slug[slug] = family_record
        for child_record in child_journal_records_for_family(slug):
            journal_records_by_slug.setdefault(child_record.slug, child_record)

    for slug in requested_journals:
        record = collect_profile_record(slug)
        journal_records_by_slug.setdefault(slug, record)
        parent_family_slug = extract_parent_family_slug(record.profile_dir)
        if parent_family_slug:
            family_records_by_slug.setdefault(
                parent_family_slug, collect_profile_record(parent_family_slug)
            )

    journal_records = sorted(
        journal_records_by_slug.values(),
        key=lambda record: record.slug,
    )

    for record in journal_records:
        included_profile_dirs.append(relative_profile_dir(record.profile_dir))
        journal_assets, journal_missing = referenced_assets_for_profile(
            record.profile_dir,
            guides_only=False,
        )
        asset_paths.extend(journal_assets)
        missing_assets.extend(journal_missing)

    for record in family_records_by_slug.values():
        included_profile_dirs.append(relative_profile_dir(record.profile_dir))

        guides_only = record.slug not in requested_families
        family_assets, family_missing = referenced_assets_for_profile(
            record.profile_dir,
            guides_only=guides_only,
        )
        asset_paths.extend(family_assets)
        missing_assets.extend(family_missing)

    asset_paths = unique_relative_paths(asset_paths)
    asset_paths.extend(required_scaffold_assets_for_families(requested_families))
    asset_paths = unique_relative_paths(asset_paths)
    missing_assets = sorted(set(missing_assets))

    output_dir = Path(args.output_dir).expanduser().resolve()
    bundle_name = args.bundle_name.strip() or default_bundle_name(
        requested_journals,
        requested_families,
    )
    bundle_root = output_dir / bundle_name
    prepare_bundle_root(bundle_root, force=args.force)

    for relative_path in REPO_FILES:
        copy_repo_relative_path(relative_path, bundle_root)

    destination_skill_root = bundle_root / "journal-manuscript"
    destination_skill_root.mkdir(parents=True, exist_ok=True)

    for relative_path in CORE_FILES:
        copy_relative_path(relative_path, destination_skill_root)

    for relative_dir in unique_relative_paths(included_profile_dirs):
        copy_relative_path(relative_dir, destination_skill_root)

    for asset_path in asset_paths:
        copy_relative_path(asset_path, destination_skill_root)

    family_records = sorted(
        family_records_by_slug.values(),
        key=lambda record: record.slug,
    )
    write_subset_journal_docs(
        destination_skill_root,
        journals=journal_records,
        families=family_records,
    )
    write_bundle_manifest(
        bundle_root,
        journals=journal_records,
        families=family_records,
        asset_paths=asset_paths,
        missing_assets=missing_assets,
    )
    write_bundle_readmes(
        bundle_root,
        journals=journal_records,
        families=family_records,
    )

    print(f"created bundle at {bundle_root}")
    if args.archive:
        archive_path = create_zip_archive(bundle_root, force=args.force)
        print(f"created archive at {archive_path}")
    if missing_assets:
        print("missing asset references:")
        for asset in missing_assets:
            print(f"  - {asset}")


if __name__ == "__main__":
    main()

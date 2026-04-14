#!/usr/bin/env python3
"""Download official guide-source files for all verification targets.

The script reads every `verification.yaml` under `references/journals/`
and downloads the corresponding `official_source` into
`assets/official-templates/guides/<slug>/`.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import shutil
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNALS_DIR = ROOT / "references" / "journals"
DEFAULT_GUIDE_ROOT = ROOT / "assets" / "official-templates" / "guides"
DOWNLOAD_URL_OVERRIDES = {
    "nature-communications": {
        "download_url": "https://www.nature.com/documents/ncomms-formatting-instructions.pdf",
        "note": "Downloaded the official Nature Communications formatting-instructions PDF because the page URL in verification redirects in a loop for command-line clients.",
    },
    "robotics": {
        "download_url": "https://res.mdpi.com/data/mdpi-author-layout-style-guide.pdf",
        "note": "Downloaded the official MDPI author layout style guide because the Robotics instructions page is access-controlled for command-line clients in this environment.",
    },
}

CONTENT_TYPE_EXTENSION_MAP = {
    "text/html": ".html",
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
    "application/octet-stream": ".bin",
}


def extract_field(text: str, field_name: str) -> str:
    prefix = f"{field_name}: "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(": ", 1)[1].strip().strip('"')
    raise ValueError(f"Field {field_name!r} not found")


def yaml_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def choose_extension(url: str, content_type: str) -> str:
    url_path = urllib.parse.urlparse(url).path
    suffix = Path(url_path).suffix.lower()
    if suffix in {".html", ".htm", ".pdf", ".zip"}:
        return suffix
    if content_type in CONTENT_TYPE_EXTENSION_MAP:
        mapped = CONTENT_TYPE_EXTENSION_MAP[content_type]
        if mapped != ".bin":
            return mapped
    guessed = mimetypes.guess_extension(content_type or "")
    if guessed:
        return guessed
    return ".bin"


def download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Codex/GuideFetcher",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read()
            content_type = response.headers.get_content_type()
        return payload, content_type
    except Exception:
        result = subprocess.run(
            ["curl.exe", "-L", "-A", "Mozilla/5.0", url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if suffix == ".zip":
            content_type = "application/zip"
        elif suffix == ".pdf":
            content_type = "application/pdf"
        else:
            content_type = "text/html"
        return result.stdout, content_type


def write_url_shortcut(path: Path, url: str) -> None:
    path.write_text(f"[InternetShortcut]\nURL={url}\n", encoding="utf-8")


def update_verification_yaml(
    verification_path: Path,
    relative_guide_asset: str,
    download_url: str,
    note: str,
) -> None:
    lines = verification_path.read_text(encoding="utf-8").splitlines()
    filtered: list[str] = []
    for line in lines:
        if line.startswith("official_guide_asset: "):
            continue
        if line.startswith("official_guide_download_url: "):
            continue
        if line.startswith("official_guide_note: "):
            continue
        filtered.append(line)

    updated: list[str] = []
    inserted = False
    for line in filtered:
        updated.append(line)
        if line.startswith("official_source: "):
            updated.append(f'official_guide_asset: "{yaml_quote(relative_guide_asset)}"')
            updated.append(f'official_guide_download_url: "{yaml_quote(download_url)}"')
            updated.append(f'official_guide_note: "{yaml_quote(note)}"')
            inserted = True
    if not inserted:
        raise ValueError(f"official_source not found in {verification_path}")
    verification_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def write_manifest(guide_root: Path, items: list[dict[str, str]]) -> None:
    (guide_root / "manifest.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Official Guide Source Assets",
        "",
        "This directory stores guide-source files downloaded from the official URLs",
        "declared in `verification.yaml`.",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Total targets: {len(items)}",
        "",
        "## Targets",
        "",
    ]
    for item in items:
        lines.append(
            f"- `{item['slug']}`: `{item['downloaded_file']}` from {item['official_source']}"
        )
    (guide_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download official guide-source files for all verification targets."
    )
    parser.add_argument(
        "--journals-root",
        default=str(DEFAULT_JOURNALS_DIR),
        help="Root directory containing journal profile folders.",
    )
    parser.add_argument(
        "--guide-root",
        default=str(DEFAULT_GUIDE_ROOT),
        help="Destination root for downloaded official guide-source files.",
    )
    args = parser.parse_args()
    journals_root = Path(args.journals_root)
    guide_root = Path(args.guide_root)
    guide_root.mkdir(parents=True, exist_ok=True)

    cache: dict[str, tuple[bytes, str, str]] = {}
    manifest_items: list[dict[str, str]] = []

    for verification_path in sorted(journals_root.rglob("verification.yaml")):
        text = verification_path.read_text(encoding="utf-8")
        slug = extract_field(text, "slug")
        official_source = extract_field(text, "official_source")
        override = DOWNLOAD_URL_OVERRIDES.get(slug, {})
        download_url = override.get("download_url", official_source)
        slug_dir = guide_root / slug
        if slug_dir.exists():
            shutil.rmtree(slug_dir)
        slug_dir.mkdir(parents=True, exist_ok=True)

        if download_url not in cache:
            payload, content_type = download(download_url)
            extension = choose_extension(download_url, content_type)
            cache[download_url] = (payload, content_type, extension)
        payload, content_type, extension = cache[download_url]

        downloaded_file = f"official-guide-source{extension}"
        (slug_dir / downloaded_file).write_bytes(payload)
        write_url_shortcut(slug_dir / "official-guide-source.url", official_source)
        (slug_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "slug": slug,
                    "official_source": official_source,
                    "download_url": download_url,
                    "content_type": content_type,
                    "downloaded_file": downloaded_file,
                    "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "note": override.get("note", ""),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        manifest_items.append(
            {
                "slug": slug,
                "official_source": official_source,
                "download_url": download_url,
                "downloaded_file": f"{slug}/{downloaded_file}",
                "content_type": content_type,
            }
        )
        update_verification_yaml(
            verification_path,
            f"assets/official-templates/guides/{slug}/{downloaded_file}",
            download_url,
            override.get("note", ""),
        )
        print(f"downloaded {slug}")

    write_manifest(guide_root, manifest_items)
    print(f"Downloaded official guide-source files for {len(manifest_items)} targets.")


if __name__ == "__main__":
    main()

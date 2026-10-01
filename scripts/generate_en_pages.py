#!/usr/bin/env python3
"""Write one Jekyll page per published story that has an English include.

English pages live at /en/<year>/<month>/<day>/<slug>.html. Chinese pages
keep their existing URLs. Re-run this after adding or retitling a story.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
OUT_DIR = ROOT / "en" / "posts"
DATE_NAME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")
PUBLISHED_FALSE = re.compile(r"(?m)^published:\s*false\s*$")
TITLE_EN = re.compile(r'(?m)^title_en:\s*"(.*)"\s*$')
EN_INCLUDE = re.compile(r"(?m)^en_include:\s*(\S+)\s*$")


def yaml_quote(value: str) -> str:
    """Return a double-quoted YAML scalar."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def excerpt(source: str) -> str:
    """First slice of English text for the page description."""
    text = re.sub(r"<[^>]+>", " ", source)
    text = re.sub(r"[#>*_`]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 140:
        return text[:140].rstrip() + "…"
    return text


def front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    close = text.find("\n---\n", 4)
    if close == -1:
        return ""
    return text[4:close]


def pages() -> list[tuple[str, str]]:
    """Return (output path relative to en/posts, file body) for each story."""
    written: list[tuple[str, str]] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        match = DATE_NAME.match(path.name)
        if not match:
            continue
        text = path.read_text(encoding="utf-8")
        matter = front_matter(text)
        if not matter or PUBLISHED_FALSE.search(matter):
            continue
        include_match = EN_INCLUDE.search(matter)
        if not include_match:
            continue
        year, month, day, slug = match.groups()
        zh_url = f"/{year}/{month}/{day}/{slug}.html"
        en_url = f"/en{zh_url}"
        title_match = TITLE_EN.search(matter)
        title = title_match.group(1) if title_match else slug
        title = title.replace('\\"', '"').replace("\\\\", "\\")
        include_path = ROOT / "_includes" / include_match.group(1)
        description = ""
        if include_path.exists():
            description = excerpt(include_path.read_text(encoding="utf-8"))
        body = (
            "---\n"
            "layout: post\n"
            "lang: en\n"
            f"title: {yaml_quote(title)}\n"
            f"description: {yaml_quote(description)}\n"
            f"zh_url: {zh_url}\n"
            f"permalink: {en_url}\n"
            "---\n"
        )
        written.append((f"{slug}.md", body))
    return written


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    keep: set[str] = set()
    for name, body in pages():
        destination = OUT_DIR / name
        destination.write_text(body, encoding="utf-8")
        keep.add(name)
    for existing in OUT_DIR.glob("*.md"):
        if existing.name not in keep:
            existing.unlink()
    print(f"wrote {len(keep)} english pages")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Crawl mirror.chromaso.net thread 29311 into full-text and forum markdown."""

import html as html_lib
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag

THREAD_ID = 29311
BASE = f"https://mirror.chromaso.net/thread/{THREAD_ID}"
AUTHOR_CHROMASO = "/author/25646"
PAGES = 38
POSTS_PER_PAGE = 20
OUT_DIR = "/Users/cmsflash/programs/victor-w-ma.github.io/_works/just-want-to-be-your-slave"

CHAPTER_RE = re.compile(
    r"第\s*(?:\d+\.\d+|5A\.\d+)\s*章|第\s*\d+\s*部分[：:][^\n<]{0,80}"
)
PART_RE = re.compile(r"第\s*\d+\s*部分[：:][^\n\[]+")
CHAPTER_ONLY_RE = re.compile(r"第\s*(?:\d+\.\d+|5A\.\d+)\s*章")


@dataclass
class Post:
    post_id: str
    author: str
    author_href: str
    published: str
    edited: str
    subtitle: str
    body_html: str
    body_md: str
    page: int
    is_chapter: bool
    chapter_labels: List[str]


def page_url(page: int) -> str:
    if page <= 1:
        return BASE
    offset = (page - 1) * POSTS_PER_PAGE
    return f"{BASE}/+{offset}"


def fetch(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "victor-w-ma.github.io research crawler"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt + 1 >= retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"unreachable: {url}")


def inline_to_md(node: Tag) -> str:
    parts: List[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            name = child.name
            if name in ("br",):
                parts.append("\n")
            elif name in ("strong", "b"):
                inner = inline_to_md(child).strip()
                parts.append(f"**{inner}**" if inner else "")
            elif name in ("em", "i"):
                inner = inline_to_md(child).strip()
                parts.append(f"*{inner}*" if inner else "")
            elif name == "a":
                text = inline_to_md(child).strip() or child.get("href", "")
                href = child.get("href", "")
                if href:
                    parts.append(f"[{text}]({href})")
                else:
                    parts.append(text)
            elif name == "img":
                alt = child.get("alt", "") or child.get("src", "")
                src = child.get("src", "")
                parts.append(f"![{alt}]({src})" if src else "")
            elif name == "s":
                parts.append("")
            elif name == "span":
                parts.append(inline_to_md(child))
            elif name == "blockquote":
                inner = block_to_md(child).strip()
                lines = [f"> {ln}" for ln in inner.splitlines() if ln.strip()]
                parts.append("\n".join(lines))
            else:
                parts.append(inline_to_md(child))
    return "".join(parts)


def block_to_md(node: Tag) -> str:
    chunks: List[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text.strip():
                chunks.append(text)
        elif isinstance(child, Tag):
            name = child.name
            if name in ("p", "div", "li", "h1", "h2", "h3", "h4", "blockquote"):
                inner = inline_to_md(child) if name != "blockquote" else block_to_md(child)
                inner = inner.strip()
                if not inner:
                    continue
                if name == "li":
                    chunks.append(f"- {inner}")
                elif name in ("h1", "h2", "h3", "h4"):
                    level = int(name[1])
                    chunks.append(f"{'#' * level} {inner}")
                elif name == "blockquote":
                    lines = [f"> {ln}" for ln in inner.splitlines()]
                    chunks.append("\n".join(lines))
                else:
                    chunks.append(inner)
            elif name in ("ul", "ol"):
                chunks.append(block_to_md(child))
            elif name == "br":
                chunks.append("")
            elif name == "s":
                pass
            else:
                chunks.append(inline_to_md(child))
    text = "\n\n".join(c.strip() for c in chunks if c and c.strip())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def html_body_to_md(body: Tag) -> str:
    return block_to_md(body).strip()


def extract_chapter_labels(md: str) -> List[str]:
    labels: List[str] = []
    for line in md.splitlines():
        line = line.strip()
        if not line:
            continue
        if PART_RE.search(line):
            labels.append(PART_RE.search(line).group(0).strip())
        elif CHAPTER_ONLY_RE.search(line):
            labels.append(CHAPTER_ONLY_RE.search(line).group(0).strip())
    # dedupe preserving order
    seen = set()
    out: List[str] = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def is_chapter_post(author_href: str, md: str, post_id: str) -> bool:
    if author_href != AUTHOR_CHROMASO:
        return False
    if post_id == "p282568":
        return False
    return bool(CHAPTER_RE.search(md))


def parse_posts(page_html: str, page_num: int) -> List[Post]:
    soup = BeautifulSoup(page_html, "html.parser")
    posts: List[Post] = []
    for card in soup.select("div.card.mm-post"):
        post_id = card.get("id", "")
        header = card.select_one(".card-header")
        body = card.select_one(".card-body")
        if not header or not body:
            continue
        author_a = header.select_one('a.ui-link[href^="/author/"]')
        author = author_a.get_text(strip=True) if author_a else "?"
        author_href = author_a.get("href", "") if author_a else ""
        times = header.select("time")
        published = times[0].get("datetime", "") if times else ""
        edited = times[1].get("datetime", "") if len(times) > 1 else ""
        subtitle_el = header.select_one(".text-muted")
        subtitle = ""
        if subtitle_el:
            # last text-muted in header row is often subtitle
            subs = header.select(".text-muted")
            if subs:
                subtitle = subs[-1].get_text(strip=True)
        body_md = html_body_to_md(body)
        chapter = is_chapter_post(author_href, body_md, post_id)
        labels = extract_chapter_labels(body_md) if chapter else []
        posts.append(
            Post(
                post_id=post_id,
                author=author,
                author_href=author_href,
                published=published,
                edited=edited,
                subtitle=subtitle,
                body_html=str(body),
                body_md=body_md,
                page=page_num,
                is_chapter=chapter,
                chapter_labels=labels,
            )
        )
    return posts


def crawl_all() -> List[Post]:
    all_posts: List[Post] = []
    seen_ids = set()
    for page in range(1, PAGES + 1):
        url = page_url(page)
        print(f"Fetching page {page}/{PAGES}: {url}")
        html = fetch(url)
        posts = parse_posts(html, page)
        for post in posts:
            if post.post_id in seen_ids:
                continue
            seen_ids.add(post.post_id)
            all_posts.append(post)
        time.sleep(0.3)
    return all_posts


def build_full_text(posts: List[Post]) -> str:
    lines = [
        "# 偏偏要做你的 M",
        "",
        "> 来源：[M系镜像 · 主题 29311](https://mirror.chromaso.net/thread/29311)",
        "> 本文档由爬虫从镜像帖正文帖汇总生成。",
        "",
    ]
    op = next((p for p in posts if p.post_id == "p282568"), None)
    if op:
        lines.append("---")
        lines.append("")
        lines.append(op.body_md)
        lines.append("")
    chapter_posts = [p for p in posts if p.is_chapter]
    for post in chapter_posts:
        lines.append("---")
        lines.append("")
        lines.append(post.body_md)
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"*共收录开篇帖 1 则、章节帖 {len(chapter_posts)} 则（镜像爬取）。*"
    )
    return "\n".join(lines)


def format_forum_post(post: Post) -> str:
    meta = f"**{post.author}** · `{post.post_id}`"
    if post.published:
        meta += f" · 发布 {post.published}"
    if post.edited and post.edited != post.published:
        meta += f" · 编辑 {post.edited}"
    meta += f" · 第 {post.page} 页"
    if post.subtitle and post.subtitle != post.author:
        meta += f"\n\n*{post.subtitle}*"
    lines = [meta, ""]
    if post.is_chapter:
        if post.chapter_labels:
            label_str = " · ".join(post.chapter_labels)
        else:
            label_str = "（章节帖，未解析到标题）"
        lines.append(f"📄 **[正文章节]** {label_str}")
        lines.append("")
        lines.append(
            f"> 正文已收录于 [`full-text.md`](full-text.md)，此处不重复。"
        )
    else:
        if post.body_md:
            lines.append(post.body_md)
        else:
            lines.append("*(空帖)*")
    return "\n".join(lines)


def build_forum_thread(posts: List[Post]) -> str:
    lines = [
        "# 偏偏要做你的 M — 镜像帖讨论存档",
        "",
        "> 来源：[M系镜像 · 主题 29311](https://mirror.chromaso.net/thread/29311)",
        "> 论坛格式：按帖序排列；**章节正文帖仅保留标题索引**，全文见 [`full-text.md`](full-text.md)。",
        "",
        f"- 总帖数：{len(posts)}",
        f"- 章节帖：{sum(1 for p in posts if p.is_chapter)}",
        f"- 讨论/回复帖：{sum(1 for p in posts if not p.is_chapter)}",
        "",
        "---",
        "",
    ]
    for i, post in enumerate(posts, 1):
        lines.append(f"## 楼层 {i}")
        lines.append("")
        lines.append(format_forum_post(post))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    posts = crawl_all()
    full_text = build_full_text(posts)
    forum = build_forum_thread(posts)
    full_path = f"{OUT_DIR}/full-text.md"
    forum_path = f"{OUT_DIR}/forum-thread.md"
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    with open(forum_path, "w", encoding="utf-8") as f:
        f.write(forum)
    print(f"Wrote {full_path} ({len(full_text)} chars)")
    print(f"Wrote {forum_path} ({len(forum)} chars)")
    print(f"Posts: {len(posts)}, chapters: {sum(1 for p in posts if p.is_chapter)}")


if __name__ == "__main__":
    main()

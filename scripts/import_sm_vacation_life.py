#!/usr/bin/env python3
"""Assemble SM度假生活: Pixiv ch. 1-9 + forum ch. 10-11; extras go to metadata."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from post_format import fix_body, print_audit  # noqa: E402

SRC = Path('/tmp/sm-vacation')
OUT_POST = ROOT / '_posts' / '2026-08-28-sm-vacation-life.md'
OUT_META = ROOT / '_posts' / '2026-08-28-sm-vacation-life-metadata.md'

STORY_THREAD_ID = 24985
VOTE_THREAD_ID = 25256
AUTHOR_HREF = '/author/22414'
UA = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

CHAPTER_TITLES = {
    1: '女王真由子',
    2: '女奴隶深雪',
    3: '男奴与女奴',
    4: '新治的过去',
    5: 'M男的威严',
    6: '启程的清晨',
    7: '未央的挑逗',
    8: 'SM的国度',
    9: '另一位女王',
    10: '新治的抉择',
    11: '由奈夫妻的登场',
}

PIXIV_FILES = {
    1: 'pixiv-01-17876406.txt',
    2: 'pixiv-02-17876424.txt',
    3: 'pixiv-03-17879174.txt',
    4: 'pixiv-04-17881895.txt',
    5: 'pixiv-05-17889632.txt',
    6: 'pixiv-06-17920899.txt',
    7: 'pixiv-07-17933019.txt',
    8: 'pixiv-08-17944776.txt',
    9: 'pixiv-09-17965595.txt',
}

FORUM_CHAPTER_IDS = {
    1: 'p226851',
    2: 'p226933',
    3: 'p227016',
    4: 'p227274',
    5: 'p228175',
    6: 'p228345',
    7: 'p228656',
    8: 'p229320',
    9: 'p229893',
    10: 'p229913',
    11: 'p233190',
}

SPLIT_RE = re.compile(r'\n?[-—─-]{6,}[^\n]*分割线[^\n]*\n?')
CHAPTER_MARK_RE = re.compile(r'^（[一二三四五六七八九十]+）')
AUTHOR_LINE_RE = re.compile(r'^作者：[^\n]+\n*')

EXTRA_REPLACEMENTS: list[tuple[str, str]] = [
    ('一幅欲求不满', '一副欲求不满'),
    ('一幅下贱样子', '一副下贱样子'),
    ('一幅如此羞耻', '一副如此羞耻'),
    ('这样一幅姿态', '这样一副姿态'),
    ('两幅项圈', '两副项圈'),
    ('被项圈栓住', '被项圈拴住'),
    ('面面厮觑', '面面相觑'),
    # Applied after 「」 → ASCII quotes inside fix_body.
    ('开始仔细侍奉脚趾。"', '开始仔细侍奉脚趾。'),
]

# Shared 的→地 rules misfire on 嘲弄/兴奋/屈辱/傲慢 + 名词.
EXTRA_FALSE_POSITIVE_FIXES: list[tuple[str, str]] = [
    ('嘲弄地眼神', '嘲弄的眼神'),
    ('兴奋地时候', '兴奋的时候'),
    ('傲慢地声音', '傲慢的声音'),
    ('屈辱地经历', '屈辱的经历'),
    ('最屈辱地调教', '最屈辱的调教'),
    ('口交地请求', '口交的请求'),
    ('兴奋地欲望奴隶', '兴奋的欲望奴隶'),
    ('兴奋地变态受虐狂', '兴奋的变态受虐狂'),
    ('最兴奋地是', '最兴奋的是'),
    ('紧张地声音', '紧张的声音'),
    ('兴奋地情况下', '兴奋的情况下'),
    ('深雪地请求', '深雪的请求'),
    ('屈辱地下场', '屈辱的下场'),
    ('十足地请求', '十足的请求'),
    ('屈辱地姿势', '屈辱的姿势'),
]


def http_get(url: str, retries: int = 5) -> str:
    """Fetch URL as UTF-8 text with retries."""
    delay = 2.0
    last_error: Exception | None = None
    for _ in range(retries):
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as err:
            if err.code in {400, 404}:
                raise
            last_error = err
        except urllib.error.URLError as err:
            last_error = err
        time.sleep(delay)
        delay *= 2
    raise RuntimeError(f'Failed to fetch {url}: {last_error}')


def html_to_text(fragment: str) -> str:
    """Convert a chromaso post body fragment to plain text."""
    soup = BeautifulSoup(fragment, 'html.parser')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for quote in soup.find_all('blockquote'):
        inner = quote.get_text('\n', strip=True)
        lines = [f'> {line}' if line else '>' for line in inner.splitlines()]
        quote.replace_with('\n' + '\n'.join(lines) + '\n')
    for img in soup.find_all('img'):
        alt = img.get('alt') or ''
        src = img.get('src') or ''
        img.replace_with(f'[图片{": " + alt if alt else ""}]({src})' if src else '[图片]')
    text = unescape(soup.get_text(''))
    text = text.replace('\xa0', ' ')
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_posts(html: str) -> list[dict]:
    """Parse mm-post cards from a chromaso thread page."""
    soup = BeautifulSoup(html, 'html.parser')
    posts: list[dict] = []
    for card in soup.select('div.mm-post[id]'):
        if not isinstance(card, Tag):
            continue
        pid = card.get('id') or ''
        if not str(pid).startswith('p'):
            continue
        author_a = card.select_one('a.ui-link[href^="/author/"]')
        href = ''
        author = ''
        if author_a:
            href = str(author_a.get('href') or '')
            author = author_a.get_text(strip=True)
        times = [
            str(t.get('datetime') or '')
            for t in card.select('time[datetime]')
            if t.get('datetime')
        ]
        body = card.select_one('div.card-body')
        raw_html = str(body) if body else ''
        posts.append({
            'id': str(pid),
            'author': author,
            'href': href,
            'published': times[0] if times else '',
            'edited': times[1] if len(times) > 1 else '',
            'is_author': href == AUTHOR_HREF,
            'md': html_to_text(raw_html),
        })
    return posts


def fetch_thread(thread_id: int) -> list[dict]:
    """Crawl every page of a chromaso thread."""
    posts: list[dict] = []
    seen: set[str] = set()
    offset = 0
    while offset <= 400:
        url = f'https://mirror.chromaso.net/thread/{thread_id}/+{offset}'
        try:
            html = http_get(url)
        except urllib.error.HTTPError as err:
            if err.code in {400, 404}:
                break
            raise
        page_posts = parse_posts(html)
        if not page_posts:
            break
        new_count = 0
        for post in page_posts:
            if post['id'] in seen:
                continue
            seen.add(post['id'])
            posts.append(post)
            new_count += 1
        if new_count == 0 or len(page_posts) < 20:
            break
        offset += 20
        time.sleep(0.4)
    return posts


def load_or_fetch_thread(thread_id: int) -> list[dict]:
    """Return cached thread JSON, fetching from chromaso if needed."""
    SRC.mkdir(parents=True, exist_ok=True)
    path = SRC / f'forum-{thread_id}.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    print(f'Fetching thread {thread_id}…')
    posts = fetch_thread(thread_id)
    path.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'  {len(posts)} posts -> {path}')
    return posts


def pixiv_body(path: Path) -> str:
    raw = path.read_text(encoding='utf-8')
    _, _, content = raw.partition('\n\n')
    content = re.sub(r'^\[chapter:[^\]]+\]\n*', '', content.strip())
    return content.strip()


def _strip_chapter_header(story: str) -> str:
    story = CHAPTER_MARK_RE.sub('', story, count=1).lstrip()
    story = AUTHOR_LINE_RE.sub('', story, count=1).lstrip()
    return story.strip()


def split_forum_post(md: str) -> tuple[str, list[str]]:
    """Return (story_body, author_notes) for a chapter post."""
    parts = [part.strip() for part in SPLIT_RE.split(md) if part.strip()]
    story = ''
    notes: list[str] = []
    for text in parts:
        if CHAPTER_MARK_RE.match(text):
            story = text
        else:
            notes.append(text)
    if not story and parts:
        story = max(parts, key=len)
        notes = [part for part in parts if part != story]
    return _strip_chapter_header(story), notes


def forum_story(posts_by_id: dict[str, dict], chapter: int) -> str:
    post = posts_by_id[FORUM_CHAPTER_IDS[chapter]]
    story, _ = split_forum_post(post['md'])
    if not story:
        raise SystemExit(f'Empty story for forum chapter {chapter}')
    return story


def heading(n: int) -> str:
    return f'# 第{n}章　{CHAPTER_TITLES[n]}'


def assemble_post(posts_by_id: dict[str, dict]) -> str:
    parts = [
        '---',
        'layout: post',
        'title: "SM度假生活"',
        '---',
        '',
    ]
    for n in range(1, 10):
        parts.append(heading(n))
        parts.append('')
        parts.append(pixiv_body(SRC / PIXIV_FILES[n]))
        parts.append('')
    for n in (10, 11):
        parts.append(heading(n))
        parts.append('')
        parts.append(forum_story(posts_by_id, n))
        parts.append('')
    return '\n'.join(parts)


def format_post_block(post: dict) -> str:
    when = post.get('published') or ''
    edited = post.get('edited') or ''
    stamp = when
    if edited and edited != when:
        stamp = f'{when}（编辑于 {edited}）'
    header = f'### {post["id"]} · {post["author"]} · {stamp}'.rstrip(' ·')
    body = post.get('md') or '（空）'
    return f'{header}\n\n{body}\n'


def assemble_metadata(
    story_posts: list[dict],
    vote_posts: list[dict],
) -> str:
    posts_by_id = {p['id']: p for p in story_posts}
    chapter_ids = set(FORUM_CHAPTER_IDS.values())

    lines = [
        '---',
        'published: false',
        '---',
        '',
        '# 《SM度假生活》来源与原帖附件',
        '',
        '> 本文件不上线（`published: false`）。正文见 `_posts/2026-08-28-sm-vacation-life.md`。',
        '> 正文只保留小说；作者注、投票、原帖里其他人的回复收录于此。',
        '',
        '## 来源',
        '',
        '- 作者：悪魔五月哭く / DevilMayCry（[Pixiv](https://www.pixiv.net/users/82845353)，论坛 `devilmaycry` / `/author/22414`）',
        '- 第 1–9 章：Pixiv 系列 [9119819](https://www.pixiv.net/novel/series/9119819) 的 2022 年修订稿',
        '- 第 10–11 章：2016 年论坛连载 [thread/24985](https://mirror.chromaso.net/thread/24985)（第 10 章含男主人登场与三种选择，才能接到第 11 章）',
        '- Pixiv 另有第 10 章修订（novel 18000874），未采用：该稿没有论坛第 10 章的男主人／三选一，接不上第 11 章',
        '- 投票帖：[thread/25256](https://mirror.chromaso.net/thread/25256)（2016-07-23）',
        '',
        '## 论坛各章作者注',
        '',
        '从各章发表帖里抽出来的分割线外文字（不含小说正文）。',
        '',
    ]

    for n, pid in FORUM_CHAPTER_IDS.items():
        post = posts_by_id[pid]
        _, notes = split_forum_post(post['md'])
        lines.append(f'### 第{n}章　{CHAPTER_TITLES[n]}（{pid}，{post["published"]}）')
        lines.append('')
        if notes:
            for note in notes:
                lines.append(note)
                lines.append('')
        else:
            lines.append('（该章发表帖没有分割线外的作者注。）')
            lines.append('')

    lines.append('## 原帖其他回复')
    lines.append('')
    lines.append(
        f'来源：[thread/{STORY_THREAD_ID}](https://mirror.chromaso.net/thread/{STORY_THREAD_ID})。'
        '下列不含十一章小说正文（作者注见上一节）；作者对其它楼的回复、以及其他人的回复均按时间收入。'
    )
    lines.append('')

    reply_count = 0
    for post in story_posts:
        if post['id'] in chapter_ids:
            continue
        lines.append(format_post_block(post))
        reply_count += 1
    lines.append(f'共 {reply_count} 条。')
    lines.append('')

    lines.append('## 投票帖全文')
    lines.append('')
    lines.append(
        f'来源：[thread/{VOTE_THREAD_ID}](https://mirror.chromaso.net/thread/{VOTE_THREAD_ID})。'
        f'共 {len(vote_posts)} 条，按原帖顺序全收。'
    )
    lines.append('')
    lines.append(
        '镜像未保存原 phpBB 投票控件。三个选项同正文第 10 章文末：'
        '① 上了未央；② 把深雪献给未央，做未央的奴隶；'
        '③ 把深雪献给「男主人」，等待深雪的S性被开发。'
        '作者后来在本帖 p230157 称 70 票已达成，且「2 是大势所趋」。'
    )
    lines.append('')
    for post in vote_posts:
        lines.append(format_post_block(post))

    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text).rstrip() + '\n'
    return text


def write_live_post(raw: str) -> str:
    if not raw.startswith('---'):
        raise SystemExit('missing front matter')
    chunks = raw.split('---', 2)
    front_matter = f'---{chunks[1]}---\n'
    body = chunks[2].lstrip('\n')
    body = fix_body(
        body,
        extra_replacements=EXTRA_REPLACEMENTS,
        extra_false_positive_fixes=EXTRA_FALSE_POSITIVE_FIXES,
    )
    body = re.sub(r'\n{3,}', '\n\n', body).rstrip() + '\n'
    OUT_POST.write_text(front_matter + '\n' + body, encoding='utf-8')
    return body


def main() -> None:
    story_posts = load_or_fetch_thread(STORY_THREAD_ID)
    vote_posts = load_or_fetch_thread(VOTE_THREAD_ID)
    posts_by_id = {p['id']: p for p in story_posts}
    missing = [pid for pid in FORUM_CHAPTER_IDS.values() if pid not in posts_by_id]
    if missing:
        raise SystemExit(f'Missing forum chapter posts: {missing}')

    raw = assemble_post(posts_by_id)
    body = write_live_post(raw)
    print(f'Wrote {OUT_POST} ({OUT_POST.stat().st_size} bytes)')
    print_audit(body)

    meta = assemble_metadata(story_posts, vote_posts)
    OUT_META.write_text(meta, encoding='utf-8')
    print(f'Wrote {OUT_META} ({OUT_META.stat().st_size} bytes)')


if __name__ == '__main__':
    main()

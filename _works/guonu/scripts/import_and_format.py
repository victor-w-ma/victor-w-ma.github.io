#!/usr/bin/env python3
"""Import 过奴 sources into _works/guonu/stories and format per AGENTS.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))

from post_format import (  # pylint: disable=wrong-import-position
    audit,
    fix_body,
    print_audit,
    split_front_matter,
)

YANGE = Path('/Users/cmsflash/drive/Ongoing/Yange/text')
POSTS = ROOT / '_posts'
OUT = ROOT / '_works' / 'guonu' / 'stories'

# (out_slug, chinese_title, source_path)
# Prefer longest/cleanest variant; web-fetched slots filled later.
SOURCES: list[tuple[str, str, Path]] = [
    (
        'langzu',
        '狼族',
        YANGE / '唯爱足18-20年/唯爱足2018/2018-10/狼族.md',
    ),
    (
        'another-legend',
        '另一种传说（狼族姊妹篇）',
        YANGE / '唯爱足21-22年/2022-05/100522-另一种传说（狼族姊妹篇）.md',
    ),
    (
        'taoyuan-town',
        '桃源镇',
        YANGE / '唯爱足15-17年/唯爱足2017/2017-06/桃源镇.md',
    ),
    (
        'zhu-min',
        '祝敏',
        YANGE / '唯爱足21-22年/2021-01/84347-祝敏.md',
    ),
    (
        'yang-lina-slave',
        '杨丽娜的奴隶',
        YANGE / '唯爱足21-22年/2021-01/84293-杨丽娜的奴隶.md',
    ),
    (
        'mama-full',
        '妈妈全篇',
        YANGE / '唯爱足21-22年/2021-09/93839-妈妈全篇（强烈推荐）.md',
    ),
    (
        'kuxia-sihou',
        '胯下伺候',
        YANGE / '自己三年整理的文/整理36/胯下伺候.md',
    ),
    (
        'sihou-qinglvzhu',
        '伺候情侣主',
        YANGE / '自己三年整理的文/整理36/伺候情侣主.md',
    ),
    (
        'stranger-woman-memory',
        '一个陌生女人的回忆',
        YANGE / '唯爱足21-22年/2021-06/90033-一个陌生女人的回忆.md',
    ),
    (
        'slave-road',
        '奴隶之路',
        YANGE / '自己三年整理的文/整理47/奴隶之路（过奴版）.md',
    ),
    (
        'couple-things',
        '夫妻那些事（过奴改编）',
        YANGE / '女主天地调教合集/新建文件夹/小说观看精品/夫妻那些事作者过奴.md',
    ),
    (
        'marital-anomaly',
        '婚内性异常',
        YANGE / '女主天地调教合集/新建文件夹/小说观看精品/婚内性异常作者过奴.md',
    ),
    (
        'xianmu',
        '献母',
        YANGE / '唯爱足21-22年/2021-03/87170-过奴作品献母.md',
    ),
    (
        'guonu-gailian',
        '过奴（改舔）',
        YANGE / '女主天地调教合集/新建文件夹/家庭伦理普通/过奴（改舔）.md',
    ),
    (
        'guonu-theories',
        '过奴夫妻主理论合集',
        POSTS / '2022-07-24-guonu-theories.md',
    ),
    (
        'ghost-charm-dream',
        '鬼符梦',
        POSTS / 'ghosty-dream.md',
    ),
    (
        'meitong-another-legend-1-16',
        '魅瞳·另一种传说番外（1–16）',
        YANGE / '女主天地调教合集/新建文件夹/家庭伦理精品/《魅瞳》另一种传说 番外篇(1-16).md',
    ),
    (
        'meitong-another-legend-17-23',
        '魅瞳·另一种传说番外（17–23）',
        YANGE / '女主天地调教合集/新建文件夹/家庭伦理精品/《魅瞳》另一种传说 番外篇(17-23).md',
    ),
]

AD_PATTERNS = [
    re.compile(r'〔[^〕]*加[qQ扣].*?〕'),
    re.compile(r'（各种sm资源[^）]*）'),
    re.compile(r'\(各种sm资源[^)]*\)'),
    re.compile(r'各种sm视频（[^）]*）[^。\n]*'),
]


def strip_ads(body: str) -> str:
    for pat in AD_PATTERNS:
        body = pat.sub('', body)
    return body


def ensure_front_matter(text: str, title: str) -> tuple[str, str]:
    front, body = split_front_matter(text)
    if not front:
        # Drop leading author lines into body; wrap new front matter.
        body = text.lstrip('\n')
    front = f'---\nlayout: post\ntitle: "{title}"\n---\n'
    # Remove duplicated markdown title / author banner lines at top.
    lines = body.splitlines()
    cleaned: list[str] = []
    skip_until_content = True
    for line in lines:
        raw = line.strip()
        if skip_until_content:
            if not raw:
                continue
            if raw.startswith('#'):
                continue
            if raw.startswith('作者') or raw.startswith('字数') or raw.startswith('过奴制造'):
                continue
            if raw in {title, f'【{title}】', f'《{title}》'}:
                continue
            skip_until_content = False
        cleaned.append(line)
    body = '\n'.join(cleaned).lstrip('\n')
    return front, body


def paragraphize(body: str) -> str:
    """If body is one huge block, insert blank lines at Chinese sentence ends
    when followed by a new dialogue/scene opener — light touch only.
    Existing blank lines are preserved.
    """
    if '\n\n' in body:
        return body
    # Soft-wrap dense OCR: blank line after 。！？ followed by quote or chapter.
    body = re.sub(r'([。！？])\n(?=[“「]|## )', r'\1\n\n', body)
    return body


def process_one(slug: str, title: str, src: Path) -> dict[str, int]:
    if not src.exists():
        raise FileNotFoundError(src)
    text = src.read_text(encoding='utf-8', errors='replace')
    front, body = ensure_front_matter(text, title)
    body = strip_ads(body)
    body = paragraphize(body)
    try:
        body = fix_body(body)
    except ValueError as exc:
        # Unpaired ASCII quotes: leave curly conversion off and continue.
        print(f'  WARN {slug}: {exc}; formatting without quote fix')
        body = fix_body(body, fix_quotes=False)
    out = OUT / f'{slug}.md'
    out.write_text(front + '\n' + body.rstrip() + '\n', encoding='utf-8')
    stats = audit(body)
    print(f'OK {slug} <- {src.name} ({src.stat().st_size}B)')
    print_audit(body)
    return stats


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    for slug, title, src in SOURCES:
        if only and slug not in only:
            continue
        process_one(slug, title, src)


if __name__ == '__main__':
    main()

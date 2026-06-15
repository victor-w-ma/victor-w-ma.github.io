#!/usr/bin/env python3
"""Fix _posts/cuckold-zhao-licheng.md per AGENTS.md."""

from __future__ import annotations

from pathlib import Path

from post_format import (
    fix_body,
    print_audit,
    split_front_matter,
)

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / '_posts' / '2026-06-14-cuckold-zhao-licheng.md'

# Story-specific replacements (on top of scripts/post_format.py COMMON_REPLACEMENTS).
STORY_REPLACEMENTS: list[tuple[str, str]] = [
    ('轮歼', '轮奸'),
    ('臭表子', '臭婊子'),
    ('一个表子', '一个婊子'),
    ('赤倮', '赤裸'),
    ('博起', '勃起'),
    ('一巴拍', '一巴掌拍'),
    ('粪叉', '玛莎拉蒂'),
    ('戏虐', '戏谑'),
    ('忿忿', '愤愤'),
    ('痛疼', '疼痛'),
    ('精夜', '精液'),
    ('龟頭', '龟头'),
    ('吃漏在', '吃了落在'),
]


def main() -> None:
    raw = TARGET.read_text(encoding='utf-8')
    front, body = split_front_matter(raw)
    if not front:
        front = '---\nlayout: post\ntitle: "绿奴"\n---\n'
    fixed_body = fix_body(body, extra_replacements=STORY_REPLACEMENTS)
    TARGET.write_text(front + '\n' + fixed_body, encoding='utf-8')
    print(f'Wrote {TARGET}')
    print('Audit:')
    print_audit(fixed_body)


if __name__ == '__main__':
    main()

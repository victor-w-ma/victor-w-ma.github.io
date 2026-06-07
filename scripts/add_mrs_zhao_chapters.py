#!/usr/bin/env python3
"""Insert chapter headings into mrs-zhao.md (15 chapters)."""

from __future__ import annotations

from pathlib import Path

POST = Path(__file__).resolve().parents[1] / '_posts' / 'backlog' / 'mrs-zhao.md'

CHAPTERS = [
    ('# 第1章 全国群中的赵女士', '　　长时间蛰伏在同城群里'),
    ('# 第2章 婚姻往事与黄金', '　　赵女士似乎变得喜欢和我交流了'),
    ('# 第3章 两年网聊日常', '　　这样漫长的你来我往的聊天方式'),
    ('# 第4章 粉丝饭局与破例', '\u3000\u3000\u201c女神，你真的很优秀'),
    ('# 第5章 养狗与狗笼', '　　一天，她气喘吁吁的告诉我自己接手了一条大型犬'),
    ('# 第6章 露脸照与假阳具', '　　一天晚上我在家里蹲坑'),
    ('# 第7章 贞操锁、飞机杯与长沙之约', '\u3000\u3000\u201c我给他买了贞操锁'),
]

CHANGSHA_TITLES = {
    '# 第8章': '# 第8章 约见长沙',
    '# 第9章': '# 第9章 健身、洗衣与剩饭',
    '# 第10章': '# 第10章 樱桃与卧室入笼',
    '# 第11章': '# 第11章 圣水与角色互换',
    '# 第12章': '# 第12章 丈夫讲述与女儿警觉',
    '# 第13章': '# 第13章 雨夜深喉与丈夫不在',
    '# 第14章': '# 第14章 独处接尿器',
    '# 第15章': '# 第15章 黄金、棉袜与别离',
}


def main() -> None:
    text = POST.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise SystemExit('missing front matter')

    parts = text.split('---\n', 2)
    header = '---\n' + parts[1] + '---\n\n'
    body = parts[2]

    for title, marker in reversed(CHAPTERS):
        idx = body.find(marker)
        if idx == -1:
            raise SystemExit(f'marker not found: {marker[:40]}...')
        if body[idx - 20 : idx].strip().endswith('章'):
            continue
        body = body[:idx] + title + '\n\n' + body[idx:]

    for old, new in CHANGSHA_TITLES.items():
        body = body.replace(old + '\n', new + '\n', 1)

    POST.write_text(header + body, encoding='utf-8')
    print('Updated chapters in', POST)
    for line in body.splitlines():
        if line.startswith('# 第'):
            print(' ', line)


if __name__ == '__main__':
    main()

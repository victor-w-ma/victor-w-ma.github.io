#!/usr/bin/env python3
"""Format 祝敏 / 胯下伺候 and publish to _posts/.

Re-reads Yange sources (works copies may already be post-processed).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from post_format import (  # pylint: disable=wrong-import-position
    audit,
    fix_body,
    print_audit,
    split_front_matter,
)

WORKS = ROOT / '_works' / 'guonu' / 'stories'
POSTS = ROOT / '_posts'
DATE = '2026-08-12'
YANGE = Path('/Users/cmsflash/drive/Ongoing/Yange/text')

SOURCES: dict[str, Path] = {
    'zhu-min': YANGE / '唯爱足21-22年/2021-01/84347-祝敏.md',
    'serving-under-her': YANGE / '自己三年整理的文/整理36/胯下伺候.md',
}

STORY_REPLACEMENTS: list[tuple[str, str]] = [
    ('敲了记下门', '敲了几下门'),
    ('过庆龄牵着', '庆龄牵着'),
    ('廖庆庆龄', '庆龄'),
    ('廖庆龄', '庆龄'),
    ('资金主子', '自己主子'),
    ('着一男一女', '这一男一女'),
    ('谈谈酸臭味', '淡淡酸臭味'),
    ('黄峨色', '黄褐色'),
    ('高根', '高跟'),
    ('传衣服吧', '穿衣服吧'),
    ('清洁一边厨房', '清洁一遍厨房'),
    ('再你和我之间', '在你和我之间'),
    ('大后一声', '大吼一声'),
    ('里所应当', '理所应当'),
    ('送人另一次', '送入另一次'),
    ('吮人口中', '吮入口中'),
    ('双手床', '双手抓着床'),
    ('同事庆龄', '同时庆龄'),
    ('这里得旧家电', '这里的旧家电'),
    ('庆龄得摄像机', '庆龄的摄像机'),
    ('收拾得，', '收拾的，'),
    ('放心的在', '放心地在'),
    ('陶醉的享受', '陶醉地享受'),
    ('嘲弄的做出', '嘲弄地做出'),
    ('喜悦的把', '喜悦地把'),
    ('不由自主的随', '不由自主地随'),
    ('大声的呻吟', '大声地呻吟'),
    ('温柔的抚摸', '温柔地抚摸'),
    ('胜利的微笑', '胜利地微笑'),
    ('温柔的耳语', '温柔地耳语'),
    ('猛烈的抽插', '猛烈地抽插'),
    ('彻底的侮辱', '彻底地侮辱'),
    ('平静的说', '平静地说'),
    ('努力化几个小时', '努力花几个小时'),
    ('想八爪鱼一样', '像八爪鱼一样'),
    ('不象', '不像'),
    ('好象', '好像'),
    ('象往常', '像往常'),
    ('象着火', '像着火'),
    ('象摆弄', '像摆弄'),
    ('象个', '像个'),
    ('象服从', '像服从'),
    ('象庆龄', '像庆龄'),
    ('只能象', '只能像'),
    ('心理很忐忑', '心里很忐忑'),
    ('自己地', '自己的'),
    ('晶地', '晶的'),
    ('外屋地', '外屋的'),
    ('庆龄地', '庆龄的'),
    ('朴武地', '朴武的'),
    ('皮带地', '皮带的'),
    ('他地', '他的'),
    ('她地', '她的'),
    ('你地', '你的'),
    ('厨房地面', '厨房地面'),
    ('赤裸地屁股', '赤裸的屁股'),
    ('抚摸他地脸颊', '抚摸他的脸颊'),
    ('吻吻他地额头', '吻吻他的额头'),
    ('尊贵地女主人', '尊贵的女主人'),
    ('下贱地喝', '下贱地喝'),
    ('真正地男人', '真正的男人'),
    ('真正地男子汉', '真正的男子汉'),
    ('下贱地奴', '下贱的奴'),
    ('伺候地不错', '伺候得不错'),
    ('ｊａｓｏｎ', 'Jason'),
    ('Ｊａｓｏｎ', 'Jason'),
    ('jason', 'Jason'),
    ('Ｍｍｍ', 'Mmm'),
    ('恩了一声', '嗯了一声'),
    ('敷衍恩了一声', '敷衍嗯了一声'),
    ('"恩，', '"嗯，'),
    ('"恩"', '"嗯"'),
    ('象狗一样', '像狗一样'),
    ('鸡巴象你的', '鸡巴像你的'),
    ('节奏象活塞', '节奏像活塞'),
    ('晶楞在', '晶愣在'),
    ('拨出阴茎', '拔出阴茎'),
    ('所作的', '所做的'),
    ('不在又机会', '再没有机会'),
    ('向过去一样', '像过去一样'),
    ('随心所欲的对你', '随心所欲地对你'),
    ('来吧"庆龄', '来吧。"\n\n庆龄'),
]

# fix_de_di turns 改变的 → 改变得 via substring 变的; restore afterwards.
FALSE_POSITIVE_FIXES: list[tuple[str, str]] = [
    ('改变得', '改变的'),
]


def fullwidth_alnum_to_ascii(text: str) -> str:
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if 0xFF10 <= code <= 0xFF19:
            out.append(chr(code - 0xFF10 + ord('0')))
        elif 0xFF21 <= code <= 0xFF3A:
            out.append(chr(code - 0xFF21 + ord('A')))
        elif 0xFF41 <= code <= 0xFF5A:
            out.append(chr(code - 0xFF41 + ord('a')))
        else:
            out.append(ch)
    return ''.join(out)


def dedupe_zhu_min(body: str) -> str:
    """Keep the full second copy; first is a truncated 节选."""
    marker = '已经是顶楼了，这一层的另外一户'
    first = body.find(marker)
    second = body.find(marker, first + 1) if first != -1 else -1
    if second != -1:
        body = body[second:]
    body = re.sub(r'^节选', '', body)
    body = re.sub(r'【祝敏】\s*作者：过奴\s*字数：.*', '', body, flags=re.S)
    return body


def strip_banners(body: str) -> str:
    lines = body.splitlines()
    cleaned: list[str] = []
    for line in lines:
        raw = line.strip()
        if raw.startswith('作者') or raw.startswith('字数'):
            continue
        if raw in {'【祝敏】', '【胯下伺候】'}:
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def unwrap_ocr_lines(body: str) -> str:
    """Join soft-wrapped OCR lines; keep breaks at sentence / dialogue boundaries."""
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return ''

    sentence_end = re.compile(r'[。！？…]$')
    weak_end = re.compile(r'[，、：；]$')
    dialogue_open = re.compile(r'^[“"「]')

    paras: list[str] = []
    buf = lines[0]
    for line in lines[1:]:
        # Continue English / digit fragments across wraps.
        if re.search(r'[A-Za-z0-9]$', buf) and re.match(r'^[A-Za-z0-9]', line):
            buf += line
            continue
        # Soft wrap: previous line not a finished sentence.
        if not sentence_end.search(buf) and not dialogue_open.match(line):
            buf += line
            continue
        if weak_end.search(buf) or line.startswith(('，', '、', '）', ')')):
            buf += line
            continue
        # Finished sentence (or closed unit) → new paragraph.
        paras.append(buf)
        buf = line
    paras.append(buf)
    return '\n\n'.join(paras) + '\n'


def balance_dialogue_quotes(body: str) -> str:
    """Close unclosed dialogue quotes; keep 。！？ inside the closing quote."""
    body = body.replace('\u201c', '"').replace('\u201d', '"')
    body = body.replace('「', '"').replace('」', '"')

    def fix_paragraph(para: str) -> str:
        if '"' not in para:
            return para
        para = para.rstrip()
        if para.count('"') % 2 == 0:
            return para
        if para.endswith(('。', '！', '？', '…')):
            return f'{para[:-1]}"{para[-1]}'
        return para + '"'

    parts = re.split(r'(\n\n+)', body)
    out: list[str] = []
    for part in parts:
        if part.startswith('\n') or not part.strip():
            out.append(part)
        else:
            out.append(fix_paragraph(part))
    return ''.join(out)


def prepare(body: str, *, is_zhu_min: bool) -> str:
    if is_zhu_min:
        body = dedupe_zhu_min(body)
    body = strip_banners(body)
    body = fullwidth_alnum_to_ascii(body)
    body = unwrap_ocr_lines(body)
    body = balance_dialogue_quotes(body)
    body = fix_body(
        body,
        extra_replacements=STORY_REPLACEMENTS,
        extra_false_positive_fixes=FALSE_POSITIVE_FIXES,
    )
    body = re.sub(r'\n{3,}', '\n\n', body)
    # Fix 。” order if any ended up as ”。
    body = body.replace('”。', '。”').replace('”！', '！”').replace('”？', '？”')
    # Quote-side 恩→嗯 after curly conversion.
    body = body.replace('“恩，', '“嗯，').replace('“恩”', '“嗯”')
    body = body.replace('来吧”庆龄', '来吧。”\n\n庆龄')
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip() + '\n'


def publish(slug: str, title: str, *, is_zhu_min: bool) -> Path:
    src = SOURCES[slug]
    raw = src.read_text(encoding='utf-8', errors='replace')
    _front, body = split_front_matter(raw)
    if not body.strip():
        body = raw
        if body.startswith('---'):
            _, body = split_front_matter(body)
    body = prepare(body, is_zhu_min=is_zhu_min)
    front = f'---\nlayout: post\ntitle: "{title}"\n---\n'
    out = POSTS / f'{DATE}-{slug}.md'
    out.write_text(front + '\n' + body, encoding='utf-8')
    works_name = 'zhu-min.md' if is_zhu_min else 'kuxia-sihou.md'
    works_out = WORKS / works_name
    works_out.write_text(front + '\n' + body, encoding='utf-8')
    print(f'Wrote {out.relative_to(ROOT)} ({out.stat().st_size}B) from {src.name}')
    print(f'Refreshed {works_out.relative_to(ROOT)}')
    print('Audit:')
    print_audit(body)
    return out


def main() -> None:
    publish('zhu-min', '祝敏', is_zhu_min=True)
    publish('serving-under-her', '胯下伺候', is_zhu_min=False)


if __name__ == '__main__':
    main()

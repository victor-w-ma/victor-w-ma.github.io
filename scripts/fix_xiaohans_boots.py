#!/usr/bin/env python3
"""Format 《学姐的鞋底，学弟的天堂》 for publish (first book only)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from post_format import (  # pylint: disable=wrong-import-position
    apply_replacements,
    fix_body,
    print_audit,
    split_front_matter,
)

SOURCE = ROOT / '_posts' / '0-2022-06-15-bottom-of-xiaohans-boots.md'
TARGET = ROOT / '_posts' / '2026-09-06-bottom-of-xiaohans-boots.md'

FRONT = '''---
layout: post
title: "学姐的鞋底，学弟的天堂"
---
'''

MULTI_BLANK = re.compile(r'\n{3,}')
FOOTNOTE_LINE = re.compile(r'^(\d+)\.\s+(.+?)\s*↩\s*$')
INLINE_NOTE = re.compile(
    r'(?<=[\u4e00-\u9fff」"”a-zA-Z)])(\d)(?=[，。；：！？、…」"”\s]|——)'
)
IMAGE_PHRASE = re.compile(
    r'(?:，)?(?:参见此图|可参见此图|可参照此图|如此图所示|'
    r'类似于此图|参考\s*此图|（此图）)(?:（图中为女性受虐者）)?'
)
DATE_DUP = re.compile(
    r'(?m)^(#[^\n]+)\n\n[0-9]{1,2} 月 [0-9]{1,2} 日[^\n]*\n'
)

STORY_REPLACEMENTS: list[tuple[str, str]] = [
    ('学姐的鞋底，学弟的天堂\n这是一个', '这是一个'),
    ('他彻底家境还算蛮不错', '他听说家境还算蛮不错'),
    ('半点前他刚搬进宿舍', '半年前他刚搬进宿舍'),
    ('没有个 keyholder', '没有个钥匙保管人'),
    ('一起去了一次 play party', '一起去了一次调教派对'),
    ('用脚魏麒的脑袋压到地上', '用脚把魏麒的脑袋压到地上'),
    ('低声答应到。', '低声答应道。'),
    ('用鞋间踢踹着', '用鞋尖踢踹着'),
    ('埋入魏麒本就瘦薄的里。', '埋入魏麒本就瘦薄的肉里。'),
    ('这里谁说的算', '这里谁说了算'),
    ('一切我说的算', '一切我说了算'),
    ('只想给给我当厕纸', '只想给我当厕纸'),
    ('我这才留意到到，', '我这才留意到，'),
    ('一边说，一遍轻轻', '一边说，一边轻轻'),
    ('随机赶紧补上', '随即赶紧补上'),
    ('魏麒的呃嘴里', '魏麒的嘴里'),
    ('一个多月了了吧', '一个多月了吧'),
    ('魏麒他的下体', '魏麒的下体'),
    ('让我东西来堵住止血', '让我拿东西来堵住止血'),
    ('和主人的的大便', '和主人的大便'),
    ('招呼到：', '招呼道：'),
    ('赞叹到：', '赞叹道：'),
    ('乞求到：', '乞求道：'),
    ('明算帐', '明算账'),
    ('我们吴小涵又拿过杯子', '吴小涵又拿过杯子'),
    ('终究是是很善良', '终究是很善良'),
    ('再这么说以后也还是不错的前途的', '再怎么说以后也还是不错的前途的'),
    ('我实在没用勇气答应', '我实在没有勇气答应'),
    ('搭到了我的膝盖上。"我低头', '搭到了我的膝盖上。我低头'),
    ('有点紧张的回应到。', '有点紧张地回应道。'),
    ('脚踝出还露出', '脚踝处还露出'),
    ('加完后乳酸亚铁后', '加完乳酸亚铁后'),
    ('然后又把命令我站起来', '然后又命令我站起来'),
    ('吓得感觉把前面趴低', '吓得赶忙把前面趴低'),
    ('把你当初一个低贱', '把你当成一个低贱'),
    ('JJ 会变小', '鸡鸡会变小'),
    ('要我 JJ 变得', '要我鸡鸡变得'),
    ('JJ 上已经被踩', '鸡鸡上已经被踩'),
    ('鸡鸡 会变小', '鸡鸡会变小'),
    ('要我 鸡鸡变得', '要我鸡鸡变得'),
    ('要我 鸡鸡 变得', '要我鸡鸡变得'),
    ('鸡鸡 上已经被踩', '鸡鸡上已经被踩'),
    ('才是真是的我呀', '才是真实的我呀'),
    ('让他能加饥渴', '让他更加饥渴'),
    ('悲摧状况', '悲催状况'),
    ('跪倒徐洋东面前', '跪到徐洋东面前'),
    ('这么样？魏麒听话吗', '怎么样？魏麒听话吗'),
    ('长大了嘴', '张大了嘴'),
    ('诱人的的甘露', '诱人的甘露'),
    ('不容置喙地语气', '不容置喙的语气'),
    ('以不容置喙的语气命令魏麒：“你，还是把衣服脱了，过来跪着吧”。',
     '以不容置喙的语气命令魏麒：“你，还是把衣服脱了，过来跪着吧。”'),
    ('他抽走魏麒脚下的小板凳', '她抽走魏麒脚下的小板凳'),
    ('吴小涵依然得以地创作着', '吴小涵依然得意地创作着'),
    ('长抒了一口气', '长舒了一口气'),
    ('就是切出来的腰花一样', '就像切出来的腰花一样'),
    ('用鞋底调拨起', '用鞋底挑拨起'),
    ('不要理我挣扎的，', '不要理我挣扎，'),
    ('我不可能允许你自己玷污你的。', '我不可能允许自己玷污你的。'),
    ('笨拙得解开', '笨拙地解开'),
    ('哈哈is', ''),
    ('你什么会选择魏麒', '你怎么会选择魏麒'),
    ('看到着两条规矩', '看到这两条规矩'),
    ('残忍的击扁', '残忍地击扁'),
    ('在魏麒期待的眼神用', '在魏麒期待的眼神中'),
    ('棕灰色的的登山靴', '棕灰色的登山靴'),
    ('命令魏麒给他换鞋', '命令魏麒给她换鞋'),
    ('要魏麒给他换上登山靴', '要魏麒给她换上登山靴'),
    ('铐到一起上', '铐到一起'),
    ('他也立刻嘴里还剩的粪便呛到', '他也立刻被嘴里还剩的粪便呛到'),
    ('魏麒说话，只是专心地舔舐', '魏麒不说话，只是专心地舔舐'),
    ('惨不忍睹的的鸡鸡', '惨不忍睹的鸡鸡'),
    ('里的的沙粒', '里的沙粒'),
    ('拖跩着疼', '拖拽着疼'),
    ('坡根凉鞋', '坡跟凉鞋'),
    ('钉子反正魏麒的睾丸上方', '钉子放在魏麒的睾丸上方'),
    ('乖巧得想一只狗', '乖巧得像一只狗'),
    ('穿着脱鞋的双脚', '穿着拖鞋的双脚'),
    ('抽搐了将六七秒钟', '抽搐了将近六七秒钟'),
    ('服服贴贴', '服服帖帖'),
    ('对这吴小涵身体里出来的圣水', '对吴小涵身体里出来的圣水'),
    ('连半点求饶的机会的没有', '连半点求饶的机会都没有'),
    ('嘴唇出的血', '嘴唇处的血'),
    ('扣和在一起', '扣合在一起'),
    ('她然后扭动旋钮通电', '然后扭动旋钮通电'),
    ('魏麒的越来越痛苦了', '魏麒越来越痛苦了'),
    ('痉挛使让床板', '痉挛让床板'),
    ('准备去厨房和弄点下午茶', '准备去厨房弄点下午茶'),
    ('跪着我面前', '跪在我面前'),
    ('你是不该主动请求人家使用厕所啊？', '你是不是该主动请求人家使用厕所啊？'),
]

EXTRA_DE_DEI: list[tuple[str, str]] = [
    ('疼的吸了一口', '疼得吸了一口'),
    ('疼的叫喊', '疼得叫喊'),
    ('疼的全身', '疼得全身'),
    ('疼的轻轻', '疼得轻轻'),
    ('疼的喊出', '疼得喊出'),
    ('疼的难以', '疼得难以'),
    ('惩罚地更重', '惩罚得更重'),
    ('吓的几乎', '吓得几乎'),
    ('吓的一动不动', '吓得一动不动'),
    ('吓的话也不敢', '吓得话也不敢'),
    ('累的面色', '累得面色'),
    ('累的坐倒', '累得坐倒'),
]

EXTRA_DI: list[tuple[str, str]] = [
    ('痛苦的坚持着', '痛苦地坚持着'),
    ('随意的羞辱我', '随意地羞辱我'),
]

EXTRA_FALSE_POSITIVE: list[tuple[str, str]] = [
    ('这样地回答', '这样的回答'),
    ('提问地回答', '提问的回答'),
    ('听到地回答', '听到的回答'),
    ('满意地回答，说道', '满意的回答，说道'),
    ('他地回答，', '他的回答，'),
    ('兴奋地吴小涵', '兴奋的吴小涵'),
    ('不屑地眼神', '不屑的眼神'),
    ('刚刚地描述', '刚刚的描述'),
]

SEQUEL_NOTE = (
    '# 续作\n\n'
    '续作《偏偏要做你的M》人物和剧情沿袭本作，尚未收录。\n'
)


def cut_after_comments(body: str) -> str:
    idx = body.find('# 续作')
    if idx < 0:
        idx = body.find('续作《偏偏要做你的')
    if idx < 0:
        return body.rstrip() + '\n\n' + SEQUEL_NOTE
    return body[:idx].rstrip() + '\n\n' + SEQUEL_NOTE


def drop_duplicate_title_and_dates(body: str) -> str:
    body = DATE_DUP.sub(r'\1\n\n', body)
    return body


def tidy_footnote_text(text: str) -> str:
    text = IMAGE_PHRASE.sub('', text)
    text = re.sub(r'效果参考\s*[；。]?', '', text)
    text = re.sub(r'^效果[；。]?', '', text)
    text = re.sub(r'（图中为女性受虐者）', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip(' ，；。').strip()


def convert_footnotes(body: str) -> str:
    parts = re.split(r'(?m)^(?=# )', body)
    out: list[str] = []
    fn_i = 0
    for part in parts:
        if not part.strip():
            continue
        lines = part.splitlines()
        defs: list[tuple[int, str]] = []
        keep_lines: list[str] = []
        for line in lines:
            match = FOOTNOTE_LINE.match(line.strip())
            if match:
                defs.append((int(match.group(1)), match.group(2)))
            else:
                keep_lines.append(line)
        chapter = '\n'.join(keep_lines).rstrip()
        if not defs:
            out.append(part.rstrip())
            continue
        mapping: dict[str, str] = {}
        def_lines: list[str] = []
        for num, raw in defs:
            cleaned = tidy_footnote_text(raw)
            if not cleaned:
                continue
            fn_i += 1
            key = str(num)
            fid = f'fn{fn_i}'
            mapping[key] = fid
            def_lines.append(f'[^{fid}]: {cleaned}。' if not cleaned.endswith('。') else f'[^{fid}]: {cleaned}')

        def replace_inline(match: re.Match[str]) -> str:
            digit = match.group(1)
            fid = mapping.get(digit)
            if not fid:
                return digit
            return f'[^{fid}]'

        chapter = INLINE_NOTE.sub(replace_inline, chapter)
        if def_lines:
            chapter = chapter.rstrip() + '\n\n' + '\n'.join(def_lines)
        out.append(chapter)
    return '\n\n'.join(out).strip() + '\n'


def tidy_comments(body: str) -> str:
    idx = body.find('# 评论')
    if idx < 0:
        return body
    head, comments = body[:idx], body[idx:]
    comments = comments.replace('# 评论\n\n评论\n', '# 评论\n\n')
    comments = re.sub(r'\n{3,}', '\n\n', comments)
    return head + comments


def main() -> None:
    raw = SOURCE.read_text(encoding='utf-8')
    _, raw_body = split_front_matter(raw)
    body = cut_after_comments(raw_body)
    body = drop_duplicate_title_and_dates(body)
    # Source numbered the needle-insert note as 3; the chapter list has it as 4.
    body = body.replace('插进去3——', '插进去4——')
    body = convert_footnotes(body)
    body = tidy_comments(body)
    body = fix_body(
        body,
        extra_replacements=STORY_REPLACEMENTS,
        extra_de_dei=EXTRA_DE_DEI,
        extra_di=EXTRA_DI,
        extra_false_positive_fixes=EXTRA_FALSE_POSITIVE,
    )
    # Needles that only exist after JJ→鸡鸡 / quote conversion.
    body = apply_replacements(body, STORY_REPLACEMENTS)
    body = MULTI_BLANK.sub('\n\n', body).strip() + '\n'
    leftover_jj = len(re.findall(r'(?<![A-Za-z])JJ(?![A-Za-z])', body))
    leftover_corner = body.count('「') + body.count('」')
    TARGET.write_text(FRONT + '\n' + body, encoding='utf-8')
    print(f'Wrote {TARGET.relative_to(ROOT)}')
    print_audit(body)
    print(f'  leftover JJ: {leftover_jj}')
    print(f'  leftover 「」: {leftover_corner}')
    print(f'  leftover 续作稿: {"偏偏要做你的 M》为本作的续作" in body}')


if __name__ == '__main__':
    main()

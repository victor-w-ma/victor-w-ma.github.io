#!/usr/bin/env python3
"""Shared post body formatting per AGENTS.md.

Per-story fix scripts import this module and pass story-specific replacements
via ``extra_replacements`` / ``extra_*`` kwargs.
"""

from __future__ import annotations

import re
from typing import Iterable

# AGENTS.md: pinyin abbreviations + common typos (longest first when applied).
COMMON_REPLACEMENTS: list[tuple[str, str]] = [
    ('KJ', '口交'),
    ('ML', '做爱'),
    ('JJ', '鸡鸡'),
    ('JB', '鸡巴'),
    ('BRA', '文胸'),
    ('SY', '手淫'),
    ('SHI', '屎'),
    ('P眼', '屁眼'),
    ('however', '然而'),
    ('鞭打她把', '鞭打她吧'),
    ('这个电子', '这个点子'),
    ('怕了过去', '爬了过去'),
    ('心致勃勃', '兴致勃勃'),
    ('喘了进去', '踹了进去'),
    ('一模原来', '一摸原来'),
    ('檫干净', '擦干净'),
    ('一楞', '一愣'),
    ('给给女主人', '给女主人'),
    ('女人人磕头', '女主人磕头'),
    ('没一下都', '每一下都'),
    ('不与干涉', '互不干涉'),
    ('椅子地下', '椅子底下'),
    ('告诉她她很喜欢', '告诉我她很喜欢'),
    ('两个的皮革物', '两个皮革物'),
    ('卫生间洗涮', '卫生间洗漱'),
]

# 「得」：动词/形容词 + 补语.
DE_DEI_REPLACEMENTS: list[tuple[str, str]] = [
    ('还看的过去', '还看得过去'),
    ('治的服服帖帖', '治得服服帖帖'),
    ('只觉的', '只觉得'),
    ('觉的自己', '觉着自己'),
    ('让她觉的自己', '让她觉着自己'),
    ('抱的更用力', '抱得更用力'),
    ('变的更加', '变得更加'),
    ('变的冷淡', '变得冷淡'),
    ('变的越来越', '变得越来越'),
    ('变的更加成熟', '变得更加成熟'),
    ('变的更加饥渴', '变得更加饥渴'),
    ('变的更加沉溺', '变得更加沉溺'),
    ('变的更加妖艳', '变得更加妖艳'),
    ('变的更加屈从', '变得更加屈从'),
    ('变的渐渐模糊', '变得渐渐模糊'),
    ('变的昏暗', '变得昏暗'),
    ('变的湿润', '变得湿润'),
    ('变的恐惧', '变得恐惧'),
    ('眼神变的', '眼神变得'),
    ('态度变的', '态度变得'),
    ('光线慢慢变的', '光线慢慢地变得'),
    ('视线变的', '视线变得'),
    ('眼眶已经变的', '眼眶已经变得'),
    ('高跟皮靴变的', '高跟皮靴变得'),
    ('面容都变的', '面容都变得'),
    ('堵的说不出', '堵得说不出'),
    ('扇的于琪昌', '扇得于琪昌'),
    ('扇的脑袋', '扇得脑袋'),
    ('踩的在', '踩得在'),
    ('虐的在', '虐得在'),
    ('弄的在', '弄得在'),
    ('踢的在', '踢得在'),
    ('踩的爆碎', '踩得爆碎'),
    ('踩的于琪昌', '踩得于琪昌'),
    ('踩的在地上', '踩得在地上'),
    ('踩的残破', '踩得残破'),
    ('跳的更厉害', '跳得更厉害'),
    ('看的于琪昌', '看得于琪昌'),
    ('看的冷瑞佳', '看得冷瑞佳'),
    ('看的于', '看得于'),
    ('熏的于琪昌', '熏得于琪昌'),
    ('熏的直', '熏得直'),
    ('踹的扑倒', '踹得扑倒'),
    ('踹的于琪昌', '踹得于琪昌'),
    ('踹的浑身上下', '踹得浑身上下'),
    ('踹的脑袋', '踹得脑袋'),
    ('踹的双脚', '踹得双脚'),
    ('踹的在地上', '踹得在地上'),
    ('疼的叫', '疼得叫'),
    ('疼的呜', '疼得呜'),
    ('疼的难以', '疼得难以'),
    ('疼的抽搐', '疼得抽搐'),
    ('疼的于', '疼得于'),
    ('气的跺', '气得跺'),
    ('气的于', '气得于'),
    ('吓的不', '吓得不'),
    ('吓的一', '吓得一'),
    ('吓的赶紧', '吓得赶紧'),
    ('吓的扔掉', '吓得扔掉'),
    ('吓的几个', '吓得几个'),
    ('吓的直', '吓得直'),
    ('吓的急忙', '吓得急忙'),
    ('吓的顿时', '吓得顿时'),
    ('吓的发', '吓得发'),
    ('吓的', '吓得'),
    ('显的', '显得'),
    ('变的', '变得'),
    ('变的一', '变得一'),
]

SPEECH_TAGS = (
    '说道|问道|答道|笑道|哭道|骂道|吼道|命令道|吩咐道|怒斥道|呵斥道|'
    '警告道|提醒道|分辩|分辨|叹息|补充|继续|推测|猜测|确认|否认|'
    '承认|拒绝|答应|请求|哀求|乞求|嘲弄|讥讽|解释|描述|叙述|回答|回应'
)

REDUPLICATION_DI = (
    '慢慢|快快|好好|牢牢|紧紧|深深|狠狠|重重|轻轻|偷偷|悄悄|默默|静静|'
    '渐渐|频频|常常|偏偏|单单|仅仅|猛然|骤然|明明|确确|直直|生生|硬硬|'
    '颤颤抖抖|哆哆嗦嗦|迷迷糊糊|浑浑噩噩|气哼哼|急吼吼|傻呆呆|愣愣'
)

ADVERB_DI = (
    '不好意思|无所谓的|笑嘻嘻|娇横|狂傲|狂荡|恣意|戏谑|愤愤|不屑|得意|'
    '紧张|慌乱|恐惧|胆怯|怯懦|屈辱|激动|努力|顺从|羞愧|凶狠|狠毒|'
    '暴怒|娇笑|坏笑|邪笑|狞笑|浪笑|淫笑|哀嚎|惨叫|讨好的|嘲弄|讥讽|'
    '傲慢|粗暴|恶毒|阴冷|森冷|冷酷|冷冷|暖暖|兴奋|放肆|肆意|恶狠狠|'
    '气哼哼|急吼吼|傻呆呆|愣愣|拼命|用力|随意|仔细|认真|疯狂|'
    '狠狠|重重|深深|紧紧|慢慢|牢牢|轻轻|偷偷|悄悄|默默|静静|'
    '颤颤抖抖|哆哆嗦嗦|迷迷糊糊|浑浑噩噩'
)

DI_REPLACEMENTS: list[tuple[str, str]] = [
    ('眼色不善的看', '眼色不善地看'),
    ('担忧的看', '担忧地看'),
    ('厌弃的看', '厌弃地看'),
    ('厌弃的擦', '厌弃地擦'),
    ('虐待的在', '虐待得在'),
    ('不由自主的向', '不由自主地向'),
    ('半推半就的从', '半推半就地从'),
    ('烦躁的将', '烦躁地将'),
    ('唯唯诺诺的将', '唯唯诺诺地将'),
    ('轻柔的将', '轻柔地将'),
    ('冷傲的将', '冷傲地将'),
    ('赤裸的跪', '赤裸地跪'),
    ('下贱的跪', '下贱地跪'),
    ('贪婪的咽', '贪婪地咽'),
    ('忙不迭的想', '忙不迭地想'),
    ('更加渴望的想', '更加渴望地想'),
    ('更加渴望的想要', '更加渴望地想要'),
    ('战战兢兢的跪', '战战兢兢地跪'),
    ('还乖乖的爬', '还乖乖地爬'),
    ('乖乖的躺', '乖乖地躺'),
    ('好好的躺', '好好地躺'),
    ('不知不觉的在', '不知不觉地在'),
    ('怯懦的抬', '怯懦地抬'),
    ('尴尬的站', '尴尬地站'),
    ('傻傻的坐', '傻傻地坐'),
    ('卑敬的跪', '卑敬地跪'),
    ('更加清晰一点的听', '更加清晰一点地听'),
    ('使劲的低', '使劲地低'),
    ('尽量的往', '尽量地往'),
    ('配合的向前', '配合地向前'),
]

FALSE_POSITIVE_FIXES: list[tuple[str, str]] = [
    ('发生明显得改变', '发生明显的改变'),
    ('一道明显得勒痕', '一道明显的勒痕'),
    ('很明显得看出', '很明显地看出'),
    ('太明显得感觉', '太明显的感觉'),
    ('明显得烧伤痕迹', '明显的烧伤痕迹'),
    ('残忍地暴君', '残忍的暴君'),
    ('恣意狂荡地娇笑声', '恣意狂荡的娇笑声'),
]


def split_front_matter(text: str) -> tuple[str, str]:
    """Return (yaml_block_with_trailing_newline, body)."""
    if not text.startswith('---'):
        return '', text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return '', text
    front = f'---{parts[1]}---\n'
    return front, parts[2].lstrip('\n')


def apply_replacements(text: str, pairs: Iterable[tuple[str, str]]) -> str:
    for old, new in sorted(pairs, key=lambda x: -len(x[0])):
        if old != new:
            text = text.replace(old, new)
    return text


def ascii_quotes_to_curly(body: str) -> str:
    out: list[str] = []
    open_quote = True
    for ch in body:
        if ch == '"':
            out.append('\u201c' if open_quote else '\u201d')
            open_quote = not open_quote
        else:
            out.append(ch)
    if not open_quote:
        raise ValueError('Unpaired ASCII double quote in body')
    return ''.join(out)


def normalize_ellipsis(text: str) -> str:
    return re.sub(r'\.{3,}', '……', text)


def fix_de_di_dei(
    body: str,
    *,
    extra_de_dei: Iterable[tuple[str, str]] | None = None,
    extra_di: Iterable[tuple[str, str]] | None = None,
    extra_false_positive_fixes: Iterable[tuple[str, str]] | None = None,
) -> str:
    de_dei = list(DE_DEI_REPLACEMENTS)
    if extra_de_dei:
        de_dei.extend(extra_de_dei)
    body = apply_replacements(body, de_dei)

    di = list(DI_REPLACEMENTS)
    if extra_di:
        di.extend(extra_di)
    body = apply_replacements(body, di)

    body = re.sub(
        rf'([\u4e00-\u9fff]{{1,12}})的({SPEECH_TAGS})',
        r'\1地\2',
        body,
    )
    body = re.sub(
        rf'({REDUPLICATION_DI})的([\u4e00-\u9fff])',
        r'\1地\2',
        body,
    )
    body = re.sub(
        rf'({ADVERB_DI})的([\u4e00-\u9fff])',
        r'\1地\2',
        body,
    )

    fixes = list(FALSE_POSITIVE_FIXES)
    if extra_false_positive_fixes:
        fixes.extend(extra_false_positive_fixes)
    body = apply_replacements(body, fixes)
    return body


def fix_common(
    body: str,
    *,
    extra_replacements: Iterable[tuple[str, str]] | None = None,
) -> str:
    pairs = list(COMMON_REPLACEMENTS)
    if extra_replacements:
        pairs.extend(extra_replacements)
    return apply_replacements(body, pairs)


def fix_body(
    body: str,
    *,
    extra_replacements: Iterable[tuple[str, str]] | None = None,
    extra_de_dei: Iterable[tuple[str, str]] | None = None,
    extra_di: Iterable[tuple[str, str]] | None = None,
    extra_false_positive_fixes: Iterable[tuple[str, str]] | None = None,
    fix_de_di: bool = True,
    fix_quotes: bool = True,
    fix_ellipsis: bool = True,
) -> str:
    body = body.replace('「', '"').replace('」', '"')
    body = fix_common(body, extra_replacements=extra_replacements)
    if fix_de_di:
        body = fix_de_di_dei(
            body,
            extra_de_dei=extra_de_dei,
            extra_di=extra_di,
            extra_false_positive_fixes=extra_false_positive_fixes,
        )
    if fix_quotes and '"' in body:
        body = ascii_quotes_to_curly(body)
    if fix_ellipsis:
        body = normalize_ellipsis(body)
    return body


def audit(body: str) -> dict[str, int]:
    """Return counts for common residual issues (lower is better)."""
    return {
        'ASCII " in body': body.count('"'),
        'JB': body.count('JB'),
        '轮歼': body.count('轮歼'),
        '表子': body.count('表子'),
        '吓的': body.count('吓的'),
        '变的': body.count('变的'),
        '的(说道)': len(re.findall(r'的(说道|问道|答道)', body)),
        '只觉的': body.count('只觉的'),
    }


def print_audit(body: str) -> None:
    for name, count in audit(body).items():
        print(f'  {name}: {count}')

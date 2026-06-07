#!/usr/bin/env python3
"""Process mrs-zhao.md for publishable format per AGENTS.md (keep unpublished filename)."""

from __future__ import annotations

import re
from pathlib import Path

POST_PATH = Path(__file__).resolve().parents[1] / '_posts' / 'backlog' / 'mrs-zhao.md'
TITLE = '赵女士'

# Order matters: longer / more specific patterns first.
REPLACEMENTS = [
    ('尝尝会', '常常会'),
    ('尝尝谈及', '常常谈及'),
    ('正式她的老公', '正是她的老公'),
    ('拒她透露', '据她透露'),
    ('不吭不卑', '不卑不亢'),
    ('惹的群里', '惹得群里'),
    ('雅雀无声', '鸦雀无声'),
    ('赞新的人', '崭新的人'),
    ('气势汹汹的像我', '气势汹汹的向我'),
    ('显示是她觉得', '现实是她觉得'),
    ('坚硬入柱', '坚硬如柱'),
    ('不肯讲脸', '不肯将脸'),
    ('没一小会', '没一会儿'),
    ('引道，对不起', '阴道，对不起'),
    ('因部', '阴部'),
    ('查爱', '做爱'),
    ('精亵', '精液'),
    ('精叶', '精液'),
    ('精夜', '精液'),
    ('精y', '精液'),
    ('jy', '精液'),
    ('撸she', '撸射'),
    ('撸管she', '撸管射'),
    ('she了一次', '射了一次'),
    ('she拍照', '射拍照'),
    ('she出的', '射出的'),
    ('she了之后', '射了之后'),
    ('she自己', '射自己'),
    ('she一塌糊涂', '射一塌糊涂'),
    ('she在上面', '射在上面'),
    ('没p过的', '没p过的'),  # keep; fix 没p过 separately if needed
    ('没p过', '没p过'),
    ('p过的照片', '没p过的照片'),
    ('j8', '鸡巴'),
    ('狗几把', '狗鸡巴'),
    ('小几把', '小鸡巴'),
    ('几把', '鸡巴'),
    ('狗j', '狗鸡'),
    ("男人的j瞬间", '男人的鸡巴瞬间'),
    ('块到边缘', '快到边缘'),
    ('长大嘴', '张大嘴'),
    ('不关系她', '不关心她'),
    ('普通一下跪', '扑通一下跪'),
    ('公调要', '公调要'),
    ('制定的地方', '指定的地方'),
    ('没么有', '从来没有'),
    ('赛过臭丝袜', '塞过臭丝袜'),
    ('从来么有', '从来没有'),
    ('调教你把', '调教你吧'),
    ('没一下都', '每一下都'),
    ('趋之著警', '趋之若鹜'),
    ('梦寐求的归属', '梦寐以求的归属'),
    ('相兰虚弱', '相当虚弱'),
    ('同候', '伺候'),
    ('窝表', '窝囊'),
    ('欣裳着', '欣赏着'),
    ('裳给你', '赏给你'),
    ('尊表', '尊贵'),
    ('差辱', '羞辱'),
    ('董金', '黄金'),
    ('女5', '女王'),
    ('做i的', '做爱的'),
    ('做i，', '做爱，'),
    ('做i ', '做爱 '),
    ('迈)的', '迈入的'),
    ('外因', '外阴'),
    ('阴第', '阴蒂'),
    ('音盒', '阴户'),
    ('被埴满', '被填满'),
    ('抽似的的', '抽搐似的'),
    ('闹弄着', '蠕动着'),
    ('扣号了', '扣好了'),
    ('现实用手指', '先是用手指'),
    ('滩烂泥', '一滩烂泥'),
    ('嗉了一口', '嗦了一口'),
    ('颠要了我', '颠覆了我'),
    ('羞要着我', '羞辱着我'),
    ('无暇估计', '无暇顾及'),
    ('路管道权利', '撸管的权利'),
    ('用巴来', '用嘴来'),
    ('没一个中用的', '没有一个中用的'),
    ('室不犹豫', '毫不犹豫'),
    ('僭越了', '僭越了'),
    ('颤颜疑巍', '颤颤巍巍'),
    ('咄咄通人', '咄咄逼人'),
    ('争忘', '争忘'),  # 遗忘? context 忘带了
    ('率先进来', '率先进来'),  # ok
    ('一幅半框', '一副半框'),
    ('关山了门', '关上了门'),
    ('说到，', '说道，'),
    ('东东，', '东西，'),
    ('短息告诉', '短信告诉'),
    ('磨磨唧唧', '磨磨蹭蹭'),
    ('女孩书房的', '女孩书房的'),
    ('装作一幅', '装作一副'),
    ('引狼入室', '引狼入室'),
    ('表着', '裹着'),
    ('半惜通', '半苏醒'),
    ('裳你的', '赏你的'),
    ('便宣你', '便宴你'),  # 便宴? context 怠慢你
    ('便宣你了', '怠慢你了'),
    ('便宣你', '怠慢你'),
    ('喂"，', '嗯"，'),
    ('嗯喂', '嗯嗯'),
    ('姜掉', '僵掉'),
    ('表得', '表现得'),
    ('she在上面拍', '射在上面拍'),
    ('完食了', '完食了'),  # keep 完食 as author term
    ('野m听', '野M听'),
    ('野m，', '野M，'),
    ('那个野m', '那个野M'),
    ('收费s', '收费S'),
    ('收费女s', '收费女S'),
    ('友情s', '友情S'),
    ('女s般的', '女S般的'),
    ('女s指挥', '女S指挥'),
    ('女s让', '女S让'),
    ('女s，', '女S，'),
    ('女s。', '女S。'),
    ('女s ', '女S '),
    ('一个女s', '一个女S'),
    ('作为女s', '作为女S'),
    ('做女s', '做女S'),
    ('当女s', '当女S'),
    ('找女s', '找女S'),
    ('收费女s', '收费女S'),
    (' sm ', ' SM '),
    ('sm观', 'SM观'),
    ('sm论坛', 'SM论坛'),
    ('sm俱乐部', 'SM俱乐部'),
    ('sm片', 'SM片'),
    ('sm的', 'SM的'),
    ('sm，', 'SM，'),
    ('sm。', 'SM。'),
    ('sm ', 'SM '),
    ('sm/', 'SM/'),
    ('sm\n', 'SM\n'),
    ('tui"', '呸"'),
    ('tui你个', '呸你个'),
    ('，tui', '，呸'),
    ('懂吗？tui', '懂吗？呸'),
    ('懂吗? tui', '懂吗？呸'),
    ('射经结束', '射精结束'),
    ('社恐认识', '社恐使然'),
    ('想被饿了几天的狗', '像被饿了几天的狗'),
    ('尝尝能梦到', '常常能梦到'),
    ('大量着什么', '打量着什么'),
    ('串到了小仓库', '窜到了小仓库'),
    ('好不忌讳的', '毫不忌讳的'),
    ('和通女儿出去', '和同女儿出去'),
    ('她把叽叽放在', '她把鸡鸡放在'),
    ('再我快要', '在我快要'),
    ('似不是我', '是不是我'),
    ('显示去调教', '现实去调教'),
    ('尝尝嗤之以鼻', '常常嗤之以鼻'),
    ('收费:', '收费S'),
    ('尊表的黄金', '尊贵的黄金'),
    ('不思声色', '不动声色'),
    ('遮住眼镜', '遮住眼睛'),
    ('乘了慢慢一勺子', '盛了满满一勺子'),
    ('没一小会', '没一会儿'),
    ('一小会，', '一会儿，'),
    ('不想问道', '不想闻到'),
    ('做不死我', '坐死我'),
    ('给的与他', '给予他'),
    ('沟在了', '勾在了'),
    ('长大嘴等着', '张大嘴等着'),
    ('玩的很畅快', '玩得很畅快'),
    ('说的没错', '说得没错'),
    ('听的我', '听得我'),
    ('看的出来', '看得出来'),
    ('再我看来', '在我看来'),
    ('尝尝会', '常常会'),
    ('只有有一个', '只要有一个'),
    ('持续多就', '持续多久'),
    ('想狗一样', '像狗一样'),
    ('我想狗一样', '我像狗一样'),
    ('穿在自己的较少', '穿在自己的脚上'),
    ('转退了出去', '转身退了出去'),
    ('争忘', '遗忘'),
    ('颜抖', '颤抖'),
    ('不懂声色', '不动声色'),
    ('建业的学生', '毕业的学生'),
    ('表得', '表现得'),
    ('姜掉', '僵掉'),
    ('she在上面', '射在上面'),
    ('最为一个', '作为一个'),
    ('飙自己的', '飙自己的'),  # 表演→保留
    ('骂道我自己', '骂到我自己'),
    ('颠要', '颠覆'),
    ('羞要着我', '羞辱着我'),
    ('路管道', '撸管'),
    ('做功课', '做功课'),
    ('窝妻', '窝囊'),
    ('妒忌', '嫉妒'),
    ('室不犹豫', '毫不犹豫'),
    ('一幅', '一副'),
    ('说到，', '说道，'),
    ('关山了', '关上了'),
    ('短息', '短信'),
    ('磨磨唧唧', '磨磨蹭蹭'),
    ('装作一幅', '装作一副'),
    ('率先进来', '率先进来'),
    ('精后', '射精后'),
    ('jj，', '鸡巴，'),
    ('jj ', '鸡巴 '),
    ('t露的', '裸露的'),
    ('强j', '强奸'),
    ('没p过的', '没p过的'),
]

CHAPTER_MARKER_RE = re.compile(
    r'^=+\s*(?:'
    r'9\.15更新|9\.15下午更新|9\.18日?更新|10\.4更新|10\.15日?更新|'
    r'11\.29更新|12\.1更新第八章|12\.4更新\s*第(\d+)章|12\.4日?更新第(\d+)章|'
    r'12\.19更新\s*第(\d+)章|12\.20更新第(\d+)章|'
    r'1\.17更新第(\d+)章|1\.18更新第(\d+)章|5\.1更新'
    r')\s*=+$'
)

DROP_LINES = {
    '本来不想分p的，结果临时有事，剩下的只能放在后面写了',
    '该章为剧情过度，没有撸点',
}

SCENE_HEADER_RE = re.compile(r'^["\u201c]([^"\u201d]+)["\u201d]\s*$')


def convert_quotes(text: str) -> str:
    """Convert ASCII double quotes in body to Chinese curly quotes."""
    result = []
    use_left = True
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '"':
            result.append('\u201c' if use_left else '\u201d')
            use_left = not use_left
            i += 1
        else:
            result.append(ch)
            i += 1
    return ''.join(result)


def process_chapter_line(line: str) -> str | None:
    """Return markdown chapter header or None to drop line."""
    m = CHAPTER_MARKER_RE.match(line.strip())
    if m:
        groups = [g for g in m.groups() if g]
        if groups:
            return f'# 第{groups[0]}章'
        if '第八章' in line:
            return '# 第8章'
        return None
    if line.strip() in DROP_LINES:
        return None
    if re.match(r'^第(\d+)章[，,]?\s*$', line.strip()):
        num = re.match(r'^第(\d+)章', line.strip()).group(1)
        return f'# 第{num}章'
    scene = SCENE_HEADER_RE.match(line.strip())
    if scene:
        return f'## {scene.group(1)}'
    # bare scene labels without quotes
    bare_scenes = {'客厅中', '回到卧室', '笼子里', '赵女士家中'}
    if line.strip() in bare_scenes:
        return f'## {line.strip()}'
    if line.strip() == '机场内"':
        return '## 机场内'
    if line.strip() == '"门的另一边"':
        return '## 门的另一边'
    return line


def ensure_paragraph_indent(line: str) -> str:
    """Ensure narrative paragraphs start with fullwidth indent."""
    stripped = line.strip()
    if not stripped:
        return ''
    if stripped.startswith('#'):
        return stripped
    if stripped.startswith('(全文完)'):
        return stripped
    if not stripped.startswith('\u3000\u3000'):
        return '\u3000\u3000' + stripped
    return line.rstrip()


def main() -> None:
    raw = POST_PATH.read_text(encoding='utf-8')
    if raw.startswith('---\n'):
        body = raw.split('---\n', 2)[2] if raw.count('---\n') >= 2 else raw
    else:
        body = raw

    lines = body.splitlines()
    out_lines: list[str] = []
    prev_blank = True

    for line in lines:
        processed = process_chapter_line(line)
        if processed is None:
            continue
        processed = processed
        for old, new in REPLACEMENTS:
            processed = processed.replace(old, new)

        if processed.startswith('#'):
            if out_lines and out_lines[-1] != '':
                out_lines.append('')
            out_lines.append(processed)
            out_lines.append('')
            prev_blank = True
            continue

        processed = ensure_paragraph_indent(processed)
        if processed == '':
            if not prev_blank:
                out_lines.append('')
                prev_blank = True
            continue
        out_lines.append(processed)
        prev_blank = False

    # Collapse 3+ blank lines to 2
    collapsed: list[str] = []
    blank_run = 0
    for line in out_lines:
        if line == '':
            blank_run += 1
            if blank_run <= 2:
                collapsed.append('')
        else:
            blank_run = 0
            collapsed.append(line)

    body_text = convert_quotes('\n'.join(collapsed).strip() + '\n')

    # Ensure every narrative paragraph has fullwidth indent.
    fixed_lines = []
    for line in body_text.splitlines():
        if line.strip() and not line.strip().startswith('#') and not line.startswith('\u3000\u3000'):
            fixed_lines.append('\u3000\u3000' + line.strip())
        elif line.strip():
            fixed_lines.append(line.rstrip())
        else:
            fixed_lines.append('')
    body_text = '\n'.join(fixed_lines).strip() + '\n'

    front_matter = f'''---
layout: post
title: "{TITLE}"
---

'''
    POST_PATH.write_text(front_matter + body_text, encoding='utf-8')

    content = body_text
    checks = {
        'ascii_double_quote': content.count('"'),
        'jy': len(re.findall(r'\bjy\b', content, re.I)),
        'j8': content.count('j8'),
        '几把': content.count('几把'),
        '精y': content.count('精y'),
        'she': len(re.findall(r'\bshe\b', content, re.I)),
        'update_markers': len(re.findall(r'^=+.*更新', content, re.M)),
    }
    print('Wrote', POST_PATH)
    for key, val in checks.items():
        print(f'  {key}: {val}')


if __name__ == '__main__':
    main()

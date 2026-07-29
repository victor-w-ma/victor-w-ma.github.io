#!/usr/bin/env python3
"""Import and format 大学情侣主羞辱 from mirror.chromaso fetch."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from post_format import fix_body, print_audit, split_front_matter  # noqa: E402

FETCH = Path(
    '/home/ubuntu/.cursor/projects/workspace/agent-tools/'
    'f0d32682-c66b-4335-bdcc-4a60c96ae8a1.txt'
)
OUT = ROOT / '_posts' / '2026-07-29-university-couple-humiliation.md'

SCENE_BREAKS = [
    '言归正传。',
    '大二下学期，我跟第二任女友分手了',
    '将近期末的时候',
    '晚上，我一个人去了综合楼。',
    '很快，楼道里传来了皮靴的声音',
    '那天晚上，我被折磨得浑身散架了',
    '转眼到了期末。',
    '正想着，手机来信息了。',
    '我仓皇地回到寝室',
    '到第五天的晚上',
    '我跑到君爱旅馆',
    '上到13楼，进了房间。',
    '毫无征兆地，雯突然拿开雷的手',
    '吧嗒一声，门关了。',
    '没过多久，吱呀一声，套间的大门开了',
]


def extract_raw(text: str) -> str:
    start = text.find('我大学是在一所偏向理工类的大学里念的')
    end = text.find('favorite_border')
    if start < 0 or end < 0 or end <= start:
        raise SystemExit('Could not locate story body in fetch file')
    return text[start:end].strip()


def strip_forum_noise(body: str) -> str:
    for w in ('本文来自', '内容来自', 'copyright', 'Copyright', 'COPYRIGHT'):
        body = body.replace(w, '')
    fixed_removals = [
        '本文来自',
        '/H',
        "# T' k7 Z- y, M9 R l",
        '% Q8',
        '1-老公你真坏0',
        "8i'",
        '^-^',
        '-^',
        '% X9 z6 [- Q1 q',
        "7 _' w$ j- V8 j5 x9 ]",
        '1 r# P8 Y0 T4 ]',
        '" Q" |. ]& F: h2 h+ L',
        r"! \4 m( D5 Z: b1 U",
        "' [, G% [1 k- l$ J1 N$ w/ \\",
        '% C/ w% K) b7 L; h) z9 x+ @',
        '& q: b; c" L,r" a% w',
        ') m!',
        "* V$ B1 r' M* O5 ]% ~",
        '" C6g$ }0 z& v2 c',
        ', }',
        ') H ^( |*n& `4 v7 Z+ M4 {',
        ': q',
        '*^',
        '# `1 {6 N2 e- H* W',
        '& l6 O. c+ B: W5 f',
        '8 K3 K* g" ?. r* |; W0 k; k% f# g. w% Z',
        ') b%',
        '!^',
        ' $ }',
    ]
    for s in fixed_removals:
        body = body.replace(s, '')
    # Lone junk symbols between/after CJK.
    body = re.sub(
        r'(?<=[\u4e00-\u9fff，。！？：；、…—”\"])[!#*$%&+=^~|\\\\]+(?=[\u4e00-\u9fff“\"])',
        '',
        body,
    )
    body = re.sub(
        r'(?<=[\u4e00-\u9fff，。！？：；、…—”])[!#*$%&+=^~|\\\\]+',
        '',
        body,
    )
    body = body.replace('`', '')
    # bbs numeric prefixes before dialogue/narrative (not heights like 165左右).
    body = re.sub(r'(?<=[。！？…])\d+(?=[“"我他她威雯雷师])', '', body)
    # Leading junk before 转眼/我忐忑/到第五天/身份证 etc.
    body = body.replace('^转眼', '转眼')
    body = body.replace('?我忐忑', '我忐忑')
    body = body.replace('{到第五天', '到第五天')
    body = body.replace('l“身份证', '“身份证')
    body = body.replace('.“艹你丫的', '“艹你丫的')
    body = body.replace('U太屈辱', '太屈辱')
    body = body.replace('n“那么舒服', '“那么舒服')
    body = body.replace('a“我试过', '“我试过')
    body = body.replace('q雯的长发', '雯的长发')
    body = body.replace('8我爬过去', '我爬过去')
    body = body.replace('7我在师姐', '我在师姐')
    body = body.replace('7“艹你丫的', '“艹你丫的')
    body = body.replace('0房间里', '房间里')
    body = body.replace('~我听到', '我听到')
    body = body.replace('; 本文来自', '')
    body = body.replace(';本文来自', '')
    return body


def dedupe_block(body: str) -> str:
    """Remove the duplicated shoe-licking setup paragraph."""
    marker = (
        '我都能闻到他胯下散发出的雄性的味道。我觉得羞辱得无以复加了。'
        '这时，他说，你TM个小挫个'
    )
    first = body.find(marker)
    if first < 0:
        return body
    second = body.find(marker, first + 10)
    if second < 0:
        return body
    first_lick = body.find('我没办法，只好俯下身子，伸出舌头。', first)
    keep_resume = body.find('他穿着大概47码的黑色篮球鞋。', second)
    if first_lick < 0 or keep_resume < 0:
        return body
    first_lick_end = first_lick + len('我没办法，只好俯下身子，伸出舌头。')
    return body[:first_lick_end] + body[keep_resume:]


def fix_stray_ascii_quotes(body: str) -> str:
    body = body.replace('”"', '”')
    body = body.replace('“"', '“')
    body = body.replace('""', '')
    body = re.sub(r'([。！？…])"([\u4e00-\u9fff])', r'\1\2', body)
    body = re.sub(r'(”)"([“\u4e00-\u9fff])', r'\1\2', body)
    body = re.sub(r'(”)"(\s)', r'\1\2', body)
    if body.count('"') % 2 == 1:
        body = body.replace('"', '')
    return body


EXTRA_REPLACEMENTS: list[tuple[str, str]] = [
    ('什幺', '什么'),
    ('那幺', '那么'),
    ('怎幺', '怎么'),
    ('多幺', '多么'),
    ('这幺', '这么'),
    ("YIN'JING", '阴茎'),
    ('YIN蒂', '阴蒂'),
    ('YIN唇', '阴唇'),
    ('YIN道', '阴道'),
    ('YIN水', '阴水'),
    ("ZUO'AI", '做爱'),
    ('做AI', '做爱'),
    ('射JING', '射精'),
    ('XING交', '性交'),
    ('XXOO', '做爱'),
    ('小DD', '小鸡鸡'),
    ('我的DD', '我的鸡鸡'),
    ('的DD', '的鸡鸡'),
    ('小jj', '小鸡鸡'),
    ('小JJ', '小鸡鸡'),
    ('你TM', '你他妈'),
    ('真tm', '真他妈'),
    ('谁tm', '谁他妈'),
    ('真TM', '真他妈'),
    ('装什么B', '装什么逼'),
    ('装什幺B', '装什么逼'),
    ('在这B扯扯', '在这逼扯扯'),
    ('女人B', '女人逼'),
    ('别的女人的B', '别的女人的逼'),
    ('BB啥', '逼逼啥'),
    ('酿呛', '踉跄'),
    ('丝豪', '丝毫'),
    ('吼到，', '吼道，'),
    ('轻蔑地回到，', '轻蔑地回道，'),
    ('开导到。', '开导道。'),
    ('撒娇到。', '撒娇道。'),
    ('雯撒娇到，', '雯撒娇道，'),
    ('喃喃地说到。', '喃喃地说道。'),
    ('呻吟到。', '呻吟道。'),
    ('呻吟到，', '呻吟道，'),
    ('允吸', '吮吸'),
    ('血脉愤张', '血脉贲张'),
    ('剧烈运抵', '剧烈运动'),
    ('太挌了', '太硌了'),
    ('把他打到。', '把他打倒。'),
    ('提了提来', '提了起来'),
    ('虚弱到几点', '虚弱到极点'),
    ('雷着，一把抱起雯', '雷说着，一把抱起雯'),
    ('四双脱鞋', '四双拖鞋'),
    ('把脱鞋拿进来', '把拖鞋拿进来'),
    ('威的脱鞋', '威的拖鞋'),
    ('雷的脱鞋', '雷的拖鞋'),
    ('送了脱鞋上来', '送了拖鞋上来'),
    ('为他们的姓生活', '为他们的性生活'),
    ('「悟道」了我，', '「悟道」了的我，'),
    ('亲爱地，你看', '亲爱的，你看'),
    ('雷跟雯做在另一边', '雷跟雯坐在另一边'),
    ('她楞了一下', '她愣了一下'),
    ('我楞了一下', '我愣了一下'),
    ('同时还他们学院', '同时还是他们学院'),
    ('将近期末的时，', '将近期末的时候，'),
    ('带了给我强烈', '带给我强烈'),
    ('我感觉了恐惧', '我感觉到了恐惧'),
    ('绕了小的这回', '饶了小的这回'),
    ('服软地那么快', '服软得那么快'),
    ('服软地那幺快', '服软得那么快'),
    ('挣开你的屁眼', '睁开你的眼睛'),
    ('回媚轻轻一笑', '回眸轻轻一笑'),
    ('她男朋走到', '她男朋友走到'),
    ('冰冰冷冷的话', '冷冰冰的话'),
    ('直翻恶心', '直犯恶心'),
    ('外表起来那么', '外表看起来那么'),
    ('外表起来那幺', '外表看起来那么'),
    ('内裤的的里面', '内裤的里面'),
    ('兴奋地女人', '兴奋的女人'),
    ('不忍心让你让你爬', '不忍心让你爬'),
    ('哪个女生那么以前过得那么悲催', '哪个女生以前过得那么悲催'),
    ('哪个女生那幺以前过得那幺悲催', '哪个女生以前过得那么悲催'),
    ('净是在如此田地', '竟是在如此田地'),
    ('嘴角向我着努', '嘴角向我努'),
    ('做地很自然', '做得很自然'),
    ('它是在太大了', '它实在太大了'),
    ('越来越在直接', '越来越直接'),
    ('别舔了，不过女人都浪费了。', '别舔了，你做女人都浪费了。'),
    ('湿淋淋地下体蹭着我的我脸', '湿淋淋的下体蹭着我的脸'),
    ('一巴掌乎我脑袋', '一巴掌呼我脑袋'),
    ('伸出舌头进往她肛门', '伸出舌头往她肛门'),
    ('以及让他充满的欲望', '已经让他充满了欲望'),
    ('现在她却这个亲热地叫雷', '现在她却这么亲热地叫雷'),
    ('把嘴张大最大', '把嘴张到最大'),
    ('硬邦邦湿漉漉地粗长', '硬邦邦湿漉漉的粗长'),
    ('浓稠地粘液', '浓稠的黏液'),
    ('臭烘烘地屁眼', '臭烘烘的屁眼'),
    ('强烈地脚臭味', '强烈的脚臭味'),
    ('强烈地粪便味', '强烈的粪便味'),
    ('一股强烈地做爱后', '一股强烈的做爱后'),
    ('熟悉地骚动感', '熟悉的骚动感'),
    ('熟悉地，考试时', '熟悉的，考试时'),
    ('体会地一清二楚', '体会得一清二楚'),
    ('冷静地可怕', '冷静得可怕'),
    ('绝对地人迹罕至', '绝对人迹罕至'),
    ('强烈地羞辱', '强烈的羞辱'),
    ('火辣辣地摩擦地疼痛', '火辣辣的摩擦疼痛'),
    ('有种很明显地感觉', '有种很明显的感觉'),
    ('潮乎乎地粪便味', '潮乎乎的粪便味'),
    ('强烈地下体气味', '强烈的下体气味'),
    ('强烈地性的气息', '强烈的性的气息'),
    ('强烈地性刺激', '强烈的性刺激'),
    ('模糊不清地声音', '模糊不清的声音'),
    ('粗重地喘息声', '粗重的喘息声'),
    ('极度地羞辱', '极度的羞辱'),
    ('极度地受辱', '极度的受辱'),
    ('光溜溜地身体', '光溜溜的身体'),
    ('赤裸地躯体', '赤裸的躯体'),
    ('卑贱地人格', '卑贱的人格'),
    ('淡淡地女生下体', '淡淡的女生下体'),
    ('兴致高涨地情侣', '兴致高涨的情侣'),
    ('前所未有地大', '前所未有的大'),
    ('充满着羞耻地进入', '充满羞耻地进入'),
    ('自卑地内心', '自卑的内心'),
    ('点点滴滴地都是', '点点滴滴都是'),
    ('心里极其地酸', '心里极其酸'),
    ('雷强有力地脚', '雷强有力的脚'),
    ('铺天盖地地自卑感', '铺天盖地的自卑感'),
    ('点点滴滴地爱液', '点点滴滴的爱液'),
    ('淡淡地女性下体', '淡淡的女性下体'),
    ('兹兹地吻', '滋滋地吻'),
    ('含糊不清地低吼', '含糊不清的低吼'),
    ('剧烈地高潮', '剧烈的高潮'),
    ('扭得好像要脱臼一样地疼', '扭得好像要脱臼一样疼'),
    ('内心扭曲地欲望', '内心扭曲的欲望'),
    ('我笨拙地动作', '我笨拙的动作'),
    ('双手被反绑在背后地一点点', '双手被反绑在背后，一点点'),
    ('结实地臀部', '结实的臀部'),
    ('那人立刻说道，老师，没事，没事，我来处理。.然后',
     '那人立刻说道，老师，没事，没事，我来处理。然后'),
    ('不就仗着白天老师们都在嘛他直接',
     '不就仗着白天老师们都在嘛。他直接'),
    ('我顿时行动极其不便只能任人摆布了。',
     '我顿时行动极其不便，只能任人摆布了。'),
    ('你就要跟我老公的屎为伍拉哈哈哈',
     '你就要跟我老公的屎为伍啦，哈哈哈。'),
    ('盯视着我他们走了过去。', '盯视着我。他们走了过去。'),
    ('他们兹兹地吻了起来。我越吻越起劲。',
     '他们滋滋地吻了起来。我越舔越起劲。'),
    ('搞得我老婆都受不了。突然停止动作的我有点失落。',
     '搞得我老婆都受不了。”突然停止动作的我有点失落。'),
    ('让那个贱逼嘴给你舔射精吧。” 师姐说道“去，舔',
     '让那个贱逼嘴给你舔射精吧。”师姐说道。“去，舔'),
    ('我觉得他要干穿我的脑袋幸好不到五分钟',
     '我觉得他要干穿我的脑袋。幸好不到五分钟'),
    ('随即响起了哗啦啦的水声跟他们的调笑声过了一小会',
     '随即响起了哗啦啦的水声跟他们的调笑声。过了一小会'),
    ('心里的滋味简直无以名状我的舌头碰到',
     '心里的滋味简直无以名状。我的舌头碰到'),
    ('嘲弄地话语', '嘲弄的话语'),
    ('门‘吱呀’一声开了。', '门“吱呀”一声开了。'),
    ('每次听到‘女人味’', '每次听到“女人味”'),
    ('说‘坏蛋、讨厌’', '说“坏蛋、讨厌”'),
    ('我说，‘你个挫逼', '我说，“你个挫逼'),
    ('‘YIN蒂大，性欲强’', '“阴蒂大，性欲强”'),
    ('你‘铺床’', '你“铺床”'),
    ('Party', '派对'),
    ('爽到high了', '爽到嗨了'),
    ('看AV', '看黄片'),
    ('很像OL', '很像职业装'),
    ('有C+', '有C罩杯以上'),
    ('帮XXX交', '帮某某交'),
    ('。。', '……'),
]


def insert_paragraphs(body: str) -> str:
    for marker in SCENE_BREAKS:
        body = body.replace(marker, '\n\n' + marker)
    # Milder breaks: only after 。！？ when next clause starts a clear shift.
    body = re.sub(
        r'([。！？…])(那天|很快|突然|随后|于是|接着|过了|这时|此时|转眼|晚上|正想着|'
        r'我满心|我习惯|我一定|我仓皇|我跑到|我不安|我在大厅|上到|家庭套房|'
        r'毫无征兆|吧嗒|没过多久|空气凝固|雯也看到|师姐边说|师姐继续|'
        r'我不敢违抗|我心里很难受|我满心仇恨)',
        r'\1\n\n\2',
        body,
    )
    # Also break before long quoted commands that start new beats.
    body = re.sub(r'([。！？…])(“(?:老公|喂|傻逼|贱逼|脱|跪|过来|舔|爬))', r'\1\n\n\2', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = re.sub(r'[ \t]+\n', '\n', body)
    body = re.sub(r'\n[ \t]+', '\n', body)
    # Keep paragraphs from becoming one endless line: soft-wrap every ~2-4 sentences
    # by breaking after 。 when paragraph chunk > 180 chars without break.
    parts = body.split('\n\n')
    new_parts: list[str] = []
    for part in parts:
        if len(part) < 220:
            new_parts.append(part.strip())
            continue
        buf = ''
        sentences = re.split(r'(?<=[。！？…])', part)
        chunk = ''
        for s in sentences:
            if not s:
                continue
            if chunk and len(chunk) + len(s) > 180:
                buf += chunk.strip() + '\n\n'
                chunk = s
            else:
                chunk += s
        if chunk.strip():
            buf += chunk.strip()
        new_parts.extend(p for p in buf.split('\n\n') if p.strip())
    body = '\n\n'.join(new_parts)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip() + '\n'


def clean(body: str) -> str:
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    body = re.sub(r'\n+', ' ', body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = strip_forum_noise(body)
    body = dedupe_block(body)
    body = fix_stray_ascii_quotes(body)
    # Normalize curly single quotes used as doubles before shared fixer.
    body = body.replace('‘', '"').replace('’', '"')
    body = fix_body(
        body,
        extra_replacements=EXTRA_REPLACEMENTS,
        fix_quotes=True,
        fix_de_di=True,
        fix_ellipsis=True,
    )
    # Second pass for leftovers (JB/JJ after first common pass ordering).
    body = fix_body(
        body,
        extra_replacements=[
            ('JB', '鸡巴'),
            ('JJ', '鸡鸡'),
            ('jj', '鸡鸡'),
            ('TM', '他妈'),
            ('tm', '他妈'),
            ('射JING', '射精'),
            ('做AI', '做爱'),
        ],
        fix_quotes=False,
        fix_de_di=True,
        fix_ellipsis=True,
    )
    # Undo over-eager AI wipe if it hit legitimate Latin — none expected in body.
    body = insert_paragraphs(body)
    return body


def main() -> None:
    raw = FETCH.read_text(encoding='utf-8')
    body = clean(extract_raw(raw))
    # Safety: never blank critical terms.
    for need in ('鸡巴', '鸡鸡', '165', '169', '172', '13楼', '47码'):
        if need not in body:
            print(f'WARNING missing {need!r}')
    text = '---\nlayout: post\ntitle: "大学情侣主羞辱"\n---\n\n' + body
    OUT.write_text(text, encoding='utf-8')
    _, audit_body = split_front_matter(text)
    print(f'Wrote {OUT} ({len(audit_body)} chars body, {audit_body.count(chr(10)+chr(10))+1} paras)')
    print_audit(audit_body)
    for token in (
        '本文来自', '内容来自', 'copyright', 'YIN', 'ZUO', 'XXOO', '做AI',
        '什幺', '那幺', '怎幺', 'JB', 'JJ', '小DD', '/H',
    ):
        c = audit_body.count(token)
        if c:
            print(f'  residual {token}: {c}')


if __name__ == '__main__':
    main()

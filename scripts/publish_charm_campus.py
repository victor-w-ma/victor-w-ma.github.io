#!/usr/bin/env python3
"""Extract, polish, and publish 魅女校园 / 隔墙有眼 / 作品."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from post_format import (  # pylint: disable=wrong-import-position
    ascii_quotes_to_curly,
    fix_body,
    print_audit,
    split_front_matter,
)

YANGE = Path('/Users/cmsflash/drive/Ongoing/Yange/text')
POSTS = ROOT / '_posts'
DATE = '2026-09-15'

CAMPUS_SRC = YANGE / '唯爱足21-22年/2021-01/84458-魅女校园（最全）.md'
WALL_SRC = YANGE / '唯爱足18-20年/唯爱足2019/2019-05/奇談之隔墙有眼.md'
WORK_SRC = YANGE / '唯爱足18-20年/唯爱足2019/2019-05/奇谈之作品.md'

CHAPTER_SPLIT = re.compile(
    r'(?=^(?:魅女[一二三四五六七]|校园[一二三四五六七]|魅女校园[八九])：)',
    re.M,
)

HEADING_MAP = (
    ('魅女校园九：', '## 魅女校园九'),
    ('魅女校园八：', '## 魅女校园八'),
    ('魅女七：', '## 魅女七'),
    ('魅女六：', '## 魅女六'),
    ('魅女五：', '## 魅女五'),
    ('魅女四：', '## 魅女四'),
    ('魅女三：', '## 魅女三'),
    ('魅女二：', '## 魅女二'),
    ('魅女一：', '## 魅女一'),
    ('校园七：', '## 校园七'),
    ('校园六：', '## 校园六'),
    ('校园五：', '## 校园五'),
    ('校园四：', '## 校园四'),
    ('校园三：', '## 校园三'),
    ('校园二：', '## 校园二'),
    ('校园一：', '## 校园一'),
)

CAMPUS_AGEUP: list[tuple[str, str]] = [
    ('高二一班', '大二一班'),
    ('高三一班', '大三一班'),
    ('高二的下半学期', '大二的下半学期'),
    ('高一后半学期', '大一后半学期'),
    ('高二一个班级', '大二一个班级'),
    ('高二的一个学生', '大二的一个学生'),
    ('已是高三的一天', '已是大三的一天'),
    ('现在你们都高三了', '现在你们都大三了'),
    ('高三的第一次年段大考', '大三的第一次期中考试'),
    ('我们可是女校来着', '我们可是女子大学来着'),
    ('幸好是女校', '幸好是女子大学'),
    ('如果是普通学校', '如果是男女混校'),
    ('青春期男生', '男生'),
    ('刚入学一年级的时候', '刚入学大一的时候'),
    ('校服外套', '外套'),
    ('一大群未成年少女', '一大群女生'),
    ('未成年少女', '女生'),
    ('都还只是未成年', '都还只是大学生'),
    ('失控的少女', '失控的女生'),
    ('这个少女', '这个女生'),
    ('那些少女', '那些女生'),
    ('料想到少女会', '料想到女生会'),
    ('仅仅是个少女', '仅仅是个女生'),
    ('稳住这个少女', '稳住这个女生'),
    ('班主任', '辅导员'),
    ('教师会议', '教学会议'),
    ('高二', '大二'),
    ('高三', '大三'),
    ('高一', '大一'),
    ('女校', '女子大学'),
    ('少女', '女生'),
]

COMMON_TYPOS: list[tuple[str, str]] = [
    ('陈易希', '陈尹希'),
    ('王忆熙', '王诗伊'),
    ('yin 液', '淫液'),
    ('yin液', '淫液'),
    ('YIN水', '淫水'),
    ('做 爱', '做爱'),
    ('舔 肛', '舔肛'),
    ('舔 着肛', '舔着肛'),
    ('口 交', '口交'),
    ('kou交', '口交'),
    ('阳 具', '阳具'),
    ('手 枪', '手枪'),
    ('手抢', '手枪'),
    ('抽查着', '抽插着'),
    ('添缸', '舔肛'),
    ('俩个', '两个'),
    ('脑蛋', '脑袋'),
    ('倔起', '撅起'),
    ('服服踮踮', '服服帖帖'),
    ('服踮着', '服帖地'),
    ('服踮', '服帖'),
    ('狼借', '狼藉'),
    ('完美无暇', '完美无瑕'),
    ('含糊不去', '含糊不清'),
    ('及其犯规', '极其犯规'),
    ('不解的的是', '不解的是'),
    ('有些儿性感', '有些性感'),
    ('招到拒绝', '遭到拒绝'),
    ('竟然上天给了', '既然上天给了'),
    ('连媒体都报告了', '连媒体都报道了'),
    ('掉塌在胯部', '垮在胯部'),
    ('你在这样我就要', '你再这样我就要'),
    ('另人发指', '令人发指'),
    ('嘴巴长得大大的', '嘴巴张得大大的'),
    ('让我得屎', '让我的屎'),
    ('很恨的往', '狠狠地往'),
    ('蛮进了', '埋进了'),
    ('嗑着头', '磕着头'),
    ('幸淋到', '喷淋到'),
    ('渴望不及', '可望而不可及'),
    ('那想到好像', '哪想到好像'),
    ('找了魔般', '着了魔般'),
    ('在仔细看其实', '再仔细看其实'),
    ('做为', '作为'),
    ('这辔尿', '这泡尿'),
    ('辔汤', '泡汤'),
    ('引接了', '迎接了'),
    ('对像还是', '对象还是'),
    ('下意思的', '下意识地'),
    ('真故事这棒', '这故事真棒'),
    ('计算机', '电脑'),
    ('吃着临时而', '吃着零食而'),
    ('半醒得陈尹希', '半醒的陈尹希'),
    ('亦又下贱', '亦或下贱'),
    ('看的见', '看得见'),
    ('却有其事', '确有其事'),
    ('憋了一眼', '瞥了一眼'),
    ('自居屋', '自住屋'),
    ('圈入嘴里', '卷入嘴里'),
    ('还再为她', '还在为她'),
    ('排泄的，那金黄色', '排泄着，那金黄色'),
    ('两个长相相似的少女', '两个长相相似的女生'),
    ('同租的少女', '同租的女生'),
    ('Q3232388053', 'QQ3232388053'),
    ('喷she', '喷射'),
    ('yin声', '淫声'),
    ('yin水', '淫水'),
    ('yin荡', '淫荡'),
    ('yin叫', '淫叫'),
    ('yin笑', '淫笑'),
    ('几把', '鸡巴'),
    ('抢操的', '枪操得'),
    ('高架酒杯', '高脚酒杯'),
    ('升学考都给加分', '期末都给加分'),
    ('傻逼班主任', '傻逼辅导员'),
    ('两个少女的嘴巴', '两个女生的嘴巴'),
    ('那年我才十六岁', '那年我才十九岁'),
    ('十六岁，她就玩腻男人了', '十九岁，她就玩腻男人了'),
    ('十六岁，思思从胯下', '十九岁，思思从胯下'),
    ('液体笔直的冲进', '液体笔直地冲进'),
    ('满脸通红的喊', '满脸通红地喊'),
    ('厌恶的瞄', '厌恶地瞄'),
    ('不停的换来', '不停地换来'),
    ('失望的靠在', '失望地靠在'),
]

WORK_AGEUP: list[tuple[str, str]] = [
    ('那时还不满18岁的小女生', '那时刚十九岁的女生'),
    ('陈尹希她才刚刚16岁', '陈尹希刚满十九岁'),
    ('陈尹希这个16岁的丫头', '陈尹希这个十九岁的丫头'),
    ('这个还只有十六岁的姑娘', '这个才十九岁的姑娘'),
    ('这个仅仅16岁的女生', '这个才十九岁的女生'),
    ('16岁的女生有着恶魔般的思想', '十九岁的女生有着恶魔般的思想'),
    ('她在16岁那年', '她在十九岁那年'),
]

SPEAKERS = (
    r'陈怡恬|陈忆熙|张丽莉|尹琴琴|李淑|王诗伊|陈玉晓|徐婷|李琴|程予希|'
    r'黄晨辰|陈尹希|陈子仪|李玲珊|言潇芸|李丽悠|悠儿|思思|小思|'
    r'那女人|面具女人|那红毛|红毛|中年女人|陈斌|队长|张力|小张|'
    r'眼镜妹|学生会长|李管家|大姐|随着'
)

EXTRA_DE_DEI: list[tuple[str, str]] = [
    ('迷的不像样', '迷得不像样'),
    ('搞的乌烟瘴气', '搞得乌烟瘴气'),
    ('玩弄的不像样', '玩弄得不像样'),
    ('撑的露出', '撑得露出'),
    ('长的太大', '长得太大'),
    ('发育的也特好', '发育得也特好'),
    ('发育的太快', '发育得太快'),
    ('打扮的样子', '打扮的样子'),
    ('长的好高', '长得好高'),
    ('换的特朴实', '换得特朴实'),
    ('舔的来了性欲', '舔得来了性欲'),
    ('丰腴的惊人', '丰腴得惊人'),
    ('瞪的圆圆', '瞪得圆圆'),
    ('弄的高潮迭起', '弄得高潮迭起'),
    ('笨的要命', '笨得要命'),
    ('瘦的只剩下', '瘦得只剩下'),
    ('饿的差不多', '饿得差不多'),
    ('吸的那么用力', '吸得那么用力'),
    ('吸吃的干干净净', '吸吃得干干净净'),
    ('喝的大醉', '喝得大醉'),
    ('喝的酩酊大醉', '喝得酩酊大醉'),
    ('气的发抖', '气得发抖'),
    ('弄的没兴致', '弄得没兴致'),
    ('坐的窒息', '坐得窒息'),
    ('摇得越用力', '摇得越用力'),
    ('调查的一清二楚', '调查得一清二楚'),
    ('装的楚楚动人', '装得楚楚动人'),
    ('反应的过来', '反应得过来'),
    ('走的差不多', '走得差不多'),
    ('舔的发麻', '舔得发麻'),
    ('表现的好点', '表现得好点'),
    ('馋的', '馋得'),
    ('吃的死死的', '吃得死死的'),
    ('脱的只剩下', '脱得只剩下'),
    ('脱的精光', '脱得精光'),
    ('脱的光光', '脱得光光的'),
    ('掰的那么大', '掰得那么大'),
    ('写的怎样了', '写得怎样了'),
    ('写的差不多', '写得差不多'),
    ('大的惊人', '大得惊人'),
    ('说的好', '说得好'),
]

EXTRA_DI: list[tuple[str, str]] = [
    ('漫不经心的玩', '漫不经心地玩'),
    ('卖力的为她', '卖力地为她'),
    ('一脸嫌弃的说', '一脸嫌弃地说'),
    ('唯唯诺诺的祈求', '唯唯诺诺地祈求'),
    ('卖力的舔吸', '卖力地舔吸'),
    ('无聊着想着', '无聊地想着'),
    ('偷偷的瞄', '偷偷地瞄'),
    ('大大咧咧的往', '大大咧咧地往'),
    ('嘻皮笑脸的说', '嘻皮笑脸地说'),
    ('用力的把女生', '用力地把女生'),
    ('微微张开着嘴巴', '微微张着嘴巴'),
    ('小心翼翼的扳', '小心翼翼地扳'),
    ('有点嗔怒的望', '有点嗔怒地望'),
    ('有些得意的往', '有些得意地往'),
    ('傲慢的摇', '傲慢地摇'),
    ('有点厌恶的看', '有点厌恶地看'),
    ('另人发指的命令', '令人发指地命令'),
    ('缓缓的跪', '缓缓地跪'),
    ('奋力把', '奋力把'),
    ('厌恶的说', '厌恶地说'),
    ('敞开着腿', '敞开着腿'),
    ('讨好的为其', '讨好地为其'),
    ('含糊不清的说', '含糊不清地说'),
    ('灿烂的笑', '灿烂地笑'),
    ('笑眯眯的望', '笑眯眯地望'),
    ('装模作样的说', '装模作样地说'),
    ('得意的回头', '得意地回头'),
    ('嘲弄的语气', '嘲弄的语气'),
    ('尽量把语气装的', '尽量把语气装得'),
    ('细细的品味', '细细地品味'),
    ('小心翼翼的为', '小心翼翼地为'),
    ('兴致勃勃的开始', '兴致勃勃地开始'),
    ('欢快的边操', '欢快地边操'),
    ('机械的说', '机械地说'),
    ('温柔的说', '温柔地说'),
    ('面无表情却又温柔的说', '面无表情却又温柔地说'),
    ('厌恨的看', '厌恨地看'),
    ('挣扎的爬', '挣扎着爬'),
    ('疯狂的摇头', '疯狂地摇头'),
    ('悄然滑下', '悄然滑下'),
    ('深深的冲着', '深深地冲着'),
    ('卖力舔着', '卖力地舔着'),
    ('冷淡的跟', '冷淡地跟'),
    ('兴致勃勃的趴', '兴致勃勃地趴'),
    ('慢悠悠的视线', '慢悠悠的视线'),
    ('虔诚的托着', '虔诚地托着'),
    ('自暴自弃般的玩弄', '自暴自弃般地玩弄'),
    ('偷偷的找过', '偷偷地找过'),
    ('努力的引导', '努力地引导'),
    ('尽情的享受', '尽情地享受'),
    ('乖乖的张开', '乖乖地张开'),
    ('长的漂亮', '长得漂亮'),
]

FALSE_POSITIVE: list[tuple[str, str]] = [
    ('打扮的样子', '打扮的样子'),
    ('拍的视频', '拍的视频'),
    ('努力地男人', '努力的男人'),
    ('认真地学生', '认真的学生'),
    ('清理的屁眼', '清理着屁眼'),
    ('理所当然的接受', '理所当然地接受'),
    ('无法自拔的迷恋着', '无法自拔地迷恋着'),
    ('越来越过份的要求', '越来越过份的要求'),
    ('欢快的大叫', '欢快地大叫'),
    ('不停的探索', '不停地探索'),
    ('越发的无所顾忌', '越发地无所顾忌'),
    ('努力又机械的掏', '努力又机械地掏'),
    ('慢慢的，让这对', '慢慢地，让这对'),
    ('虔诚的爬到', '虔诚地爬到'),
    ('识趣的把', '识趣地把'),
    ('熟练的把', '熟练地把'),
    ('尽心尽力的为', '尽心尽力地为'),
    ('美滋滋的听着', '美滋滋地听着'),
    ('昏昏沉沉的睡', '昏昏沉沉地睡'),
    ('严肃的讲话着', '严肃地讲着'),
    ('安静的做着题目', '安静地做着题目'),
    ('有点恼怒的用力', '有点恼怒地用力'),
    ('说的好', '说得好'),
    ('发楞', '发愣'),
    ('昏天暗地的喝', '昏天暗地地喝'),
    ('充满诱惑的趴', '充满诱惑地趴'),
    ('笑眯眯的跑', '笑眯眯地跑'),
    ('无奈的吐出', '无奈地吐出'),
    ('厌恶的把烟', '厌恶地把烟'),
    ('惹的男生', '惹得男生'),
    ('不安的站着', '不安地站着'),
    ('轮流不间断的为', '轮流不间断地为'),
    ('改变得话', '改变的话'),
]

AUTHOR_QQ = (
    '大家一直发我消息我也无法回复，所以弄了个Q3232388053，可以加我，'
    '名字就是架子秘密。'
)

WALL_INTRO = """世界上有着很多不可能的事情，看似不可能，却时刻在这世界上发生着，只是，在现实社会中，它们并不是那么显而易见。

那些奇怪荒谬、让人不可置信又鲜为人知的事情，就是所谓的奇谈。

我是架子，一个收藏奇谈的人。我被这些奇谈吸引着，每当我找到一个新的奇谈，我都会细细地品味它们，然后，我就会……

讲给你们听。

今天我就来给大家讲第一个奇谈。
"""

WALL_OUTRO = """
怎样？第一个奇谈奇怪吗？其实，我们身边有很多这样的故事，只是我们都没有去关注它。奇谈，时时刻刻在我们身边发生着呢。

好了，奇谈之隔墙有眼就到这里。下次，又会有谁落入奇谈的故事里呢？我们，下一个奇谈再见吧。
"""


def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        if old != new:
            text = text.replace(old, new)
    return text


def extract_campus(raw: str) -> str:
    matches = list(re.finditer(r'^魅女一：', raw, re.M))
    if not matches:
        raise ValueError('魅女一 heading not found')
    start = matches[1].start() if len(matches) > 1 else matches[0].start()
    end_marker = '对呢，一定，陈怡恬，陈忆熙，你们一定会见面的，一定。'
    end = raw.find(end_marker, start)
    if end < 0:
        raise ValueError('campus ending marker not found')
    return raw[start:end + len(end_marker)].strip()


def ageup_campus_chapters(body: str) -> str:
    parts = CHAPTER_SPLIT.split(body)
    out: list[str] = []
    for part in parts:
        if not part.strip():
            continue
        first = part.split('：', 1)[0]
        if first.startswith('校园') or first.startswith('魅女校园'):
            part = apply_pairs(part, CAMPUS_AGEUP)
        out.append(part)
    return ''.join(out)


def convert_headings(body: str) -> str:
    body = body.replace('未来是不确定的。魅女二：', '未来是不确定的。\n\n魅女二：')
    for old, new in HEADING_MAP:
        body = re.sub(rf'^{re.escape(old)}\s*', f'{new}\n\n', body, flags=re.M)
    body = body.replace('奇谈之隔墙有眼第二章', '## 第二章')
    body = re.sub(r'^第二章\s*$', '## 第二章', body, flags=re.M)
    body = re.sub(r'^第三章：\s*$', '## 第三章', body, flags=re.M)
    return body


def split_glued_spaces(body: str) -> str:
    lines: list[str] = []
    for line in body.split('\n'):
        if line.startswith('#'):
            lines.append(line)
            continue
        line = re.sub(r' {2,}', '\n\n', line)
        lines.append(line)
    return '\n'.join(lines)


def insert_missing_close_quotes(body: str) -> str:
    body = re.sub(
        rf'("[^"\n]{{1,400}}[！？。…～])(\s*)({SPEAKERS})',
        r'\1"\2\3',
        body,
    )
    return body


def balance_dialogue_quotes(body: str) -> str:
    def fix_paragraph(para: str) -> str:
        if '"' not in para:
            return para
        para = para.rstrip()
        if para.count('"') % 2 == 0:
            return para
        if para.endswith(('。', '！', '？', '…', '～')):
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


def join_wrapped_lines(body: str) -> str:
    lines = body.split('\n')
    out: list[str] = []
    for line in lines:
        if (
            out
            and out[-1]
            and not out[-1].startswith('#')
            and not out[-1].endswith(('。', '！', '？', '…', '—', '"', '：', '，'))
            and line
            and not line.startswith(('#', '"'))
        ):
            out[-1] += line
        else:
            out.append(line)
    return '\n'.join(out)


def lines_as_paragraphs(body: str) -> str:
    chunks: list[str] = []
    for raw_line in body.split('\n'):
        line = raw_line.strip()
        if not line:
            continue
        chunks.append(line)
    return '\n\n'.join(chunks)


def close_quotes_before_narrator_curly(body: str) -> str:
    names = (
        r'陈怡恬|陈忆熙|张丽莉|尹琴琴|李淑|王诗伊|陈玉晓|徐婷|李琴|'
        r'黄晨辰|陈尹希|陈子仪|言潇芸|李丽悠|思思|小思|那个女生|'
        r'伴随着|蹲着的女人|这个才十九岁|十九岁的女生|中年女人|'
        r'队长|张力|小张|面具女人|那女人|那红毛|红毛|市区的|'
        r'一个有些年纪|在另一间'
    )
    prev = None
    while prev != body:
        prev = body
        body = re.sub(
            rf'“([^”]*[！？。～…])({names})',
            r'“\1”\2',
            body,
        )
    return body


def curly_quotes_per_paragraph(body: str) -> str:
    parts = re.split(r'(\n\n+)', body)
    out: list[str] = []
    for part in parts:
        if part.startswith('\n') or '"' not in part:
            out.append(part)
            continue
        try:
            out.append(ascii_quotes_to_curly(part))
        except ValueError:
            if part.count('"') % 2 == 1:
                if part.endswith(('。', '！', '？', '…', '～')):
                    part = f'{part[:-1]}"{part[-1]}'
                else:
                    part = part + '"'
            out.append(ascii_quotes_to_curly(part))
    return ''.join(out)


def strip_extra_close_quotes(body: str) -> str:
    parts = re.split(r'(\n\n+)', body)
    out: list[str] = []
    for part in parts:
        if part.startswith('\n') or not part.strip():
            out.append(part)
            continue
        while part.count('\u201d') > part.count('\u201c'):
            idx = part.rfind('\u201d')
            part = part[:idx] + part[idx + 1:]
        out.append(part)
    return ''.join(out)


def polish(body: str, *, extra: list[tuple[str, str]] | None = None) -> str:
    body = body.replace('\u201c', '"').replace('\u201d', '"')
    body = body.replace(AUTHOR_QQ, '')
    body = convert_headings(body)
    body = split_glued_spaces(body)
    body = join_wrapped_lines(body)
    pairs = list(COMMON_TYPOS)
    if extra:
        pairs.extend(extra)
    body = apply_pairs(body, pairs)
    body = body.replace('"你有新邮件"\n\n。', '"你有新邮件"。')
    body = body.replace('"你有新邮件"\n。', '"你有新邮件"。')
    for _ in range(3):
        body = insert_missing_close_quotes(body)
    body = lines_as_paragraphs(body)
    body = balance_dialogue_quotes(body)
    body = fix_body(
        body,
        extra_replacements=[],
        extra_de_dei=EXTRA_DE_DEI,
        extra_di=EXTRA_DI,
        extra_false_positive_fixes=FALSE_POSITIVE,
        fix_quotes=False,
    )
    body = curly_quotes_per_paragraph(body)
    body = close_quotes_before_narrator_curly(body)
    body = strip_extra_close_quotes(body)
    body = body.replace('”。', '。”').replace('”！', '！”').replace('”？', '？”')
    body = body.replace('“恩，', '“嗯，').replace('“恩”', '“嗯”')
    body = body.replace('“恩恩', '“嗯嗯').replace('“恩…', '“嗯…')
    body = body.replace('。“”', '。').replace('”“', '').replace('“”', '')
    body = body.replace('爱情”…', '爱情…')
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = re.sub(r'\n+(## )', r'\n\n\1', body)
    return body.strip() + '\n'


def write_post(slug: str, title: str, body: str, *, status: str | None = None) -> Path:
    status_line = f'status: {status}\n' if status else ''
    front = f'---\nlayout: post\ntitle: "{title}"\n{status_line}---\n'
    out = POSTS / f'{DATE}-{slug}.md'
    out.write_text(front + '\n' + body, encoding='utf-8')
    print(f'Wrote {out.relative_to(ROOT)} ({out.stat().st_size}B)')
    print('Audit:')
    print_audit(body)
    remaining = {
        '高二': body.count('高二'),
        '高三': body.count('高三'),
        '女校': body.count('女校'),
        '班主任': body.count('班主任'),
        '未成年': body.count('未成年'),
        '16岁': body.count('16岁') + body.count('十六岁'),
        'ASCII quotes': body.count('"'),
    }
    print('Checks:', remaining)
    return out


def publish_campus() -> None:
    raw = CAMPUS_SRC.read_text(encoding='utf-8')
    body = extract_campus(raw)
    body = ageup_campus_chapters(body)
    body = body.replace('班主任', '辅导员')
    body = polish(body)
    write_post('seductive-campus', '魅女校园', body)


def publish_wall() -> None:
    raw = WALL_SRC.read_text(encoding='utf-8')
    _, body = split_front_matter(raw)
    body = WALL_INTRO + '\n' + body.strip() + '\n' + WALL_OUTRO
    body = polish(body)
    write_post('eyes-behind-the-wall', '隔墙有眼', body)


def publish_work() -> None:
    raw = WORK_SRC.read_text(encoding='utf-8')
    _, body = split_front_matter(raw)
    body = apply_pairs(body, WORK_AGEUP)
    body = polish(body)
    write_post('the-artwork', '作品', body, status='断更')


def main() -> None:
    publish_campus()
    print()
    publish_wall()
    print()
    publish_work()


if __name__ == '__main__':
    main()

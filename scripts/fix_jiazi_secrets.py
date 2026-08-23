#!/usr/bin/env python3
"""Extract 架子秘密 from backlog, format, and publish."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from post_format import (  # pylint: disable=wrong-import-position
    fix_body,
    print_audit,
    split_front_matter,
)

BACKLOG = ROOT / '_posts' / 'backlog' / 'xiaoer-1.md'
TARGET = ROOT / '_posts' / '2026-08-22-jiazi-secrets.md'
START = '# 架子秘密'
END = '# 随手流水文'
FRONT = '---\nlayout: post\ntitle: "架子秘密"\n---\n'

STORY_REPLACEMENTS: list[tuple[str, str]] = [
    ('YIN水', '淫水'),
    ('YIN玩', '淫玩'),
    ('YIN语', '淫语'),
    ('口 交', '口交'),
    ('赵楚楚', '李楚楚'),
    ('屁股肉一塔', '屁股肉一塌'),
    ('加Q3232388053', '加QQ3232388053'),
    ('恰如春梦 了无痕', '恰如春梦了无痕'),
    ('看安静的看着我', '她安静地看着我'),
    ('我也要要看看', '我也要看看'),
    ('自己就往躺在床上', '自己就往床上一躺'),
    ('晓儿发个我这段', '晓儿发给我这段'),
    ('L艰难着拿着', 'L艰难地拿着'),
    ('俩个', '两个'),
]

EXTRA_DE_DEI: list[tuple[str, str]] = [
    ('抓的轻点', '抓得轻点'),
    ('来的爽了', '来得爽了'),
    ('写的很坏', '写得很坏'),
    ('变化的极快', '变化得极快'),
    ('变得更加的亲密', '变得更加亲密'),
    ('长的并不邪恶', '长得并不邪恶'),
    ('高贵的多的屁眼', '高贵得多的屁眼'),
    ('只懂的舔', '只懂得舔'),
    ('只懂的吃', '只懂得吃'),
]

EXTRA_FALSE_POSITIVE: list[tuple[str, str]] = [
    ('更让我兴奋地是', '更让我兴奋的是'),
]

EXTRA_DI: list[tuple[str, str]] = [
    ('无聊的拿起', '无聊地拿起'),
    ('很容易的，', '很容易地，'),
    ('楚楚动人的望着', '楚楚动人地望着'),
    ('楚楚动人的求我', '楚楚动人地求我'),
    ('幽幽的望着', '幽幽地望着'),
    ('不自觉的变', '不自觉地变'),
    ('淡定的说道', '淡定地说道'),
    ('轻轻的说道', '轻轻地说道'),
    ('温柔的说道', '温柔地说道'),
    ('认真的说道', '认真地说道'),
    ('神秘兮兮的说道', '神秘兮兮地说道'),
    ('自导自演的叫', '自导自演地叫'),
    ('很自豪的跟我', '很自豪地跟我'),
    ('不停的秀恩爱', '不停地秀恩爱'),
    ('轻咬的嘴唇楚楚动人地望着', '轻咬着嘴唇，楚楚动人地望着'),
    ('小声的说着', '小声地说着'),
    ('不可思议的望着', '不可思议地望着'),
    ('不停的舔吸', '不停地舔吸'),
    ('不停的吸吮', '不停地吸吮'),
    ('一前一后的按', '一前一后地按'),
    ('忘我的舔起', '忘我地舔起'),
    ('淡定的说着', '淡定地说着'),
    ('可爱的笑着', '可爱地笑着'),
    ('慢慢悠悠的说着', '慢慢悠悠地说着'),
    ('悠哉的拿起', '悠哉地拿起'),
    ('平淡的说着', '平淡地说着'),
    ('慢悠悠的把', '慢悠悠地把'),
    ('大大咧咧的跟', '大大咧咧地跟'),
    ('乐呵呵的看着', '乐呵呵地看着'),
    ('昏昏沉沉的看着', '昏昏沉沉地看着'),
    ('不敢停歇的舔弄', '不敢停歇地舔弄'),
    ('气鼓鼓的说着', '气鼓鼓地说着'),
    ('下贱的求我', '下贱地求我'),
    ('熟练的挑', '熟练地挑'),
    ('很轻松的在', '很轻松地在'),
    ('虔诚的磕头', '虔诚地磕头'),
    ('大大方方的敞开', '大大方方地敞开'),
    ('犯贱的嗦', '犯贱地嗦'),
    ('犯贱的在吃', '犯贱地在吃'),
    ('毫无尊严的各种', '毫无尊严地各种'),
    ('卖力的讨好', '卖力地讨好'),
    ('成功的在学姐', '成功地在学姐'),
    ('悠然的躺在', '悠然地躺在'),
    ('大大的敞开着', '大大地敞开着'),
    ('千方百计的羞辱', '千方百计地羞辱'),
    ('不停的磕头', '不停地磕头'),
]


def extract_story(raw: str) -> tuple[str, str]:
    start = raw.find(START)
    end = raw.find(END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError(f'cannot find {START!r} .. {END!r} in {BACKLOG}')
    story = raw[start:end]
    rest = raw[end:].lstrip('\n')
    story = re.sub(r'^# 架子秘密\n+', '', story)
    story = re.sub(r'^## 一\s*$', '# （一）', story, flags=re.M)
    story = re.sub(r'^## 二\s*$', '# （二）', story, flags=re.M)
    story = re.sub(r'^## 三\s*$', '# （三）', story, flags=re.M)
    story = re.sub(r'^## 四\s*$', '# （四）', story, flags=re.M)
    story = re.sub(r'^## 五\s*$', '# （五）', story, flags=re.M)
    story = re.sub(r'^## 架子秘密五后篇\s*$', '# 五后篇', story, flags=re.M)
    story = re.sub(r'^### \d+\n+', '', story, flags=re.M)
    story = story.replace('\u201c', '"').replace('\u201d', '"')
    story = re.sub(r'[ \t]+\n', '\n', story)
    story = re.sub(r'\n{3,}', '\n\n', story)
    story = re.sub(r'^(# .+)\n(?!\n)', r'\1\n\n', story, flags=re.M)
    return story.strip() + '\n', rest


def main() -> None:
    raw = BACKLOG.read_text(encoding='utf-8')
    if raw.startswith('---'):
        _, raw_body = split_front_matter(raw)
    else:
        raw_body = raw

    body, remainder = extract_story(raw_body)
    fixed = fix_body(
        body,
        extra_replacements=STORY_REPLACEMENTS,
        extra_de_dei=EXTRA_DE_DEI,
        extra_di=EXTRA_DI,
        extra_false_positive_fixes=EXTRA_FALSE_POSITIVE,
    )
    TARGET.write_text(FRONT + '\n' + fixed, encoding='utf-8')
    BACKLOG.write_text(remainder, encoding='utf-8')
    print(f'Wrote {TARGET}')
    print(f'Trimmed {BACKLOG}')
    print('Audit:')
    print_audit(fixed)


if __name__ == '__main__':
    main()

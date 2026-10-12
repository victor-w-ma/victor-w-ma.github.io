#!/usr/bin/env python3
"""Rewrite 乐乐 as cis female in Black Daddy Mike (straight)."""

from __future__ import annotations

from pathlib import Path

from post_format import print_audit, split_front_matter

ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / '_posts' / '2025-03-15-black-daddy-mike-straight.md'
EN = ROOT / '_includes' / 'translations' / 'en' / 'black-daddy-mike-straight.html'

# Longest matches first.
ZH_REPLACEMENTS: list[tuple[str, str]] = [
    (
        '不对，他刚刚说他原本是直男，喜欢女人，但在监狱里对其他的亚洲人狱友产生了性趣，因为他发现黄皮小子比女人更懂得伺候他这样的黑人。',
        '不对，他刚刚说自己喜欢女人，但在监狱里对黄皮小子产生了性趣，因为他发现黄皮小子比女人更懂得伺候他这样的黑人。',
    ),
    (
        '在家和乐乐吃完情侣之间的二人午餐后，乐乐在我洗碗的时候，说要去附近的超市买点’日用品’，我本来是想一起去的，但乐乐说，先洗碗吧，她很快就回来。',
        '在家和乐乐吃完情侣之间的二人午餐后，乐乐在我洗碗的时候，说要去附近的超市买点衣服，我本来是想一起去的，但乐乐说，先洗碗吧，她很快就回来。',
    ),
    (
        '乐乐的声音带着我从未听见过的俏皮和一丝丝埋怨：“买好了，你知道吗？我付钱的时候，那个收银员看我的眼神都不对劲。”',
        '乐乐的声音带着我从未听见过的俏皮和一丝丝埋怨：“买好了，你知道吗？我付钱的时候，那个收银员看我买这种衣服，眼神都不对劲。”',
    ),
    (
        '我默默地看着乐乐脱掉身上的衣服，穿上了黑丝、洛丽塔的裙子，最后甚至戴上了假睫毛和美瞳。',
        '我默默地看着乐乐脱掉身上的衣服，换上了黑丝和洛丽塔裙子，最后甚至戴上了假睫毛和美瞳。',
    ),
    (
        '“天呐！宝贝，你真的太漂亮了！”麦克的称赞源源不断：“在电梯里第一眼看到你的时候，我就知道你化了妆绝对比任何女生都好看！”',
        '“天呐！宝贝，你真的太漂亮了！”麦克的称赞源源不断：“在电梯里第一眼看到你的时候，我就知道你打扮起来一定特别好看！”',
    ),
    (
        '“宝贝，你真的太美了，我忍不住了！先给老公亲亲。”麦克突然用右手搂住乐乐，左手摸上了乐乐的假胸，不顾乐乐的挣扎，硕大嘴唇直接印在了乐乐的嘴巴上。',
        '“宝贝，你真的太美了，我忍不住了！先给老公亲亲。”麦克突然用右手搂住乐乐，左手摸上了乐乐的胸部，不顾乐乐的挣扎，硕大嘴唇直接印在了乐乐的嘴巴上。',
    ),
    (
        '我看到麦克舔着嘴角，眼里散发着浓郁的情欲，这是我从未看到过的眼神。麦克似乎真的很喜欢女装后的乐乐，眼神里那股强烈的兴奋是掩饰不住的。',
        '我看到麦克舔着嘴角，眼里散发着浓郁的情欲，这是我从未看到过的眼神。麦克似乎真的很喜欢换上这身衣服的乐乐，眼神里那股强烈的兴奋是掩饰不住的。',
    ),
    (
        '我难以想象，麦克居然会操女人，他不是直男吗？不对，乐乐现在是一副女装的模样，并且比女生更加漂亮，这也许是吸引麦克操她小穴的理由。',
        '我难以想象，麦克居然会当着我的面操乐乐。他一直说自己是直男，对女人有欲望，可那是我的女朋友啊。现在的乐乐换上了这身衣服，比平时更加漂亮，也许这就是吸引麦克对她下手的理由。',
    ),
    (
        '看着乐乐没有反抗的身体状态，我知道他们肯定不是第一次做爱了。最让我怀疑的就是那天乐乐到麦克家里吃晚饭的时候，也许那就是乐乐的第一次破身，那天晚上到底发生了什么？',
        '看着乐乐没有反抗的身体状态，我知道他们肯定不是第一次做爱了。最让我怀疑的就是那天乐乐到麦克家里吃晚饭的时候，也许那就是他们第一次做爱，那天晚上到底发生了什么？',
    ),
    (
        '麦克一边摸着乐乐的假胸，一边调笑道：“那个黄皮猴子操你比较舒服，还是老子操你比较舒服？”',
        '麦克一边摸着乐乐的胸部，一边调笑道：“那个黄皮猴子操你比较舒服，还是老子操你比较舒服？”',
    ),
    (
        '“我的乐乐啥都不脏！”我嘿嘿笑着，一边更加卖力地舔舐着乐乐的阴毛，一边用手撸动着乐乐的阴部。我能感觉到乐乐很爽，她的阴部湿漉漉地流着水，似乎随时可能达到高潮。',
        '“我的乐乐啥都不脏！”我嘿嘿笑着，一边更加卖力地舔舐着乐乐的阴毛，一边用手抚弄着乐乐的阴部。我能感觉到乐乐很爽，她的阴部湿漉漉地流着水，似乎随时可能达到高潮。',
    ),
    (
        '乐乐与麦克之间算是性爱伙伴，也就是炮友之间的关系。麦克是直男，对身为女性的乐乐充满了欲望，他喜欢乐乐的模样，那会让他很兴奋。乐乐则是喜欢麦克硕大的黑肉棒为她的身体带来的快感和高潮，纯粹只是身体上的喜欢。',
        '乐乐与麦克之间算是性爱伙伴，也就是炮友之间的关系。麦克是直男，对乐乐充满了欲望，他喜欢她的身体，那会让他很兴奋。乐乐则是喜欢麦克硕大的黑肉棒为她的身体带来的快感和高潮，纯粹只是身体上的喜欢。',
    ),
    (
        '他一直都不在乎我的想法，只是把我当做一个工具使用。他喜欢乐乐女性的样子，为此可以尽情操她。',
        '他一直都不在乎我的想法，只是把我当做一个工具使用。他喜欢乐乐，为此可以尽情操她。',
    ),
]

EN_REPLACEMENTS: list[tuple[str, str]] = [
    (
        'No, he just said that he was originally a straight man who liked women, but he became sexually interested in other Asian inmates in prison because he found that yellow-skinned boys knew how to serve black men like him better than women.',
        'No, he just said that he liked women, but he became sexually interested in yellow-skinned boys in prison because he found that they knew how to serve black men like him better than women.',
    ),
    (
        'After having a couple\'s lunch with Lele at home, while I was washing the dishes, Lele said that she was going to a nearby supermarket to buy some "daily necessities." I originally wanted to go with her, but Lele said to wash the dishes first, and she would be back soon.',
        'After having a couple\'s lunch with Lele at home, while I was washing the dishes, Lele said that she was going to a nearby supermarket to buy some clothes. I originally wanted to go with her, but Lele said to wash the dishes first, and she would be back soon.',
    ),
    (
        'Lele\'s voice was playful and a little bit complaining that I had never heard before: "I\'ve bought it, you know? When I paid, the cashier looked at me wrong."',
        'Lele\'s voice was playful and a little bit complaining that I had never heard before: "I\'ve bought it, you know? When I paid, the cashier looked at me funny for buying this kind of clothes."',
    ),
    (
        'I watched silently as Lele took off her clothes, put on black stockings, a Lolita skirt, and finally even false eyelashes and contact lenses.',
        'I watched silently as Lele took off her clothes, changed into black stockings and a Lolita skirt, and finally even put on false eyelashes and contact lenses.',
    ),
    (
        '"Oh my God! Baby, you are so beautiful!" Mike\'s compliments kept coming: "When I first saw you in the elevator, I knew that you would definitely look better than any other girl with makeup on!"',
        '"Oh my God! Baby, you are so beautiful!" Mike\'s compliments kept coming: "When I first saw you in the elevator, I knew you would look especially beautiful all dressed up!"',
    ),
    (
        '"Baby, you are so beautiful, I can\'t help it! Kiss my husband first." Mike suddenly hugged Lele with his right hand and touched Lele\'s fake breast with his left hand. Regardless of Lele\'s struggle, his huge lips were printed directly on Lele\'s mouth.',
        '"Baby, you are so beautiful, I can\'t help it! Give your husband a kiss." Mike suddenly hugged Lele with his right hand and touched Lele\'s breasts with his left hand. Regardless of Lele\'s struggle, his huge lips were printed directly on Lele\'s mouth.',
    ),
    (
        'I saw Mike licking the corners of his mouth, and his eyes were full of lust, which I had never seen before. Mike seemed to really like Lele, who was dressed as a woman, and the intense excitement in his eyes could not be concealed.',
        'I saw Mike licking the corners of his mouth, and his eyes were full of lust, which I had never seen before. Mike seemed to really like Lele in this outfit, and the intense excitement in his eyes could not be concealed.',
    ),
    (
        'I can\'t imagine that Mike can actually fuck women. Isn\'t he a straight man? No, Lele now looks like a woman and is more beautiful than a girl. This may be the reason to attract Mike to fuck her pussy.',
        'I can\'t imagine that Mike would fuck Lele right in front of me. He always said he was straight and wanted women, but that was my girlfriend. Lele looked even more beautiful in this outfit. Maybe that was why Mike went after her.',
    ),
    (
        'Looking at Lele\'s body state without resistance, I knew it was definitely not the first time they had sex. What makes me most suspicious is when Lele went to Mike\'s house for dinner that day. Maybe that was Lele\'s first loss of virginity. What happened that night?',
        'Looking at Lele\'s body state without resistance, I knew it was definitely not the first time they had sex. What makes me most suspicious is when Lele went to Mike\'s house for dinner that day. Maybe that was the first time they had sex. What happened that night?',
    ),
    (
        'While touching Lele\'s fake breasts, Mike teased: "Is it more comfortable for that yellow-skinned monkey to fuck you, or for me to fuck you?"',
        'While touching Lele\'s breasts, Mike teased: "Is it more comfortable for that yellow-skinned monkey to fuck you, or for me to fuck you?"',
    ),
    (
        'Mike is a straight man who is full of desire for Lele, who is a woman. He likes Lele\'s appearance, which makes him very excited.',
        'Mike is a straight man who is full of desire for Lele. He likes her body, which makes him very excited.',
    ),
    (
        'He never cared what I thought and just used me as a tool. He liked the way Lele looked like a woman and could fuck her to his heart\'s content.',
        'He never cared what I thought and just used me as a tool. He liked Lele and could fuck her to his heart\'s content.',
    ),
]


def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> str:
    missing: list[str] = []
    for old, new in pairs:
        if old not in text:
            missing.append(old[:80])
            continue
        text = text.replace(old, new)
    if missing:
        raise SystemExit('Missing strings:\n- ' + '\n- '.join(missing))
    return text


def main() -> None:
    raw = ZH.read_text(encoding='utf-8')
    front, body = split_front_matter(raw)
    body = apply_pairs(body, ZH_REPLACEMENTS)
    ZH.write_text(front + '\n' + body, encoding='utf-8')
    print(f'Wrote {ZH}')
    print_audit(body)

    leftovers = [
        '假胸',
        '女装',
        '伪娘',
        '人妖',
        '比女生更加',
        '女性的样子',
        '身为女性的乐乐',
        '第一次破身',
    ]
    print('Leftover scan:')
    for token in leftovers:
        print(f'  {token}: {body.count(token)}')

    en = EN.read_text(encoding='utf-8')
    en = apply_pairs(en, EN_REPLACEMENTS)
    EN.write_text(en, encoding='utf-8')
    print(f'Wrote {EN}')
    en_leftovers = [
        'fake breast',
        'dressed as a woman',
        'more beautiful than a girl',
        'looked like a woman',
        'who is a woman',
        'loss of virginity',
        'daily necessities',
    ]
    print('EN leftover scan:')
    for token in en_leftovers:
        print(f'  {token}: {en.lower().count(token.lower())}')


if __name__ == '__main__':
    main()

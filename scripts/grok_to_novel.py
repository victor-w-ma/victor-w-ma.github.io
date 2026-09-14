"""Convert Grok dialogue transcript into a continuous novel."""

import pathlib
import re

_SRC = pathlib.Path(
    "_posts/ideas/middle-aged-wife-dominant-control-grok.md"
)
_DST = pathlib.Path(
    "_posts/ideas/middle-aged-wife-dominant-control-grok-fixed.md"
)

# Narrative order; skip superseded or meta-only sections.
# 8/9: same-school / early dual-parent (replaced by 11–14).
# 15: character summary meta.
SECTION_ORDER = [
    2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14,
    18, 19, 20, 21, 22,
    16, 17, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33,
    34, 35, 37, 38, 39,
]

PART_TITLES = {
    2: "一、牢笼",
    3: "二、表妹家",
    4: "三、岚狗",
    5: "四、隐秘的反叛",
    6: "五、学校",
    7: "六、校长室",
    10: "七、班主任回家",
    11: "八、出头",
    12: "九、泄愤",
    13: "十、同召",
    14: "十一、权威崩塌",
    18: "十二、另一所学校",
    19: "十三、反客为主",
    20: "十四、弱父",
    21: "十五、以牙还牙",
    22: "十六、觉醒",
    16: "十七、任课老师",
    17: "十八、家访",
    23: "十九、三天婢女",
    24: "二十、教师大会",
    25: "二十一、回家泄愤",
    26: "二十二、英语老师的报复",
    27: "二十三、补课",
    28: "二十四、越来越过分",
    29: "二十五、成效分化",
    30: "二十六、脏屁眼",
    31: "二十七、汇报",
    32: "二十八、单亲爸爸家",
    33: "二十九、刘老板家",
    34: "三十、最后一个顽固学生",
    35: "三十一、强势接管",
    37: "三十二、规矩",
    38: "三十三、三人独处",
    39: "三十四、绝对臣服",
}

META_PATTERNS = [
    re.compile(r"^（故事完）$"),
    re.compile(r"^故事待续$"),
    re.compile(r"^故事连通点："),
    re.compile(r"^目前情况："),
    re.compile(r"^现在压制链"),
    re.compile(r"^现在学校形成"),
    re.compile(r"^从这一天起，林老师"),
    re.compile(r"^李娜已经开始从受害者"),
    re.compile(r"^王芳对对方爸爸的直接"),
    re.compile(r"^这个段落"),
    re.compile(r"^这个版本严格按照"),
    re.compile(r"^新设定已调整"),
    re.compile(r"^现在刘老板家已经"),
    re.compile(r"^现在所有顽固学生"),
    re.compile(r"^王教练对陈老师的臣服已经"),
    re.compile(r"^需要我继续写"),
    re.compile(r"^需要继续写"),
    re.compile(r"^需要我详细展开"),
    re.compile(r"^想继续"),
    re.compile(r"^想让我继续"),
    re.compile(r"^想继续写"),
    re.compile(r"^想继续深入"),
    re.compile(r"^还是加深"),
    re.compile(r"^或者切换"),
    re.compile(r"^或者加深"),
    re.compile(r"^或者其他"),
    re.compile(r"^或者切换回"),
    re.compile(r"^告诉我具体"),
    re.compile(r"^请告诉我"),
    re.compile(r"^随时告诉我"),
    re.compile(r"^如果你想加长"),
    re.compile(r"^\* \* \*$"),
    re.compile(r"^还是下一次"),
    re.compile(r"^目前张岚还蒙在鼓里"),
    re.compile(r"^女校长[＞>]"),
    re.compile(r"^（例如："),
    re.compile(r"^现在最后一个"),
    re.compile(r"^李娜兴奋地点头"),
    re.compile(r"^……$"),
]

SUBTITLE_RE = re.compile(r"^### .+$")
META_BOLD_RE = re.compile(r"^\*\*(核心压制链|主要人物|其他设定|\d+\.)")
OPTION_LINE = re.compile(
    r"^\- .*(其他方向|详细场景|主线回归|最新发展|想加的|续写更长|其他剧情|其他发展)"
)
STORY_BULLET = re.compile(r"^\- (每天|同时督促|把小薇)")

OPENING_REPLACEMENTS = (
    (
        "同一晚，城市的另一个小区，王芳的家里灯火通明却安静得诡异。",
        "王芳住的另一头，这套屋子灯还亮着，却静得不像有人说话。",
    ),
    (
        "与此同时，在城市的另一所普通中学，王芳的儿子王浩也出事了。",
        "王浩在另一所中学念书。那天，他也闯了祸。",
    ),
    (
        "新的一周，李明又在学校闯祸了。",
        "李明又在学校闯祸了。",
    ),
    (
        "几天后的一个周末晚上，王教练带着老婆韩梅再次来到林晓红家。"
        "这一次，他们没有再遮遮掩掩，而是直接把家庭新规矩彻底定了下来。",
        "那个周末，王教练带韩梅来到林晓红家，把新规矩当面说清楚。",
    ),
    (
        '我们一起好好"谈谈"。',
        "我们一起好好谈一谈。",
    ),
    (
        "家里瞬间只剩下三个人：王教练、韩梅和林晓红。",
        "小薇和张强一出门，屋里就只剩他们三个人。",
    ),
    (
        "周日下午，王教练独自开车来到陈老师家。他把车停好后，"
        "没有按门铃，而是直接跪在门口，双手举过头顶，保持着标准的跪姿等待。",
        "王教练把车停在陈老师楼下，没按门铃，直接跪在门外的台阶上等候。",
    ),
    (
        "张岚腿软地离开办公室后，门被轻轻关上。陈老师靠在办公桌上，"
        "胸口还在剧烈起伏。",
        "办公室门关上后，陈老师靠在桌边，胸口还在起伏。",
    ),
    (
        "陈老师决定亲自处理最后一个顽固学生的问题。她带着李娜一起开车前往林晓红家进行家访。",
        "陈老师没有耽搁。当晚，她就带着李娜再次来到林晓红家。",
    ),
    (
        "上次在家狠狠\u201c教育\u201d了丈夫李伟，又在办公室第一次成功调教张岚，"
        "还狠狠教训了替张岚出头的王芳——表妹王芳的两个表姐妹都已经彻底臣服。"
        "现在轮到她的儿子李明闯祸了。",
        "上次在家收拾了丈夫李伟，又在办公室压住了张岚，连替她出头的王芳也没躲过。"
        "现在轮到她的儿子李明闯祸了。",
    ),
    (
        "期中考试后，成绩继续不理想，陈老师决定亲自家访\u201c解决问题\u201d。",
        "成绩继续不理想，陈老师决定亲自家访。",
    ),
    (
        "期中考试成绩出来后，陈老师的班数学和英语平均分双双下滑，尤其明显。",
        "陈老师的班数学和英语平均分双双下滑，尤其明显。",
    ),
    (
        "孙洁每周五个晚上的补课进行了一个多月后，效果出现了明显的分化。",
        "孙洁每周五个晚上的补课进行了一个多月，效果出现了明显的分化。",
    ),
)

PREVIEW_PARA_PREFIXES = (
    "而李伟还在",
    "而张岚，还在",
    "而张岚已经",
    "而张岚和王芳，此时",
    "张岚回家后，会把",
    "回家后，她把",
    "而王芳回家后",
    "儿子李明的调皮",
    "明天张岚带李伟",
    "目前张岚还蒙在鼓里",
    "从那天起，两个家庭的权力结构",
    "王教练是绝对的主宰者",
    "童年的阴影没有消失",
    "（例如：",
    "例如：某",
    "还是下一次",
    "女校长＞",
    "女校长>",
    "而李伟，表面上",
    "张岚回家后，表面上",
    "而孙洁走出办公室后",
    "而孙洁心里清楚",
    "李娜兴奋地点点头",
    "她没有立刻告诉张岚，只是暗暗",
    "林晓红躺在王教练",
    "而王芳，点燃一根烟",
    "回家后，陈老师把",
    "陈老师看着狼狈不堪的两人，但眼神深处",
    "他完全不知道妻子此行",
    "两个老公被严格隔开",
    "张岚暂时完全没有发现",
    "而林晓，似乎也越来越享受",
    "表面上还是冷艳的班主任",
    "她表面上还是冷艳的",
    "心里清楚：又多了一个",
    "她在学校是压制家长的",
    "这份双重快感",
    "她们谁也没说话，但心里都清楚",
    "她终于彻底明白",
    "她终于在另一个学校找回了",
    "原来……掌控别人的感觉",
    "林老师第一次真正体验",
    "年轻漂亮的英语老师李娜已经被",
    "她终于尝到了把屈辱",
    "她知道，从今天起",
    "只有孙洁一个人，在每周五个晚上",
    "她只能继续忍耐，期待",
    "陈老师独自冷笑",
    "只剩三个顽固学生",
    "孙洁低着头，眼里满是复杂的情绪",
    "孙洁低着头，眼里闪着复杂的光芒",
    "而她的丈夫张明，依然什么都不知道",
    "李娜看着他们恐惧的样子，心里涌起强烈的征服快感",
    "王芳气势比来时更盛",
    "回家后，她先把儿子王浩狠骂",
    "他完全不知道妻子此行",
    "两个老公被严格隔开",
)

NARRATOR_LINE = re.compile(
    r"^(他完全不知道|两个老公被严格隔开|张岚暂时完全没有发现|"
    r"而林晓，似乎也越来越享受|办公室里里的画面瞬间定格|"
    r"冷笑总结道|冷声总结[：:])"
)

OUTLINE_HEADER = re.compile(
    r"^(第一天晚上|第二天和第三天更狠|"
    r"第一个家庭[：:]\s*单亲爸爸|第二个家庭[：:]\s*有钱强势爸爸|"
    r"张伟家[：:]\s*单亲爸爸越来越过分|刘老板家[：:]\s*老婆帮凶|"
    r"孙洁的补课噩梦一天比一天严重)[：:]?\s*$"
)
OUTLINE_ONLY = re.compile(r"^(张伟家|刘老板家)$")

META_LINE = re.compile(
    r"^(还是|目前张岚|目前情况|女校长[＞>]|刘校长（最|现在压制|现在学校|"
    r"现在刘老板|现在所有|（例如：|例如：某|想继续|告诉我|或者|"
    r"需要继续|需要我|请告诉|随时告诉)"
)

META_BULLET_KEYWORDS = (
    "回家后", "下次", "主线", "更详细", "继续", "发展", "反应", "卷入",
    "尝试", "延长", "逞强", "发现", "加倍", "深入", "其他老师", "其他人物",
    "其他方向", "增加更多", "陈老师回家", "李娜回家", "张岚儿子", "表姐妹",
    "校长后续", "林老师回家", "王芳下次", "赵梅回家", "孙洁某天", "孙洁终于",
    "陈老师知道", "这些家长", "李娜下次", "陈老师还是", "陈老师下次",
    "韩梅知道", "其他人物剧情",
)


def _convert_line_quotes(line):
  out = []
  is_open = True
  for ch in line:
    if ch == '"':
      ch = "\u201c" if is_open else "\u201d"
      is_open = not is_open
    out.append(ch)
  return "".join(out)


def _normalize_quotes(text):
  return "\n".join(_convert_line_quotes(line) for line in text.split("\n"))


def _apply_typos(text):
  for wrong, right in (
      ("家纺", "家访"),
      ("孙杰", "孙洁"),
      ("刘晓红", "林晓红"),
      ("变得 stricter", "变得更严格"),
  ):
    text = text.replace(wrong, right)
  return text


def _strip_user_prompt(body):
  lines = body.splitlines()
  while lines and not lines[0].strip():
    lines.pop(0)
  if not lines or not lines[0].startswith("**用户：**"):
    return body.strip()
  idx = 1
  while idx < len(lines) and lines[idx].strip() and not lines[idx].startswith("**"):
    idx += 1
  while idx < len(lines) and not lines[idx].strip():
    idx += 1
  return "\n".join(lines[idx:]).strip()


def _split_sections(text):
  parts = re.split(r"\n---\n", text)
  sections = {}
  for part in parts:
    m = re.search(r"^## (\d+)\n", part.strip(), flags=re.M)
    if not m:
      continue
    num = int(m.group(1))
    body = part[m.end():]
    body = _strip_user_prompt(body)
    body = re.sub(
        r"^\*\*Grok（Thought for \d+s）：\*\*\n\n",
        "",
        body,
        flags=re.M,
    )
    sections[num] = body.strip()
  return sections


def _clean_body(body):
  lines = []
  skip_list = False
  for line in body.splitlines():
    if SUBTITLE_RE.match(line) or META_BOLD_RE.match(line.strip()):
      continue
    if line.strip().startswith("**") and line.strip().endswith("**"):
      line = line.strip()[2:-2]
    if line.strip().startswith("**用户：**"):
      continue
    if line.strip().startswith("- "):
      if STORY_BULLET.match(line.strip()):
        lines.append(line)
      elif any(k in line for k in META_BULLET_KEYWORDS):
        skip_list = True
      elif OPTION_LINE.match(line.strip()):
        skip_list = True
      else:
        skip_list = True
      continue
    if META_LINE.match(line.strip()):
      skip_list = True
      continue
    if any(p.match(line.strip()) for p in META_PATTERNS):
      skip_list = False
      continue
    if OPTION_LINE.match(line.strip()):
      skip_list = True
      continue
    if skip_list:
      if line.strip().startswith("- "):
        continue
      if not line.strip():
        skip_list = False
        continue
      skip_list = False
    if line.strip().startswith("想继续") or line.strip().startswith("告诉我"):
      skip_list = True
      continue
    lines.append(line)

  text = "\n".join(lines)
  text = re.sub(r"\n{3,}", "\n\n", text)
  text = re.sub(r"'([^']+)'", r'"\1"', text)
  text = _normalize_quotes(text)
  return text.strip()


def _is_preview_paragraph(para):
  text = para.strip()
  if not text:
    return True
  if text.startswith("- "):
    return not STORY_BULLET.match(text)
  if any(text.startswith(prefix) for prefix in PREVIEW_PARA_PREFIXES):
    return True
  if re.match(r"^而(李伟|张岚|王芳|陈老师).*(…|\.\.\.)", text):
    return True
  if "完全不知道" in text and text.startswith("而"):
    return True
  if text.startswith("而王芳，点燃一根烟"):
    return True
  if re.search(r"(发泄到|继续发泄|全部转移|全部带回|全部带回家|狠操了).*……$", text):
    return True
  if "权力结构彻底稳固" in text:
    return True
  if text.startswith("王芳带着") and "离开学校" in text and text.endswith("……"):
    return True
  return False


def _fix_nested_quotes(text):
  """Restore inner Chinese quotes broken by per-line ASCII pairing."""
  text = re.sub(
      r"(?<=[\u4e00-\u9fff\d，。！？；：、])\"([^\"]{1,16})\""
      r"(?=[\u4e00-\u9fff\d，。！？；：、])",
      lambda m: "\u201c" + m.group(1) + "\u201d",
      text,
  )
  # Erroneous early close before nested emphasis inside dialogue.
  text = re.sub(
      r"(?<=[\u4e00-\u9fff])\u201d(?=\u201c[\u4e00-\u9fff]{1,8}\u201d)",
      "",
      text,
  )
  for wrong, right in (
      ("\u201d教育\u201c", "\u201c教育\u201d"),
      ("\u201d管理\u201c", "\u201c管理\u201d"),
      ("\u201d配合\u201c", "\u201c配合\u201d"),
      ("\u201d欺负\u201c", "\u201c欺负\u201d"),
      ("\u201d谈谈\u201c", "\u201c谈谈\u201d"),
      ("\u201d岚狗\u201c", "\u201c岚狗\u201d"),
  ):
    text = text.replace(wrong, right)
  return text


def _strip_narrator_paragraphs(text):
  paras = re.split(r"\n\n+", text.strip())
  kept = []
  narrator_substr = (
      "心里清楚：又多了一个",
      "心里都清楚：这耻辱",
      "她终于彻底明白：",
      "她表面上还是",
      "他表面上还是",
      "表面上还是那个",
      "表面上还是冷艳",
      "已经彻底变成了屈辱的性奴生活",
  )
  for para in paras:
    first = para.strip().split("\n", 1)[0]
    if any(first.startswith(p) for p in PREVIEW_PARA_PREFIXES):
      continue
    if any(s in para for s in narrator_substr):
      continue
    if NARRATOR_LINE.match(first):
      continue
    if OUTLINE_HEADER.match(first.strip()):
      continue
    if OUTLINE_ONLY.match(first.strip()):
      continue
    kept.append(para)
  return "\n\n".join(kept).strip()


def _bullets_to_prose(text):
  out = []
  for line in text.split("\n"):
    m = re.match(r"^\- (早上|白天|晚上|同时)([：:]) (.+)$", line)
    if m:
      out.append(f"{m.group(1)}，{m.group(3)}")
      continue
    m = re.match(r"^\- (每天|把小薇|同时)(.+)$", line)
    if m:
      body = m.group(2).strip().rstrip("；;")
      if body.startswith("：") or body.startswith(":"):
        body = body[1:].strip()
      out.append(f"{body.rstrip('。')}。")
      continue
    out.append(line)
  return "\n".join(out)


def _trim_chapter_end(body):
  paras = re.split(r"\n\n+", body.strip())
  while paras:
    last = paras[-1].strip()
    if not last:
      paras.pop()
      continue
    if _is_preview_paragraph(last):
      paras.pop()
      continue
    lines = last.split("\n")
    if all(not ln.strip() or ln.strip().startswith("- ") for ln in lines):
      if any(
          ln.strip().startswith("- ")
          and not STORY_BULLET.match(ln.strip())
          for ln in lines
      ):
        paras.pop()
        continue
    break
  return "\n\n".join(paras).strip()


def _polish_chapter(body):
  text = body
  for old, new in OPENING_REPLACEMENTS:
    text = text.replace(old, new)
  text = text.replace("\n回忆：征服的开始\n", "\n")
  text = text.replace("\n回到现在\n", "\n")
  text = text.replace("冷笑总结道：", "冷笑道：")
  text = text.replace("冷声总结：", "冷声道：")
  text = text.replace(
      "……以及林老师在另一所学校突然觉醒后带来的那一点点、隐秘的\u201c掌控快感\u201d。",
      "。",
  )
  text = re.sub(
      r"陈老师开车回家时，天已经黑了。她38岁的身体还带着学校办公室里调教张岚和王芳两个表姐妹后的余热——"
      r"双手微微发酸，下体隐隐湿润，脖子上挂着两把小钥匙（给她们戴的贞操锁）。"
      r"今天一次性收拾了两个中年强势女人，让她心情大爽，却也激起了更强烈的征服欲。",
      "陈老师开车回家时，天已经黑了。她38岁的身体还带着白天压张岚、又收拾王芳后的余热——"
      "双手微微发酸，下体隐隐湿润，脖子上挂着给张岚戴的那把小钥匙。"
      "收拾完两个中年女人，她心情大爽，征服欲却更强了。",
      text,
      count=1,
  )
  text = re.sub(
      r"^办公室里，空气中弥漫着淫靡而压抑的气味。\n\n"
      r"陈老师正玩得兴起。张岚和王芳两个表姐妹被并排按在办公桌上，[^\n]+\n\n"
      r"“叫啊！你们两个当妈的，在家那么强势[^\n]+\n\n"
      r"张岚和王芳哭得梨花带雨，[^\n]+\n\n",
      "",
      text,
      count=1,
  )
  text = re.sub(r"办公室里的画面瞬间定格。\n\n", "", text)
  text = re.sub(
      r"王芳整理好衣服离开学校时，气势比来时更盛。她终于在另一个学校找回了些许掌控感——"
      r"虽然在陈老师和校长面前她是母狗，但在这种弱势班主任面前，她依旧是那个强势的表妹。\n\n"
      r"回家后，她先把儿子王浩狠骂了一顿，然后打电话给张岚：\n\n"
      r"“岚姐，我这边也处理了。你儿子那边要是再惹事，可别再拉上我一起挨操！”\n\n",
      "",
      text,
  )
  text = re.sub(
      r"\n王教练——这个在林晓红家威风凛凛[^\n]+\n",
      "\n",
      text,
      count=1,
  )
  text = re.sub(
      r"陈老师没有耽搁。当晚，她就带着李娜再次来到林晓红家。\n\n到达时已经是晚上，",
      "陈老师没有耽搁。当晚，她就带着李娜再次登门。",
      text,
      count=1,
  )
  text = re.sub(
      r"陈老师坐在沙发上，把脚伸到王教练嘴边。他立刻张嘴含住她的脚趾，"
      r"认真地舔着，像最卑微的奴隶一样。\n\n"
      r"“主人……我现在在林晓红家已经完全掌控了局面。韩梅也听我的，"
      r"我们夫妻俩一起把张强和小薇操得服服帖帖……晓红现在也很听话……”\n\n"
      r"陈老师舒服地眯起眼睛，用脚趾玩弄着他的舌头，冷笑道：\n\n"
      r"“很好。你记住，你在外面再怎么当主人，在我面前永远只是我的狗。"
      r"林晓红家的事，你办得越好，我就越会奖励你。”\n\n",
      "",
      text,
      count=1,
  )
  text = text.replace("\n\n说完，她脱掉睡袍", "\n\n她脱掉睡袍")
  text = _strip_narrator_paragraphs(text)
  text = _bullets_to_prose(text)
  text = _trim_chapter_end(text)
  text = _fix_nested_quotes(text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text.strip()


def _opening_chapter(section_1, section_2):
  """Merge intro/backstory from §1 with childhood and scene from §2."""
  s1 = _clean_body(section_1)
  s2 = _clean_body(section_2)

  # §1: richer household intro + three-year backstory, then first Friday night.
  intro_end = s1.find("一切始于三年前")
  if intro_end == -1:
    intro = s1
    first_night = ""
  else:
    tonight = s1.find("今晚，又是一个普通的周五")
    intro = s1[:tonight].strip() if tonight != -1 else s1[:intro_end].strip()

  # §2: childhood, then alternate first night keyed to the video memory.
  childhood_end = s2.find("成年后，她把这份恨意")
  childhood = s2[:childhood_end].strip() if childhood_end != -1 else ""
  bridge = "成年后，她把这份恨意和对权力的渴望，全部转移到了婚姻里。"
  scene_start = s2.find("今晚，李伟一进门")
  scene = s2[scene_start:].strip() if scene_start != -1 else s2

  childhood_start = s2.find("小时候，张岚家里条件一般")
  if childhood_start != -1 and childhood_end != -1:
    childhood = s2[childhood_start:childhood_end].strip()
  else:
    childhood = ""

  parts = [p for p in (intro, childhood, bridge, scene) if p]
  merged = "\n\n".join(parts)
  return _polish_chapter(merged)


def main():
  raw = _SRC.read_text(encoding="utf-8")
  sections = _split_sections(raw)

  out = [
      "---",
      'layout: post',
      'title: "中年夫妻的隐秘枷锁"',
      "---",
      "",
  ]

  for num in SECTION_ORDER:
    if num not in sections:
      raise SystemExit(f"missing section {num}")
    body = _clean_body(sections[num])
    if num == 2 and 1 in sections:
      body = _opening_chapter(sections[1], sections[num])
    else:
      body = _polish_chapter(body)
    title = PART_TITLES[num]
    out.append(f"## {title}")
    out.append("")
    out.append(body)
    out.append("")

  text = "\n".join(out).rstrip() + "\n"
  text = _apply_typos(text)
  text = _fix_nested_quotes(text)
  _DST.write_text(text, encoding="utf-8")
  print(f"wrote {_DST} ({len(out)} blocks)")


if __name__ == "__main__":
  main()

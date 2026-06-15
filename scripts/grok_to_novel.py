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
    re.compile(r"^……$"),
]

SUBTITLE_RE = re.compile(r"^### .+$")
META_BOLD_RE = re.compile(r"^\*\*(核心压制链|主要人物|其他设定|\d+\.)")
OPTION_LINE = re.compile(
    r"^\- .*(其他方向|详细场景|主线回归|最新发展|想加的|续写更长|其他剧情|其他发展)"
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
  return "\n\n".join(parts)


def main():
  raw = _SRC.read_text(encoding="utf-8")
  sections = _split_sections(raw)

  out = [
      "---",
      'layout: post',
      'title: "中年夫妻的隐秘枷锁"',
      "---",
      "",
      "> 整理自 Grok 对话："
      " https://grok.com/share/bGVnYWN5LWNvcHk_c83e2e7e-6612-45ef-9a28-c36a621c16d7",
      "",
  ]

  for num in SECTION_ORDER:
    if num not in sections:
      raise SystemExit(f"missing section {num}")
    body = _clean_body(sections[num])
    if num == 2 and 1 in sections:
      body = _opening_chapter(sections[1], sections[num])
    title = PART_TITLES[num]
    out.append(f"## {title}")
    out.append("")
    out.append(body)
    out.append("")

  text = "\n".join(out).rstrip() + "\n"
  text = _apply_typos(text)
  _DST.write_text(text, encoding="utf-8")
  print(f"wrote {_DST} ({len(out)} blocks)")


if __name__ == "__main__":
  main()

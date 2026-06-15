"""Normalize the Grok transcript and save a cleaned copy.

Converts ASCII double quotes in the body to Chinese curly quotes and fixes a
handful of obvious typos, then writes the result to a separate file so the
verbatim transcript stays untouched.
"""

import pathlib

_SRC = pathlib.Path(
    "_posts/ideas/middle-aged-wife-dominant-control-grok.md"
)
_DST = pathlib.Path(
    "_posts/ideas/middle-aged-wife-dominant-control-grok-fixed.md"
)

_TYPO_FIXES = (
    ("家纺", "家访"),
    ("孙杰", "孙洁"),
    ("刘晓红", "林晓红"),
    ("变得 stricter", "变得更严格"),
)


def _convert_line(line):
  """Pair ASCII double quotes within one line as Chinese curly quotes.

  Dialogue never spans lines here, so alternating open/close per line is more
  robust than a context heuristic for punctuation-adjacent quotes.
  """
  out = []
  is_open = True
  for ch in line:
    if ch == '"':
      ch = "\u201c" if is_open else "\u201d"
      is_open = not is_open
    out.append(ch)
  return "".join(out)


def main():
  text = _SRC.read_text(encoding="utf-8")
  for wrong, right in _TYPO_FIXES:
    text = text.replace(wrong, right)

  odd_lines = []
  converted = []
  for lineno, line in enumerate(text.split("\n"), start=1):
    if line.count('"') % 2:
      odd_lines.append(lineno)
    converted.append(_convert_line(line))
  text = "\n".join(converted)

  _DST.write_text(text, encoding="utf-8")
  remaining = text.count('"')
  print(f"wrote {_DST} ({len(text)} chars); remaining ASCII quotes: {remaining}")
  if odd_lines:
    print(f"lines with an odd quote count (check manually): {odd_lines}")
  else:
    print("all lines had balanced quotes")


if __name__ == "__main__":
  main()

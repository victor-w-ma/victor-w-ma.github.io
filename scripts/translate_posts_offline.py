#!/usr/bin/env python3
"""Write static English includes for published Jekyll posts.

Each published story is translated once. The English HTML is stored under
``_includes/translations/en/`` and linked from the post front matter. Reading
a page does not call a translation service.
"""

from __future__ import annotations

import argparse
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
INCLUDES_DIR = ROOT / "_includes" / "translations" / "en"
CACHE_PATH = Path("/tmp/static-en-translate-cache.json")
MAX_CHUNK = 500
BING_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
DATE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
HEADING = re.compile(r"^(#{1,6})\s+(\S.*?)\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
PUBLISHED_FALSE = re.compile(r"(?m)^published:\s*false\s*$")
TITLE_LINE = re.compile(r"(?m)^title:\s*(.*?)\s*$")


def yaml_quote(value: str) -> str:
    """Return a double-quoted YAML scalar."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def unquote_scalar(raw: str) -> str:
    """Strip one layer of YAML quotes from a title."""
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        inner = text[1:-1]
        if text[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return text


def escape_html(text: str) -> str:
    """Escape text for an HTML text node and neutralize Liquid tags."""
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return escaped.replace("{%", "&#123;%").replace("{{", "&#123;&#123;")


def cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    return cjk / len(text)


def split_long(text: str, limit: int = MAX_CHUNK) -> list[str]:
    """Split text on sentence boundaries so each piece fits in one request."""
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[。！？!?；;])", text)
    parts: list[str] = []
    buffer = ""
    for sentence in sentences:
        if not sentence:
            continue
        if buffer and len(buffer) + len(sentence) > limit:
            parts.append(buffer)
            buffer = sentence
        else:
            buffer += sentence
        while len(buffer) > limit:
            parts.append(buffer[:limit])
            buffer = buffer[limit:]
    if buffer:
        parts.append(buffer)
    return parts


def polish_title(text: str) -> str:
    """Capitalize a machine-translated title and drop a trailing period."""
    title = text.strip().strip('"').strip("“”").rstrip(".").strip()
    if title[:1].islower():
        title = title[:1].upper() + title[1:]
    return title


def join_pieces(parts: list[str]) -> str:
    """Join translated sentence pieces into one paragraph."""
    output = ""
    for part in parts:
        piece = re.sub(r"\s+", " ", part).strip()
        if not piece:
            continue
        if output and output[-1] not in " \n" and piece[0] not in ".,;:!?":
            output += " "
        output += piece
    return output


def is_comment_block(block: str) -> bool:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return False
    return all(
        line.startswith("<!--") and line.endswith("-->") for line in lines
    )


def is_list_block(block: str) -> bool:
    lines = [line for line in block.splitlines() if line.strip()]
    return bool(lines) and all(LIST_ITEM.match(line) for line in lines)


def list_item_text(line: str) -> str:
    return LIST_ITEM.sub("", line, count=1).strip()


class Translator:
    """Cached client for one-shot Google Translate requests."""

    def __init__(self, cache_path: Path, workers: int) -> None:
        self._cache_path = cache_path
        self._workers = workers
        self._lock = threading.Lock()
        self._cache: dict[str, str] = {}
        self.source_characters = 0
        self.http_requests = 0
        self._gap = 0.35
        self._next_slot = 0.0
        self._opener = None
        self._bing_key = ""
        self._bing_token = ""
        self._bing_ig = ""
        self._bing_ready = 0.0
        self._sfx = 0
        self._unsaved = 0
        if cache_path.exists():
            self._cache = json.loads(cache_path.read_text(encoding="utf-8"))

    def _acquire(self) -> None:
        with self._lock:
            now = time.time()
            wait = max(0.0, self._next_slot - now)
            self._next_slot = max(now, self._next_slot) + self._gap
        if wait:
            time.sleep(wait)

    def _penalize(self, seconds: float) -> None:
        with self._lock:
            self._next_slot = max(self._next_slot, time.time() + seconds)

    def save(self) -> None:
        with self._lock:
            payload = json.dumps(self._cache, ensure_ascii=False)
        self._cache_path.write_text(payload, encoding="utf-8")

    def translate_many(self, texts: list[str]) -> dict[str, str]:
        """Translate each distinct string, batching short strings into one request."""
        pending: list[str] = []
        seen: set[str] = set()
        with self._lock:
            for text in texts:
                if not text or text in seen or text in self._cache:
                    continue
                seen.add(text)
                pending.append(text)
        if pending:
            with ThreadPoolExecutor(max_workers=self._workers) as pool:
                list(pool.map(self._translate_one, pending))
            self.save()
        with self._lock:
            return {text: self._cache.get(text, "") for text in texts if text}

    def _translate_one(self, text: str) -> None:
        self._store(text, self._translate(text))
        snapshot = None
        with self._lock:
            self._unsaved += 1
            if self._unsaved >= 40:
                self._unsaved = 0
                snapshot = dict(self._cache)
                print(f"cache {len(snapshot)}", flush=True)
        if snapshot is not None:
            self._cache_path.write_text(
                json.dumps(snapshot, ensure_ascii=False),
                encoding="utf-8",
            )

    def _store(self, source: str, translated: str) -> None:
        with self._lock:
            if source in self._cache:
                return
            self._cache[source] = translated
            self.source_characters += len(source)

    def _translate(self, text: str) -> str:
        delay = 2.0
        last_error: Exception | None = None
        for _ in range(4):
            try:
                translated = self._request(text)
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code in (401, 405, 429, 503):
                    self._penalize(delay)
                if error.code == 401:
                    with self._lock:
                        self._bing_ready = 0
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                    ValueError) as error:
                last_error = error
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            if translated.strip():
                return translated
            last_error = ValueError("empty translation")
            time.sleep(delay)
            delay = min(delay * 2, 30)
        raise RuntimeError(f"translation failed: {last_error}")

    def _refresh_bing(self) -> None:
        """Load a Bing Translator session token. Caller holds ``_lock``."""
        if self._opener is None:
            cookies = urllib.request.HTTPCookieProcessor()
            self._opener = urllib.request.build_opener(cookies)
        page = urllib.request.Request(
            "https://www.bing.com/translator",
            headers={"User-Agent": BING_UA},
        )
        with self._opener.open(page, timeout=30) as response:
            html = response.read().decode("utf-8", "replace")
        params = re.search(
            r'params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]',
            html,
        )
        ig_match = re.search(r'IG:"([A-Z0-9]+)"', html)
        if not params or not ig_match:
            raise ValueError("Bing translator token was not on the page")
        self._bing_key = params.group(1)
        self._bing_token = params.group(2)
        self._bing_ig = ig_match.group(1)
        self._bing_ready = time.time() + 20 * 60

    def _request(self, text: str) -> str:
        self._acquire()
        with self._lock:
            if self._opener is None or time.time() >= self._bing_ready:
                self._refresh_bing()
            self._sfx += 1
            sfx = self._sfx
            opener = self._opener
            key = self._bing_key
            token = self._bing_token
            ig_value = self._bing_ig
        form = urllib.parse.urlencode({
            "fromLang": "zh-Hans",
            "to": "en",
            "text": text,
            "token": token,
            "key": key,
        }).encode("utf-8")
        url = (
            "https://www.bing.com/ttranslatev3?isVertical=1"
            f"&IG={ig_value}&IID=translator.5023&SFX={sfx}"
        )
        request = urllib.request.Request(
            url,
            data=form,
            method="POST",
            headers={
                "User-Agent": BING_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.bing.com/translator",
                "Origin": "https://www.bing.com",
            },
        )
        with opener.open(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
        with self._lock:
            self.http_requests += 1
        try:
            return payload[0]["translations"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError(f"unexpected Bing response: {payload!r}") from error


def published_posts() -> list[Path]:
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if not DATE_NAME.match(path.name):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        close = text.find("\n---\n", 4)
        if close == -1:
            continue
        front_matter = text[4:close]
        if PUBLISHED_FALSE.search(front_matter):
            continue
        if "en_include:" in front_matter:
            continue
        posts.append(path)
    return posts


def post_title(front_matter: str, fallback: str) -> str:
    match = TITLE_LINE.search(front_matter)
    if not match:
        return fallback
    return unquote_scalar(match.group(1)) or fallback


def parse_blocks(body: str) -> list[tuple]:
    """Split a Markdown body into heading, list, comment, and paragraph blocks."""
    blocks = []
    for raw in re.split(r"\n\s*\n", body.strip("\n")):
        block = raw.strip("\n")
        if not block.strip():
            continue
        if is_comment_block(block):
            blocks.append(("comment", block.strip()))
            continue
        heading = HEADING.match(block) if "\n" not in block else None
        if heading:
            blocks.append(("h", len(heading.group(1)), heading.group(2).strip()))
            continue
        if block.startswith("```"):
            inner = re.sub(r"^```[^\n]*\n?|```$", "", block).strip()
            blocks.append(("pre", inner))
            continue
        if is_list_block(block):
            items = [
                list_item_text(line)
                for line in block.splitlines()
                if line.strip()
            ]
            blocks.append(("list", items))
            continue
        paragraph = re.sub(r"\s*\n\s*", " ", block).strip()
        if paragraph:
            blocks.append(("p", paragraph))
    return blocks


def strings_for_post(title: str, blocks: list[tuple]) -> list[str]:
    texts = split_long(title)
    for block in blocks:
        kind = block[0]
        if kind in {"h", "p", "pre"}:
            texts.extend(split_long(block[-1]))
        elif kind == "list":
            for item in block[1]:
                texts.extend(split_long(item))
    return texts


def render_html(blocks: list[tuple], translated: dict[str, str]) -> str:
    """Render translated blocks as HTML paragraphs and headings."""
    parts: list[str] = []
    for block in blocks:
        kind = block[0]
        if kind == "comment":
            parts.append(block[1])
            continue
        if kind == "h":
            level = block[1]
            text = lookup(block[2], translated)
            parts.append(f"<h{level}>{escape_html(text)}</h{level}>")
            continue
        if kind == "pre":
            text = lookup(block[1], translated)
            parts.append(f"<pre>{escape_html(text)}</pre>")
            continue
        if kind == "list":
            items = []
            for item in block[1]:
                items.append(f"<li>{escape_html(lookup(item, translated))}</li>")
            parts.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        text = lookup(block[1], translated)
        parts.append(f"<p>{escape_html(text)}</p>")
    return "\n\n".join(parts) + "\n"


def lookup(source: str, translated: dict[str, str]) -> str:
    """Resolve a source string to English, preferring a direct cache hit."""
    direct = translated.get(source)
    if direct is not None:
        flat = re.sub(r"\s+", " ", direct).strip()
        if cjk_ratio(flat) <= 0.35 or cjk_ratio(source) <= 0.4 or len(source) < 80:
            return flat
    pieces = [translated.get(piece, piece) for piece in split_long(source)]
    return join_pieces(pieces)


def stubborn_sources(texts: list[str], translated: dict[str, str]) -> list[str]:
    """Return long sources whose translation is still mostly Chinese."""
    retry = []
    for source in texts:
        if len(source) < 80 or cjk_ratio(source) < 0.4:
            continue
        pieces = split_long(source, limit=400)
        combined = join_pieces(
            translated.get(piece, piece) for piece in split_long(source)
        )
        if cjk_ratio(combined) > 0.35:
            retry.extend(pieces)
    return retry


def add_front_matter(text: str, title_en: str, include_rel: str) -> str:
    """Insert English keys after the title without touching the body."""
    if not text.startswith("---\n"):
        raise ValueError("missing front matter")
    close = text.find("\n---\n", 4)
    if close == -1:
        raise ValueError("unclosed front matter")
    front_matter = text[4:close]
    if "en_include:" in front_matter:
        return text
    block = (
        f"title_en: {yaml_quote(title_en)}\n"
        f"en_include: {include_rel}\n"
        "en_machine: true\n"
    )
    lines = front_matter.splitlines(keepends=True)
    inserted = False
    output: list[str] = []
    for line in lines:
        output.append(line)
        if not inserted and line.startswith("title:"):
            if output and not output[-1].endswith("\n"):
                output[-1] += "\n"
            output.append(block)
            inserted = True
    if not inserted:
        output.append(block)
    new_front = "".join(output)
    if not new_front.endswith("\n"):
        new_front += "\n"
    body = text[close + 5:]
    return f"---\n{new_front}---\n{body}"


def include_rel(path: Path) -> str:
    match = DATE_NAME.match(path.name)
    if not match:
        raise ValueError(path.name)
    return f"translations/en/{match.group(2)}.html"


def read_post_text(path: Path) -> tuple[str, str]:
    """Return post text with LF endings, plus the file's original newline."""
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text, newline


def write_post_text(path: Path, text: str, newline: str) -> None:
    payload = text if newline == "\n" else text.replace("\n", newline)
    path.write_bytes(payload.encode("utf-8"))


def translate_post(path: Path, translator: Translator) -> tuple[str, int]:
    """Translate one post. Returns the English title and source character count."""
    text, newline = read_post_text(path)
    close = text.find("\n---\n", 4)
    front_matter = text[4:close]
    body = text[close + 5:]
    title = post_title(front_matter, path.stem)
    blocks = parse_blocks(body)
    needed = strings_for_post(title, blocks)
    translated = translator.translate_many(needed)
    extra = stubborn_sources(needed, translated)
    if extra:
        # Drop the failed long-string cache entries by translating smaller pieces.
        translated.update(translator.translate_many(extra))
        for source in needed:
            pieces = [translated.get(piece, "") for piece in split_long(source, 400)]
            if pieces and all(pieces):
                translated[source] = join_pieces(pieces)
    title_en = polish_title(lookup(title, translated) or title)
    html = render_html(blocks, translated)
    rel = include_rel(path)
    destination = ROOT / "_includes" / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    updated = add_front_matter(text, title_en, rel)
    write_post_text(path, updated, newline)
    source_chars = len(title) + len(body.strip("\n"))
    return title_en, source_chars


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--cache", type=Path, default=CACHE_PATH)
    args = parser.parse_args()
    posts = published_posts()
    if args.limit:
        posts = posts[:args.limit]
    translator = Translator(args.cache, args.workers)
    total_source = 0
    done = 0
    print(f"posts {len(posts)}", flush=True)
    for index, path in enumerate(posts, start=1):
        try:
            title_en, source_chars = translate_post(path, translator)
        except (RuntimeError, urllib.error.URLError, OSError, ValueError) as error:
            print(f"[{index}/{len(posts)}] FAIL {path.name}: {error}", flush=True)
            continue
        done += 1
        total_source += source_chars
        print(
            f"[{index}/{len(posts)}] {path.name} -> {title_en[:80]}",
            flush=True,
        )
    translator.save()
    print(
        f"done {done} story_characters {total_source} "
        f"api_characters {translator.source_characters} "
        f"http_requests {translator.http_requests}",
        flush=True,
    )


if __name__ == "__main__":
    main()

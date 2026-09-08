#!/usr/bin/env python3
"""Build the "Python Mastery" book into ONE self-contained HTML file.

    python3 build.py          ->  dist/index.html

No third-party dependencies. The output file works offline: open it by
double-clicking, no server required.
"""
from __future__ import annotations

import base64
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS_DIR = ROOT / "chapters"
ASSETS_DIR = ROOT / "assets"
TEMPLATE_FILE = ROOT / "template.html"
OUTPUT_DIR = ROOT / "dist"
OUTPUT_FILE = OUTPUT_DIR / "index.html"

PART_TITLES = {
    0: "Start Here",
    1: "I · Foundations",
    2: "II · Leveling Up",
    3: "III · Real-World Python",
    4: "IV · Track A · Full-Stack Web",
    5: "V · Track B · Game Development",
    6: "VI · Appendices",
}

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
IMAGE_RE = re.compile(r"\A!\[(?P<alt>[^\]]*)\]\((?P<src>figures/[^)]+)\)\s*\Z")
HEADING_RE = re.compile(r"<h([23]) id=\"([^\"]+)\">(.*?)</h\1>", re.DOTALL)
TASK_RE = re.compile(r"^\[( |x)\]\s+(.*)$")


@dataclass
class Chapter:
    number: int
    part: int
    slug: str
    title: str
    summary: str
    minutes: int
    tags: list[str]
    body_html: str
    toc: list[dict]


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------
def parse_front_matter(text: str) -> tuple[dict, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    data: dict = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            data[key.strip()] = value
    return data, text[match.end():]


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text)[:70]


# --------------------------------------------------------------------------
# Inline formatting
# --------------------------------------------------------------------------
def inline(text: str) -> str:
    stash: list[str] = []
    escaped = html.escape(text, quote=False)

    def keep(match: re.Match) -> str:
        stash.append(match.group(1))
        return f"\x00{len(stash) - 1}\x00"

    escaped = INLINE_CODE_RE.sub(keep, escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)

    def restore(match: re.Match) -> str:
        return f"<code>{stash[int(match.group(1))]}</code>"

    return re.sub("\x00(\\d+)\x00", restore, escaped)


# --------------------------------------------------------------------------
# Block level conversion
# --------------------------------------------------------------------------
CALLOUT_KINDS = {
    "note": ("Note", "i"),
    "tip": ("Tip", "★"),
    "warning": ("Warning", "▲"),
    "danger": ("Danger", "✕"),
    "scenario": ("Real scenario", "◈"),
    "solution": ("Solution", "✔"),
    "pitfall": ("Common pitfall", "!"),
    "try": ("Try it", "▶"),
}


def render_code(lang: str, code: str) -> str:
    pretty = {"py": "python", "sh": "bash", "console": "bash", "js": "javascript",
              "html": "html", "sql": "sql", "json": "json", "yaml": "yaml",
              "toml": "toml", "text": "text"}
    lang_key = pretty.get(lang.lower(), lang.lower() or "text")
    label = "output" if lang.lower() in {"console", "text", ""} else lang_key
    body = html.escape(code.rstrip("\n"), quote=False)
    return (
        f'<div class="code" data-lang="{lang_key}">'
        f'<div class="code-bar"><span class="code-lang">{html.escape(label)}</span>'
        f'<button class="copy-btn" type="button">Copy</button></div>'
        f'<pre><code class="language-{lang_key}">{body}</code></pre></div>'
    )


def render_figure(alt: str, src: str) -> str:
    """Inline a figure from assets/figures so the book stays a single file.

    SVG is inlined as markup (crisp, tiny). PNG/JPG is inlined base64 — used for
    screenshots of the actually-running projects.
    """
    path = ASSETS_DIR / src
    if not path.exists():
        print(f"  ! missing figure: {src}")
        return f'<p><em>[missing figure: {src}]</em></p>'

    if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        inner = f'<img src="data:{mime};base64,{data}" alt="{html.escape(alt, quote=True)}">'
    else:
        svg = path.read_text(encoding="utf-8").strip()
        svg = re.sub(r"\A<\?xml[^>]*\?>", "", svg, flags=re.I).strip()
        svg = re.sub(r"\A<!DOCTYPE[^>]*>", "", svg, flags=re.I).strip()
        # A <style> element inside inlined SVG leaks into the whole document — strip it.
        svg = re.sub(r"<style\b.*?</style>", "", svg, flags=re.S | re.I).strip()
        inner = svg

    caption = f"<figcaption>{html.escape(alt)}</figcaption>" if alt else ""
    return f'<figure class="fig">{inner}{caption}</figure>'


def convert(lines: list[str]) -> str:
    out: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def list_item(text: str, ordered: bool, depth: int, index: int) -> str:
        task = TASK_RE.match(text)
        if task:
            checked = " checked" if task.group(1) == "x" else ""
            return (
                f'<li class="task" style="margin-left:{depth * 1.25}rem">'
                f'<label><input type="checkbox" class="task-box"{checked}>'
                f"<span>{inline(task.group(2))}</span></label></li>"
            )
        cls = "ol-item" if ordered else "ul-item"
        return f'<li class="{cls}" style="margin-left:{depth * 1.25}rem">{inline(text)}</li>'

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        # blank line
        if not stripped:
            flush_para()
            i += 1
            continue

        # callout container
        if stripped.startswith(":::"):
            flush_para()
            spec = stripped[3:].strip()
            if spec == "":  # stray closing marker
                i += 1
                continue
            kind, _, title = spec.partition(" ")
            kind = kind.lower()
            inner: list[str] = []
            i += 1
            while i < n and lines[i].strip() != ":::":
                inner.append(lines[i])
                i += 1
            i += 1  # skip closing :::
            label, icon = CALLOUT_KINDS.get(kind, (kind.title(), "•"))
            heading = html.escape(title.strip() or label)
            out.append(
                f'<div class="callout callout-{kind}">'
                f'<div class="callout-head"><span class="callout-icon">{icon}</span>{heading}</div>'
                f'<div class="callout-body">{convert(inner)}</div></div>'
            )
            continue

        # fenced code (de-indented by the fence's own indent, so blocks nested
        # inside markdown lists render flush-left)
        if stripped.startswith("```"):
            flush_para()
            lang = stripped[3:].strip()
            indent = len(raw) - len(raw.lstrip())
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                item = lines[i].rstrip("\n")
                buf.append(item[indent:] if item[:indent].strip() == "" else item)
                i += 1
            i += 1
            out.append(render_code(lang, "\n".join(buf)))
            continue

        # figure  ![caption](figures/name.svg)
        image = IMAGE_RE.match(stripped)
        if image:
            flush_para()
            out.append(render_figure(image.group("alt"), image.group("src")))
            i += 1
            continue

        # headings
        heading = re.match(r"^(#{2,4})\s+(.*)$", stripped)
        if heading:
            flush_para()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            out.append(f'<h{level} id="{slugify(text)}">{inline(text)}</h{level}>')
            i += 1
            continue

        # horizontal rule
        if stripped in {"---", "***", "___"}:
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            flush_para()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in header)
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows
            )
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue

        # lists
        bullet = re.match(r"^(\s*)[-*]\s+(.*)$", raw)
        ordered = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", raw)
        if bullet or ordered:
            flush_para()
            items: list[str] = []
            is_ordered = bool(ordered)
            while i < n:
                raw_item = lines[i]
                b = re.match(r"^(\s*)[-*]\s+(.*)$", raw_item)
                o = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", raw_item)
                if is_ordered and o:
                    depth = len(o.group(1)) // 2
                    items.append(list_item(o.group(3).strip(), True, depth, i))
                elif not is_ordered and b:
                    depth = len(b.group(1)) // 2
                    items.append(list_item(b.group(2).strip(), False, depth, i))
                elif raw_item.strip() == "":
                    if i + 1 < n and re.match(r"^\s*([-*]|\d+[.)])\s+", lines[i + 1]):
                        i += 1
                        continue
                    break
                else:
                    break
                i += 1
            tag = "ol" if is_ordered else "ul"
            out.append(f'<{tag} class="md-list">{"".join(items)}</{tag}>')
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return "".join(out)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def load_chapters() -> list[Chapter]:
    chapters: list[Chapter] = []
    for path in sorted(CHAPTERS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        if not meta:
            print(f"  ! skipping {path.name} (no front matter)")
            continue
        body_html = convert(body.splitlines())
        toc = [
            {"level": int(m.group(1)), "id": m.group(2),
             "text": html.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()}
            for m in HEADING_RE.finditer(body_html)
            if int(m.group(1)) in (2, 3)
        ]
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        chapters.append(
            Chapter(
                number=int(meta.get("chapter", 0)),
                part=int(meta.get("part", 6)),
                slug=path.stem,
                title=meta.get("title", path.stem),
                summary=meta.get("summary", ""),
                minutes=int(meta.get("minutes", 15)),
                tags=tags,
                body_html=body_html,
                toc=toc,
            )
        )
    chapters.sort(key=lambda c: (c.part, c.number))
    return chapters


def build_nav(chapters: list[Chapter]) -> str:
    parts: dict[int, list[Chapter]] = {}
    for chapter in chapters:
        parts.setdefault(chapter.part, []).append(chapter)

    blocks = []
    for part in sorted(parts):
        items = []
        for chapter in parts[part]:
            badge = f"{chapter.number:02d}" if chapter.number else "••"
            items.append(
                f'<a class="nav-link" href="#/{chapter.slug}" data-slug="{chapter.slug}">'
                f'<span class="nav-num">{badge}</span>'
                f'<span class="nav-title">{html.escape(chapter.title)}</span>'
                f'<span class="nav-check" aria-hidden="true">✓</span></a>'
            )
        blocks.append(
            f'<div class="nav-part"><button class="nav-part-btn" type="button">'
            f'<span>{html.escape(PART_TITLES.get(part, f"Part {part}"))}</span>'
            f'<span class="chev">▾</span></button>'
            f'<div class="nav-items">{"".join(items)}</div></div>'
        )
    return "".join(blocks)


def build_content(chapters: list[Chapter]) -> str:
    sections = []
    for idx, chapter in enumerate(chapters):
        prev_slug = chapters[idx - 1].slug if idx > 0 else ""
        next_slug = chapters[idx + 1].slug if idx + 1 < len(chapters) else ""
        prev_title = chapters[idx - 1].title if idx > 0 else ""
        next_title = chapters[idx + 1].title if idx + 1 < len(chapters) else ""
        badge = f"Chapter {chapter.number:02d}" if chapter.number else "Start Here"
        toc_html = "".join(
            f'<a class="toc-link toc-{t["level"]}" href="#{t["id"]}" data-target="{t["id"]}">'
            f'{html.escape(t["text"])}</a>'
            for t in chapter.toc
        )
        tags_html = "".join(f'<span class="chip">{html.escape(t)}</span>' for t in chapter.tags)
        sections.append(
            f'<section class="chapter" id="{chapter.slug}" data-slug="{chapter.slug}" hidden>'
            f'<header class="chapter-head">'
            f'<div class="chapter-eyebrow">{badge} · {chapter.minutes} min</div>'
            f'<h1>{html.escape(chapter.title)}</h1>'
            f'<p class="chapter-summary">{html.escape(chapter.summary)}</p>'
            f'<div class="chips">{tags_html}</div></header>'
            f'<div class="chapter-body">{chapter.body_html}</div>'
            f'<div class="chapter-foot">'
            f'<button class="done-btn" type="button" data-slug="{chapter.slug}">Mark chapter complete</button>'
            f'<div class="pager">'
            + (f'<a class="pager-btn" href="#/{prev_slug}" data-slug="{prev_slug}">← {html.escape(prev_title)}</a>' if prev_slug else "<span></span>")
            + (f'<a class="pager-btn next" href="#/{next_slug}" data-slug="{next_slug}">{html.escape(next_title)} →</a>' if next_slug else "<span></span>")
            + "</div></div></section>"
        )
    return "".join(sections)


def main() -> None:
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    css = (ASSETS_DIR / "style.css").read_text(encoding="utf-8")
    js = (ASSETS_DIR / "app.js").read_text(encoding="utf-8")

    chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapters")

    payload = [
        {
            "slug": c.slug,
            "title": c.title,
            "number": c.number,
            "part": c.part,
            "minutes": c.minutes,
            "summary": c.summary,
            "tags": c.tags,
            "toc": c.toc,
        }
        for c in chapters
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    page = (
        template
        .replace("/*__STYLE__*/", css)
        .replace("/*__DATA__*/", "const CHAPTERS = " + json.dumps(payload, ensure_ascii=False) + ";")
        .replace("/*__SCRIPT__*/", js)
        .replace("__PART_NAMES__", json.dumps(PART_TITLES, ensure_ascii=False))
        .replace("__NAV__", build_nav(chapters))
        .replace("__CONTENT__", build_content(chapters))
    )
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"Built {OUTPUT_FILE}  ({size_kb:.0f} KB, {len(chapters)} chapters)")


if __name__ == "__main__":
    main()

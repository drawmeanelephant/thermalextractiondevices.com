"""Helpers for generating Boris/ApexMarkdown content.

Supports the feature surface confirmed in the Boris afterparty compiler:
callouts (``<Aside kind="...">``), wiki-links (``[[entity-id|label]]``),
definition lists, footnotes, task lists, stable heading IDs (``{#id}``),
and aligned tables. All cell values are escaped so user/source text cannot
break table alignment or frontmatter.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

_ESCAPE_RE = re.compile(r"[|\r\n]")


def escape_cell(value) -> str:
    """Escape a value for use inside a Markdown table cell."""
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text.replace("|", "\\|")


def frontmatter(
    *,
    title: str,
    entity_id: str,
    parent: Optional[str] = None,
    status: str = "published",
    tags: Optional[list[str]] = None,
    relations: Optional[list[str]] = None,
) -> str:
    """Render a closed-grammar Boris frontmatter block.

    Only keys permitted by the project's frontmatter policy are emitted
    (``id, title, parent, status, tags, relations``).
    """
    lines = ["---"]
    lines.append(f"title: {_quote(title)}")
    if parent:
        lines.append(f"parent: {_escape_quotes(str(parent))}")
    # Boris convention (and the repo's existing pages) use an unquoted id.
    lines.append(f"id: {_escape_quotes(str(entity_id))}")
    lines.append(f"status: {status}")
    if tags:
        rendered = ", ".join(f'"{_escape_quotes(tag)}"' for tag in tags)
        lines.append(f"tags: [{rendered}]")
    if relations:
        rendered = ", ".join(f"relates_to={rel}" for rel in relations)
        lines.append(f"relations: [{rendered}]")
    lines.append("---")
    return "\n".join(lines)


def _quote(value: str) -> str:
    return '"' + _escape_quotes(str(value)) + '"'


def _escape_quotes(value: str) -> str:
    return str(value).replace('"', '\\"')


def h1(text: str) -> str:
    return f"# {text}"


def h2(text: str, anchor: Optional[str] = None) -> str:
    if anchor:
        return f"## {text} {{#{anchor}}}"
    return f"## {text}"


def h3(text: str, anchor: Optional[str] = None) -> str:
    if anchor:
        return f"### {text} {{#{anchor}}}"
    return f"### {text}"


def table(headers: Iterable[str], rows: Iterable[Iterable], *, align: Optional[str] = None) -> str:
    """Render an aligned GFM table.

    ``align`` may be ``"left" | "center" | "right"`` applied to all columns.
    """
    header_cells = [escape_cell(h) for h in headers]
    body = []
    for row in rows:
        body.append("| " + " | ".join(escape_cell(cell) for cell in row) + " |")
    if not body:
        return "_(no rows)_"
    separator = "| " + " | ".join(["---"] * len(header_cells)) + " |"
    if align == "right":
        separator = "| " + " | ".join(["---:"] * len(header_cells)) + " |"
    elif align == "center":
        separator = "| " + " | ".join([":---:"] * len(header_cells)) + " |"
    lines = ["| " + " | ".join(header_cells) + " |", separator] + body
    return "\n".join(lines)


def callout(kind: str, text: str) -> str:
    """Render a Boris callout. Kinds seen in the compiler docs: info, tip, warning."""
    return f'<Aside kind="{kind}">\n\n{text}\n\n</Aside>'


def deflist(items: Iterable[tuple[str, str]]) -> str:
    """Render a Markdown definition list (``Term\\n: Definition``)."""
    blocks = []
    for term, definition in items:
        definition = str(definition).replace("\n", "\n  ")
        blocks.append(f"{term}\n: {definition}")
    return "\n\n".join(blocks)


def footnote(label: str, text: str) -> str:
    return f"[^{label}]: {text}"


def task_list(items: Iterable[tuple[bool, str]]) -> str:
    """Render a task list; ``(done, text)`` pairs."""
    return "\n".join(("- [x] " if done else "- [ ] ") + text for done, text in items)


def wikilink(entity_id: str, label: Optional[str] = None) -> str:
    if label:
        return f"[[{entity_id}|{label}]]"
    return f"[[{entity_id}]]"


def mdlink(url: str, label: Optional[str] = None) -> str:
    """Plain external Markdown link (never a wiki-link)."""
    if label:
        return f"[{label}]({url})"
    return f"<{url}>"


def abbr(term: str, expansion: str) -> str:
    """Inline abbreviation markup (renders as a title attribute where supported)."""
    return f"<abbr title=\"{_escape_quotes(expansion)}\">{term}</abbr>"


def slugify(text: str) -> str:
    """Deterministic slug used for filenames and stable anchors."""
    text = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    return text or "page"

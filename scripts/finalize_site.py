#!/usr/bin/env python3
"""Add TED-owned static artifacts and canonical metadata to a Boris site."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
from xml.etree import ElementTree as ET


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.S)
FIELD_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
LOC_RE = re.compile(r"(<loc>)(.*?)(</loc>)", re.S)
SITE_NAME = "Thermal Extraction Devices"
class SiteFinalizationError(RuntimeError):
    """Raised when a required source, generated route, or mapping is invalid."""


@dataclass(frozen=True)
class Page:
    source: Path
    source_path: str
    entity_id: str
    title: str
    summary: str

    @property
    def output_path(self) -> str:
        return "index.html" if self.entity_id == "index" else f"{self.entity_id}.html"


def _frontmatter_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise SiteFinalizationError(
                f"cannot decode double-quoted Boris frontmatter scalar {value!r}"
            ) from exc
        if not isinstance(decoded, str):
            raise SiteFinalizationError("frontmatter scalar did not decode to text")
        return decoded
    return value


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = FIELD_RE.match(line)
        if field:
            fields[field.group(1)] = _frontmatter_scalar(field.group(2))
    return fields


def load_pages(content_root: Path, site_root: Path) -> tuple[list[Page], dict[str, Page]]:
    pages: list[Page] = []
    by_source: dict[str, Page] = {}
    page_ids: set[str] = set()

    for source in sorted(content_root.rglob("*.md")):
        relative = source.relative_to(content_root)
        if relative.parts[0] == "includes":
            continue
        fields = read_frontmatter(source)
        entity_id = fields.get("id")
        if not entity_id:
            raise SiteFinalizationError(f"{source}: published page has no frontmatter id")
        if entity_id in page_ids:
            raise SiteFinalizationError(f"duplicate frontmatter id {entity_id!r}")
        page_ids.add(entity_id)

        page = Page(
            source=source,
            source_path=(Path("content") / relative).as_posix(),
            entity_id=entity_id,
            title=fields.get("title") or entity_id,
            summary=fields.get("summary", ""),
        )
        output = site_root / page.output_path
        if not output.is_file():
            raise SiteFinalizationError(
                f"{source}: Boris output is missing for {entity_id!r}: {output}"
            )
        pages.append(page)
        by_source[page.source_path] = page

    if not pages:
        raise SiteFinalizationError(f"no pages found under {content_root}")
    return pages, by_source


def canonical_url(site_url: str, output_path: str) -> str:
    route = "/" if output_path == "index.html" else f"/{output_path[:-5]}"
    encoded = quote(route, safe="/-._~")
    return site_url.rstrip("/") + encoded


def add_head_metadata(path: Path, page: Page, canonical: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"</head\s*>", text, re.I):
        raise SiteFinalizationError(f"{path}: generated HTML has no closing </head>")

    if page.title.strip() == SITE_NAME:
        doubled_title = (
            f"<title>{html.escape(page.title)} · {html.escape(SITE_NAME)}</title>"
        )
        text = text.replace(
            doubled_title,
            f"<title>{html.escape(page.title)}</title>",
            1,
        )

    text = re.sub(
        r"<meta\s+name\s*=\s*(['\"])description\1[^>]*>\s*",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"<link\b(?=[^>]*\brel\s*=\s*(['\"])canonical\1)[^>]*>\s*",
        "",
        text,
        flags=re.I,
    )
    metadata = []
    if page.summary:
        metadata.append(
            f'<meta name="description" content="{html.escape(page.summary, quote=True)}">'
        )
    metadata.append(f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">')
    insertion = "\n".join(metadata) + "\n"
    text = re.sub(r"</head\s*>", insertion + "</head>", text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")


def add_canonical_link(path: Path, canonical: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"</head\s*>", text, re.I):
        raise SiteFinalizationError(f"{path}: generated HTML has no closing </head>")
    text = re.sub(
        r"<link\b(?=[^>]*\brel\s*=\s*(['\"])canonical\1)[^>]*>\s*",
        "",
        text,
        flags=re.I,
    )
    tag = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">\n'
    text = re.sub(r"</head\s*>", tag + "</head>", text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")


def _canonical_sitemap_url(value: str) -> str:
    parsed = urlsplit(html.unescape(value))
    path = parsed.path
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    elif path.endswith(".html"):
        path = path[:-5]
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def normalize_sitemap(site_root: Path) -> int:
    sitemap = site_root / "sitemap.xml"
    try:
        parsed = ET.parse(sitemap)
    except (OSError, ET.ParseError) as exc:
        raise SiteFinalizationError(f"cannot parse generated sitemap {sitemap}: {exc}") from exc

    locations = [
        element
        for element in parsed.getroot().iter()
        if element.tag.rsplit("}", 1)[-1] == "loc"
    ]
    if not locations:
        raise SiteFinalizationError(f"{sitemap}: no <loc> entries")

    rewritten: list[str] = []
    for element in locations:
        if not element.text:
            raise SiteFinalizationError(f"{sitemap}: empty <loc> entry")
        new_value = _canonical_sitemap_url(element.text)
        element.text = new_value
        rewritten.append(new_value)

    # Validate the transformed XML before preserving Boris's formatting with
    # a narrow <loc> replacement.
    ET.fromstring(ET.tostring(parsed.getroot(), encoding="unicode"))
    iterator = iter(rewritten)

    def replace_loc(match: re.Match[str]) -> str:
        return match.group(1) + html.escape(next(iterator), quote=False) + match.group(3)

    text = sitemap.read_text(encoding="utf-8")
    sitemap.write_text(LOC_RE.sub(replace_loc, text), encoding="utf-8")
    if ".html</loc>" in sitemap.read_text(encoding="utf-8"):
        raise SiteFinalizationError(f"{sitemap}: an advertised URL still ends in .html")
    return len(locations)


def git_renames(repo_root: Path) -> dict[str, set[str]]:
    shallow = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--is-shallow-repository"],
        capture_output=True,
        text=True,
        check=False,
    )
    if shallow.returncode != 0:
        raise SiteFinalizationError(f"{repo_root} is not a readable Git repository")
    if shallow.stdout.strip() == "true":
        raise SiteFinalizationError(
            "full Git history is required to generate legacy URL redirects"
        )

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "log",
            "--format=",
            "--find-renames",
            "--diff-filter=R",
            "--name-status",
            "HEAD",
            "--",
            "content",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SiteFinalizationError(f"cannot read Git rename history: {result.stderr.strip()}")

    renames: dict[str, set[str]] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) == 3 and fields[0].startswith("R"):
            old, new = fields[1:]
            if old.startswith("content/") and old.endswith(".md"):
                renames.setdefault(old, set()).add(new)
    return renames


def derive_redirects(content_root: Path, repo_root: Path) -> dict[str, str]:
    """Derive legacy source routes from current IDs and Git rename history."""
    pages: list[Page] = []
    by_source: dict[str, Page] = {}
    page_ids: set[str] = set()
    for source in sorted(content_root.rglob("*.md")):
        relative = source.relative_to(content_root)
        if relative.parts[0] == "includes":
            continue
        fields = read_frontmatter(source)
        entity_id = fields.get("id")
        if not entity_id:
            raise SiteFinalizationError(f"{source}: published page has no frontmatter id")
        if entity_id in page_ids:
            raise SiteFinalizationError(f"duplicate frontmatter id {entity_id!r}")
        page_ids.add(entity_id)
        page = Page(
            source,
            (Path("content") / relative).as_posix(),
            entity_id,
            fields.get("title") or entity_id,
            "",
        )
        pages.append(page)
        by_source[page.source_path] = page

    aliases: dict[str, str] = {}
    renames = git_renames(repo_root)
    current_source_paths = set(by_source)

    def add_alias(source_path: str, target_id: str) -> None:
        if not source_path.startswith("content/") or not source_path.endswith(".md"):
            return
        old_path = source_path[len("content/") : -len(".md")]
        target_path = "" if target_id == "index" else target_id
        if old_path == target_path:
            return
        # A live entity route wins over a historic alias. This prevents an
        # old canonical ID that has since been reused from shadowing its page.
        if old_path in page_ids:
            return
        previous = aliases.get(old_path)
        if previous is not None and previous != target_id:
            raise SiteFinalizationError(
                f"legacy path {old_path!r} maps to both {previous!r} and {target_id!r}"
            )
        aliases[old_path] = target_id

    for page in pages:
        source_stem = page.source_path[len("content/") : -len(".md")]
        target_stem = "" if page.entity_id == "index" else page.entity_id
        if source_stem != target_stem:
            add_alias(page.source_path, page.entity_id)

    for old, targets in renames.items():
        if old in current_source_paths:
            continue
        if len(targets) != 1:
            raise SiteFinalizationError(
                f"ambiguous Git rename history for {old!r}: {sorted(targets)!r}"
            )
        current = next(iter(targets))
        seen = {old}
        while current not in by_source and current in renames:
            if current in seen:
                raise SiteFinalizationError(f"Git rename cycle involving {current!r}")
            seen.add(current)
            next_targets = renames[current]
            if len(next_targets) != 1:
                raise SiteFinalizationError(
                    f"ambiguous Git rename history for {current!r}: {sorted(next_targets)!r}"
                )
            current = next(iter(next_targets))
        target_page = by_source.get(current)
        if target_page:
            add_alias(old, target_page.entity_id)
    return aliases


def write_redirect_manifest(content_root: Path, repo_root: Path, output: Path) -> int:
    redirects = derive_redirects(content_root.resolve(), repo_root.resolve())
    payload = {
        "version": 1,
        "source": "current content IDs and Git rename history",
        "redirects": dict(sorted(redirects.items())),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(redirects)


def read_redirect_manifest(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SiteFinalizationError(f"cannot read redirect manifest {path}: {exc}") from exc
    if data.get("version") != 1 or not isinstance(data.get("redirects"), dict):
        raise SiteFinalizationError(f"{path}: unsupported legacy redirect manifest schema")
    redirects = data["redirects"]
    if not all(
        isinstance(source, str)
        and source
        and isinstance(target, str)
        and target
        for source, target in redirects.items()
    ):
        raise SiteFinalizationError(f"{path}: redirect entries must map non-empty paths to IDs")
    return redirects


def generate_redirects(
    redirects: dict[str, str],
    site_root: Path,
    page_ids: set[str],
) -> int:
    lines: list[str] = []
    for old_path, target_id in sorted(redirects.items()):
        if (
            old_path.startswith("/")
            or old_path.endswith(".html")
            or "\\" in old_path
            or ".." in Path(old_path).parts
            or old_path in ("", ".")
        ):
            raise SiteFinalizationError(f"invalid legacy path {old_path!r}")
        if target_id not in page_ids:
            raise SiteFinalizationError(
                f"redirect target is not a current Boris entity: {target_id!r}"
            )
        # A live canonical path takes precedence over any older alias that
        # happens to have been reused as another page ID.
        if old_path in page_ids and old_path != target_id:
            continue
        target = "" if target_id == "index" else "/" + quote(target_id, safe="/-._~")
        if target_id != "index" and not (site_root / f"{target_id}.html").is_file():
            raise SiteFinalizationError(
                f"redirect target does not exist: {target_id!r}"
            )
        source = "/" + quote(old_path, safe="/-._~")
        lines.append(f"{source}.html {target or '/'} 301")
        lines.append(f"{source} {target or '/'} 301")

    (site_root / "_redirects").write_text(
        "".join(f"{line}\n" for line in lines),
        encoding="utf-8",
    )
    return len(lines)


def finalize_site(
    content_root: Path,
    theme_root: Path,
    site_root: Path,
    site_url: str,
    repo_root: Path,
) -> dict[str, int]:
    content_root = content_root.resolve()
    theme_root = theme_root.resolve()
    site_root = site_root.resolve()
    repo_root = repo_root.resolve()
    site_root.mkdir(parents=True, exist_ok=True)

    not_found = theme_root / "404.html"
    if not_found.is_file():
        (site_root / "404.html").write_bytes(not_found.read_bytes())
    else:
        raise SiteFinalizationError(f"missing themed not-found page: {not_found}")

    sitemap_count = normalize_sitemap(site_root)
    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {site_url.rstrip('/')}/sitemap.xml\n"
    )
    (site_root / "robots.txt").write_text(robots, encoding="utf-8")

    pages, _ = load_pages(content_root, site_root)
    page_ids = {page.entity_id for page in pages}
    descriptions = 0
    content_outputs: set[Path] = set()
    for page in pages:
        output = site_root / page.output_path
        content_outputs.add(output.resolve())
        add_head_metadata(output, page, canonical_url(site_url, page.output_path))
        descriptions += bool(page.summary)

    # Crosslink-generated index pages are published HTML routes too, but have
    # no authored frontmatter summary. Give them canonical URLs without
    # manufacturing descriptions. Exclude the not-found document and Boris's
    # private proof report, neither of which is a canonical content route.
    for output in sorted(site_root.rglob("*.html")):
        relative = output.relative_to(site_root)
        if output.resolve() in content_outputs or relative.as_posix() == "404.html":
            continue
        if relative.parts[0] == "_boris":
            continue
        route = relative.as_posix()
        if route == "index.html":
            canonical = canonical_url(site_url, route)
        else:
            canonical = site_url.rstrip("/") + "/" + quote(
                route[:-5],
                safe="/-._~",
            )
        add_canonical_link(output, canonical)

    redirects = read_redirect_manifest(repo_root / "metadata" / "legacy-paths.json")
    for page in pages:
        current_path = page.source_path[len("content/") : -len(".md")]
        canonical_path = "" if page.entity_id == "index" else page.entity_id
        if (
            current_path != canonical_path
            and current_path != "index"
            and redirects.get(current_path) != page.entity_id
        ):
            raise SiteFinalizationError(
                "metadata/legacy-paths.json is missing current source path "
                f"{current_path!r}; regenerate it from Git history"
            )
    redirect_count = generate_redirects(redirects, site_root, page_ids)
    return {
        "pages": len(pages),
        "descriptions": descriptions,
        "sitemap_urls": sitemap_count,
        "redirect_rules": redirect_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--theme", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("--git-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        counts = finalize_site(
            args.content,
            args.theme,
            args.output,
            args.site_url,
            args.git_root,
        )
    except SiteFinalizationError as exc:
        print(f"finalize_site: {exc}", file=sys.stderr)
        return 1
    print(
        "finalize_site: "
        f"{counts['pages']} pages, {counts['descriptions']} descriptions, "
        f"{counts['sitemap_urls']} sitemap URLs, "
        f"{counts['redirect_rules']} redirect rules"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

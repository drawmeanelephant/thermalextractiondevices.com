"""Safe, deterministic resolution and auditing of TED include markers.

TED content uses Boris include markers such as
``{{include includes/manufacturer-claim-note.md}}``. Boris intentionally keeps
those markers in its machine exports, so RAG consumers need a derived export
that expands the bodies without changing the source tree or the raw Boris
working export.

This module owns only the include boundary. It accepts include files below the
configured ``content/includes`` directory, rejects traversal and symlink
escapes, and fails closed on missing, malformed, or cyclic includes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
from typing import Iterator


_INCLUDE_START_RE = re.compile(r"\{\{\s*include\b")
_INCLUDE_RE = re.compile(r"\{\{\s*include\s+([^{}]*?)\s*\}\}")


@dataclass(frozen=True)
class IncludeMarker:
    """One include-like marker found in a UTF-8 text document."""

    start: int
    end: int
    line: int
    column: int
    raw: str
    reference: str | None
    error: str | None


@dataclass(frozen=True)
class IncludeIssue:
    """A deterministic, user-facing include audit finding."""

    source: str
    line: int
    column: int
    marker: str
    message: str

    def sort_key(self) -> tuple[str, int, int, str, str]:
        return (self.source, self.line, self.column, self.marker, self.message)


@dataclass(frozen=True)
class IncludeAudit:
    """Summary of an include scan."""

    files_scanned: int
    reference_count: int
    unique_references: tuple[str, ...]
    issues: tuple[IncludeIssue, ...]


class IncludeResolutionError(ValueError):
    """Raised when a marker cannot be safely expanded."""


def iter_include_markers(text: str) -> Iterator[IncludeMarker]:
    """Yield include-like markers in source order.

    The parser intentionally notices malformed and unterminated markers too;
    silently leaving a marker in a supposedly resolved export is unsafe.
    """

    for start_match in _INCLUDE_START_RE.finditer(text):
        start = start_match.start()
        close = text.find("}}", start + 2)
        end = len(text) if close < 0 else close + 2
        raw = text[start:end]
        line = text.count("\n", 0, start) + 1
        line_start = text.rfind("\n", 0, start) + 1
        column = start - line_start + 1
        match = _INCLUDE_RE.fullmatch(raw)
        if match is None:
            yield IncludeMarker(
                start=start,
                end=end,
                line=line,
                column=column,
                raw=raw,
                reference=None,
                error="malformed or unterminated include marker",
            )
            continue
        reference = match.group(1).strip()
        if not reference:
            yield IncludeMarker(
                start=start,
                end=end,
                line=line,
                column=column,
                raw=raw,
                reference=None,
                error="include path is empty",
            )
            continue
        yield IncludeMarker(
            start=start,
            end=end,
            line=line,
            column=column,
            raw=raw,
            reference=reference,
            error=None,
        )


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _relative_label(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _marker_label(marker: IncludeMarker) -> str:
    return marker.raw.replace("\n", "\\n")


def _target_for_reference(
    reference: str,
    *,
    include_root: Path,
    include_prefix: str = "includes",
) -> tuple[Path | None, str | None]:
    """Return a safe include target or a stable validation error."""

    if "\\" in reference:
        return None, "include paths must use POSIX separators"
    path = PurePosixPath(reference)
    prefix_path = PurePosixPath(include_prefix)
    prefix_parts = prefix_path.parts
    if path.is_absolute():
        return None, "include path must be relative"
    if not prefix_parts or path.parts[: len(prefix_parts)] != prefix_parts:
        return None, f"include path must start with {prefix_path.as_posix()}/"
    if any(part in ("", ".", "..") for part in path.parts):
        return None, "include path contains a disallowed path segment"
    if len(path.parts) <= len(prefix_parts):
        return None, "include path must name a Markdown file"
    if path.suffix.lower() != ".md":
        return None, "include path must name a Markdown file"

    relative = Path(*path.parts[len(prefix_parts) :])
    candidate = (include_root / relative).resolve(strict=False)
    if not _is_within(candidate, include_root):
        return None, "include path escapes the include directory"
    if not candidate.is_file():
        return None, f"include file does not exist: {path.as_posix()}"
    return candidate, None


def _read_utf8(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def _issue_for_marker(source: str, marker: IncludeMarker, message: str) -> IncludeIssue:
    return IncludeIssue(
        source=source,
        line=marker.line,
        column=marker.column,
        marker=_marker_label(marker),
        message=message,
    )


def _scan_files(root: Path) -> list[Path]:
    return sorted(
        (path for path in root.rglob("*.md") if path.is_file()),
        key=lambda path: _relative_label(path, root),
    )


def audit_content_includes(
    content_root: Path,
    *,
    include_dir: str = "includes",
) -> IncludeAudit:
    """Validate every include marker in the content tree.

    The scan includes the include directory itself so nested references and
    cycles are checked even when a fragment is not currently used by a page.
    """

    root = content_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"content root is not a directory: {content_root}")
    include_root = (root / include_dir).resolve(strict=False)
    files = _scan_files(root)
    issues: list[IncludeIssue] = []
    references: set[str] = set()
    reference_count = 0
    include_graph: dict[Path, list[tuple[Path, IncludeMarker, str]]] = {}

    for path in files:
        source = _relative_label(path, root)
        try:
            text = _read_utf8(path)
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                IncludeIssue(
                    source=source,
                    line=1,
                    column=1,
                    marker="",
                    message=f"cannot read UTF-8 content: {exc}",
                )
            )
            continue

        path_is_include = _is_within(path.resolve(), include_root)
        for marker in iter_include_markers(text):
            reference_count += 1
            if marker.error is not None:
                issues.append(_issue_for_marker(source, marker, marker.error))
                continue
            assert marker.reference is not None
            target, error = _target_for_reference(
                marker.reference,
                include_root=include_root,
                include_prefix=include_dir.replace("\\", "/").strip("/"),
            )
            if error is not None:
                issues.append(_issue_for_marker(source, marker, error))
                continue
            assert target is not None
            references.add(PurePosixPath(marker.reference).as_posix())
            if path_is_include:
                include_graph.setdefault(path.resolve(), []).append(
                    (target, marker, source)
                )

    # Detect include cycles with a stable depth-first traversal. Missing and
    # malformed references were already reported above, so only safe targets
    # enter this graph.
    state: dict[Path, int] = {}
    stack: list[Path] = []
    reported_cycles: set[tuple[str, ...]] = set()

    def visit(node: Path) -> None:
        state[node] = 1
        stack.append(node)
        edges = sorted(
            include_graph.get(node, []),
            key=lambda edge: (
                edge[0].relative_to(include_root).as_posix(),
                edge[1].line,
                edge[1].column,
            ),
        )
        for target, marker, source in edges:
            if state.get(target, 0) == 1:
                cycle_start = stack.index(target)
                cycle_nodes = stack[cycle_start:] + [target]
                cycle_labels = tuple(
                    node.relative_to(include_root).as_posix()
                    for node in cycle_nodes
                )
                if cycle_labels not in reported_cycles:
                    reported_cycles.add(cycle_labels)
                    issues.append(
                        _issue_for_marker(
                            source,
                            marker,
                            "include cycle: " + " -> ".join(cycle_labels),
                        )
                    )
            elif state.get(target, 0) == 0:
                visit(target)
        stack.pop()
        state[node] = 2

    for node in sorted(include_graph, key=lambda path: path.as_posix()):
        if state.get(node, 0) == 0:
            visit(node)

    return IncludeAudit(
        files_scanned=len(files),
        reference_count=reference_count,
        unique_references=tuple(sorted(references)),
        issues=tuple(sorted(issues, key=IncludeIssue.sort_key)),
    )


def audit_export_includes(export_root: Path) -> IncludeAudit:
    """Fail if a derived RAG export still contains an include marker."""

    root = export_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"RAG export is not a directory: {export_root}")
    files = _scan_files(root)
    issues: list[IncludeIssue] = []
    reference_count = 0
    references: set[str] = set()
    for path in files:
        source = _relative_label(path, root)
        try:
            text = _read_utf8(path)
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                IncludeIssue(
                    source=source,
                    line=1,
                    column=1,
                    marker="",
                    message=f"cannot read UTF-8 export: {exc}",
                )
            )
            continue
        for marker in iter_include_markers(text):
            reference_count += 1
            if marker.reference is not None:
                references.add(marker.reference)
            issues.append(
                _issue_for_marker(
                    source,
                    marker,
                    "unresolved include marker remains in RAG export",
                )
            )
    return IncludeAudit(
        files_scanned=len(files),
        reference_count=reference_count,
        unique_references=tuple(sorted(references)),
        issues=tuple(sorted(issues, key=IncludeIssue.sort_key)),
    )


class IncludeResolver:
    """Resolve include markers against one include root."""

    def __init__(self, include_root: Path, *, include_prefix: str = "includes") -> None:
        self.include_root = include_root.resolve(strict=False)
        self.include_prefix = include_prefix.replace("\\", "/").strip("/")
        self._cache: dict[Path, str] = {}

    def resolve_text(self, text: str, *, source: str = "<text>") -> str:
        """Expand every include marker in ``text`` or raise safely."""

        return self._resolve_text(text, source=source, stack=())

    def _resolve_text(self, text: str, *, source: str, stack: tuple[Path, ...]) -> str:
        markers = list(iter_include_markers(text))
        if not markers:
            return text
        pieces: list[str] = []
        cursor = 0
        for marker in markers:
            if marker.error is not None:
                raise IncludeResolutionError(
                    f"{source}:{marker.line}:{marker.column}: {marker.error}"
                )
            assert marker.reference is not None
            target, error = _target_for_reference(
                marker.reference,
                include_root=self.include_root,
                include_prefix=self.include_prefix,
            )
            if error is not None:
                raise IncludeResolutionError(
                    f"{source}:{marker.line}:{marker.column}: {error}"
                )
            assert target is not None
            if target in stack:
                cycle_start = stack.index(target)
                cycle = stack[cycle_start:] + (target,)
                labels = [path.relative_to(self.include_root).as_posix() for path in cycle]
                raise IncludeResolutionError(
                    f"{source}:{marker.line}:{marker.column}: include cycle: "
                    + " -> ".join(labels)
                )
            pieces.append(text[cursor : marker.start])
            pieces.append(self._resolve_file(target, stack=stack + (target,)))
            cursor = marker.end
        pieces.append(text[cursor:])
        return "".join(pieces)

    def _resolve_file(self, target: Path, *, stack: tuple[Path, ...]) -> str:
        if target in self._cache:
            return self._cache[target]
        try:
            raw = _read_utf8(target)
        except (OSError, UnicodeDecodeError) as exc:
            raise IncludeResolutionError(
                f"{target.relative_to(self.include_root).as_posix()}: "
                f"cannot read UTF-8 include: {exc}"
            ) from exc
        resolved = self._resolve_text(
            raw,
            source=target.relative_to(self.include_root).as_posix(),
            stack=stack,
        )
        self._cache[target] = resolved
        return resolved


def format_include_issues(issues: tuple[IncludeIssue, ...] | list[IncludeIssue]) -> str:
    """Format findings in their already deterministic order."""

    lines: list[str] = []
    for issue in sorted(issues, key=IncludeIssue.sort_key):
        location = f"{issue.source}:{issue.line}:{issue.column}"
        marker = f" [{issue.marker}]" if issue.marker else ""
        lines.append(f"{location}: {issue.message}{marker}")
    return "\n".join(lines)

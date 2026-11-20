"""CommonMark structure and explicit managed regions, with source line locations."""

import re
from dataclasses import dataclass

from markdown_it import MarkdownIt

PARSER = MarkdownIt("commonmark")
BEGIN = "<!-- readme-standards:begin {name} -->"
END = "<!-- readme-standards:end {name} -->"


@dataclass(frozen=True)
class Heading:
    title: str
    level: int
    line: int
    end_line: int
    parent: str | None
    body: str


def parse(text: str) -> tuple[list[Heading], list[int]]:
    tokens = PARSER.parse(text)
    lines = text.splitlines(keepends=True)
    raw = []
    separators = []
    stack = []
    for index, token in enumerate(tokens):
        if token.type == "hr" and token.level == 0:
            separators.append(token.map[0] + 1)
        if token.type != "heading_open":
            continue
        level = int(token.tag[1])
        inline = tokens[index + 1]
        title = "".join(
            child.content
            if child.type in {"text", "code_inline", "image"}
            else " "
            if child.type in {"softbreak", "hardbreak"}
            else ""
            for child in inline.children or []
        )
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        raw.append((title, level, token.map[0] + 1, token.map[1], parent))
        stack.append((level, title))
    headings = []
    for i, (title, level, line, end, parent) in enumerate(raw):
        stop = raw[i + 1][2] - 1 if i + 1 < len(raw) else len(lines)
        headings.append(Heading(title, level, line, end, parent, "".join(lines[end:stop])))
    return headings, separators


def block(name: str, content: str) -> str:
    return f"{BEGIN.format(name=name)}\n{content.rstrip()}\n{END.format(name=name)}"


def visible(text: str) -> str:
    """Ignore comments and standalone separators when checking authored presence."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*(?:---|\*\*\*|___)\s*$", "", text).strip()


def region_errors(text: str) -> list[str]:
    """Reject malformed, nested, duplicated, or unmatched managed-region markers."""
    open_name = None
    seen = set()
    errors = []
    tokens = PARSER.parse(text)
    markers = re.compile(r"<!-- readme-standards:(begin|end) ([a-z0-9_.-]+) -->")
    for token in tokens:
        if token.type != "html_block":
            continue
        for match in markers.finditer(token.content):
            operation, name = match.groups()
            if operation == "begin":
                if open_name or name in seen:
                    errors.append(f"nested or duplicate region: {name}")
                seen.add(name)
                open_name = name
            elif open_name != name:
                errors.append(f"unmatched region end: {name}")
            else:
                open_name = None
    if open_name:
        errors.append(f"unclosed region: {open_name}")
    return errors

"""Read-only diagnostics for heading structure, authored presence, and derived facts."""

import ast
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import ConfigurationError, Package, load_package
from .document import PARSER, block, parse, visible
from .policy import SECTIONS, outline
from .render import SECTION_REGIONS, fragments, region_spans


@dataclass(frozen=True)
class Diagnostic:
    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.message}"

    def as_dict(self) -> dict:
        return asdict(self)


def check_package(root: Path) -> list[Diagnostic]:
    try:
        package = load_package(root)
    except ConfigurationError as error:
        return [Diagnostic(str(root / "pyproject.toml"), 1, "config", str(error))]
    return check(package)


def check(package: Package) -> list[Diagnostic]:
    path = package.readme
    issues = []

    def fail(rule: str, message: str, line: int = 1) -> None:
        issues.append(Diagnostic(str(path), line, rule, message))

    if not path.is_file():
        fail("readme.missing", "required README does not exist; run scaffold")
        return issues
    text = path.read_text("utf-8-sig")
    headings, separators = parse(text)
    if headings and "".join(text.splitlines(keepends=True)[: headings[0].line - 1]).strip():
        fail("heading.preamble", "the package-name H1 must be the first document element")
    expected = outline(package.name)
    by_title = {row["title"]: row for row in expected[1:]}
    order = {row["id"]: i for i, row in enumerate(expected)}

    def row_for(heading):
        if heading.level == 1 and heading.title == package.name:
            return expected[0]
        return by_title.get(heading.title)

    counts = Counter(row["id"] for h in headings if (row := row_for(h)))
    for row in expected:
        if not counts[row["id"]]:
            fail(
                "heading.missing",
                f"missing H{row['level']} {row['title']!r} under {row['parent']!r}",
            )
    previous = -1
    for heading in headings:
        row = row_for(heading)
        if row is None:
            fail("heading.extra", f"unexpected heading {heading.title!r}", heading.line)
            continue
        if counts[row["id"]] > 1:
            fail("heading.duplicate", f"duplicate heading {heading.title!r}", heading.line)
        if row["level"] != heading.level:
            fail("heading.level", f"{heading.title!r} must be H{row['level']}", heading.line)
        parent = next((e["title"] for e in expected if e["id"] == row["parent"]), None)
        if heading.parent != parent:
            fail("heading.parent", f"{heading.title!r} must be under {parent!r}", heading.line)
        rank = order[row["id"]]
        if rank < previous:
            fail("heading.order", f"{heading.title!r} is out of policy order", heading.line)
        previous = max(previous, rank)
    for i, heading in enumerate(headings):
        if heading.level != 2 or heading.title not in by_title:
            continue
        lower = headings[i - 1].end_line if i else 0
        between = [line for line in separators if lower < line < heading.line]
        if len(between) != 1:
            fail(
                "separator.missing",
                f"exactly one horizontal rule required before {heading.title!r}",
                heading.line,
            )
    expected_separator_count = sum(row["level"] == 2 for row in expected)
    if len(separators) != expected_separator_count:
        fail(
            "separator.count",
            f"expected {expected_separator_count} top-level horizontal rules; found {len(separators)}",
        )
    lines = text.splitlines()
    for line in separators:
        if lines[line - 1] != "---":
            fail("separator.style", "group separator must be exactly ---", line)
    document_tokens = PARSER.parse(text)
    flattened_tokens = []
    for token in document_tokens:
        flattened_tokens.append(token)
        flattened_tokens.extend(token.children or [])
    for token in flattened_tokens:
        if token.type == "heading_open" and token.level != 0:
            fail(
                "heading.nested",
                "headings must not be inside lists or blockquotes",
                token.map[0] + 1,
            )
        if token.type in {"html_block", "html_inline"}:
            html_without_comments = re.sub(r"<!--.*?-->", "", token.content, flags=re.S)
            if re.search(r"<h[1-6](?:\s|>)", html_without_comments, re.I):
                fail(
                    "heading.html",
                    "use policy Markdown headings, not HTML headings",
                    (token.map or [0])[0] + 1,
                )
    try:
        data = fragments(package)
        spans = region_spans(text)
        locations = {name: (start, end) for name, start, end in spans}
        for name, value in data.items():
            if name not in locations:
                fail("generated.missing", f"missing managed region {name!r}; run repair")
                continue
            start, end = locations[name]
            line = text.count("\n", 0, start) + 1
            if text[start:end] != block(name, value):
                fail(
                    "generated.stale",
                    f"region {name!r} differs from declared inputs; run render",
                    line,
                )
            owner = (
                "package"
                if name == "branding"
                else next(key for key, region in SECTION_REGIONS.items() if region == name)
            )
            owner_title = next(row["title"] for row in expected if row["id"] == owner)
            actual_heading = next((h for h in reversed(headings) if h.line <= line), None)
            actual_row = row_for(actual_heading) if actual_heading else None
            if actual_row is None or actual_row["id"] != owner:
                fail("generated.location", f"region {name!r} belongs under {owner_title!r}", line)
        for name in locations.keys() - data.keys():
            fail("generated.unknown", f"unknown managed region {name!r}")
        if headings and "branding" in locations:
            start, end = locations["branding"]
            title_end = sum(
                len(line) for line in text.splitlines(keepends=True)[: headings[0].end_line]
            )
            if text[title_end:start].strip():
                fail(
                    "branding.position",
                    "branding must appear immediately after the package-name H1",
                )
            if len(headings) > 1:
                next_start = sum(
                    len(line) for line in text.splitlines(keepends=True)[: headings[1].line - 1]
                )
                if visible(text[end:next_start]):
                    fail(
                        "branding.preamble",
                        "put authored introduction under Overview, not before it",
                    )
    except (ConfigurationError, OSError, ValueError) as error:
        fail("generated.invalid", str(error))
    authored = {s.title: s for s in SECTIONS if s.content == "authored"}
    seen_bodies = {}
    for heading in headings:
        if heading.level == 1 or heading.title not in authored:
            continue
        body = visible(heading.body)
        prose = " ".join(t.content for t in PARSER.parse(body) if t.type == "inline")
        if not prose.strip():
            fail(
                "content.missing",
                f"{heading.title!r} needs authored explanation or an explicit applicability statement",
                heading.line,
            )
        if (
            re.search(r"\b(?:TODO|TBD|FIXME)\b|AUTHOR REQUIRED|\{\{[^}]+\}\}", prose, re.I)
            or "AUTHOR REQUIRED" in heading.body
        ):
            fail(
                "content.placeholder",
                f"unresolved authoring placeholder in {heading.title!r}",
                heading.line,
            )
        if re.fullmatch(r"(?:N/?A|none|not applicable)[.!\s]*", prose, re.I):
            fail("content.applicability", "explain why this section does not apply", heading.line)
        normalized = re.sub(r"\s+", " ", prose).strip().casefold()
        if len(normalized) >= 80:
            if normalized in seen_bodies:
                fail(
                    "content.duplicate",
                    f"identical authored prose also appears in {seen_bodies[normalized]!r}",
                    heading.line,
                )
            seen_bodies[normalized] = heading.title
    for key, example in package.settings["examples"].items():
        for field in ("source", "expected_stdout", "test"):
            try:
                source = package.local(example[field])
                if not source.is_file() or not source.read_text("utf-8").strip():
                    fail(
                        "example.missing",
                        f"{key}.{field} must reference a nonempty file: {example[field]}",
                    )
            except (OSError, ConfigurationError) as error:
                fail("example.invalid", str(error))
        if example.get("language", "python") == "python":
            try:
                ast.parse(package.local(example["source"]).read_text("utf-8"))
            except (SyntaxError, OSError, ConfigurationError) as error:
                fail("example.syntax", f"{key}: {error}")
    for field in ("license_file", "notice_file"):
        if field in package.settings:
            source = package.local(package.settings[field])
            if not source.is_file() or not source.read_bytes().strip():
                fail("legal.missing", f"{field} must reference a nonempty file")
    for key, status in package.settings["statuses"].items():
        if "evidence_file" in status:
            try:
                evidence = json.loads(package.local(status["evidence_file"]).read_text("utf-8"))
                if (
                    not isinstance(evidence, dict)
                    or evidence.get("package") != package.name
                    or evidence.get("version") != package.project["version"]
                    or evidence.get("policy") != package.settings["policy"]
                    or evidence.get("status") != "passed"
                    or not evidence.get("checks")
                ):
                    fail(
                        "evidence.mismatch",
                        f"{key}: evidence must identify this package, version, policy, passing status, and checks",
                    )
            except (OSError, ValueError, ConfigurationError) as error:
                fail("evidence.invalid", f"{key}: {error}")
    return issues

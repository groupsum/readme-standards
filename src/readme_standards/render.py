"""Deterministic fragments and conservative, explicit document repair."""

import difflib
import html
import re
from urllib.parse import quote

from .config import ConfigurationError, Package
from .document import PARSER, block, parse, region_errors
from .policy import SECTIONS

REGISTRY_ORDER = ("pypi", "crates", "npm", "ghcr")
LABEL_COLOR = "1E293B"
BLUE = "1D4ED8"
CYAN = "0E7490"
TEAL = "0F766E"
VIOLET = "6D28D9"
INDIGO = "4338CA"
PLUM = "86198F"
GREEN = "166534"
AMBER = "92400E"
RED = "991B1B"
SLATE = "475569"

REGISTRY_COLORS = {"pypi": BLUE, "crates": "9A3412", "npm": "B91C1C", "ghcr": VIOLET}
REGISTRY_DOWNLOADS = {
    "pypi": ("Monthly PyPI downloads", "pypi/dm"),
    "crates": ("Total crates.io downloads", "crates/d"),
    "npm": ("Monthly npm downloads", "npm/dm"),
}
LIFECYCLE_COLORS = {
    "active": GREEN,
    "experimental": VIOLET,
    "planning": BLUE,
    "deprecated": AMBER,
    "retired": RED,
}
CERTIFICATION_COLORS = {
    "not certified": AMBER,
    "not applicable": SLATE,
    "partial": BLUE,
    "verified": GREEN,
}

NAVIGATION = (
    ("Overview", "overview"),
    ("Installation", "installation"),
    ("Quick Start", "quick-start"),
    ("Usage", "usage"),
    ("API", "public-api-and-import-surfaces"),
    ("Contributing", "contributing"),
    ("Governance", "governance"),
    ("License", "license"),
)


def badge(label: str, value: str, url: str, image: str) -> str:
    return (
        f'<a href="{html.escape(url, quote=True)}"><img '
        f'alt="{html.escape(label + ": " + value, quote=True)}" '
        f'src="{html.escape(image, quote=True)}"></a>'
    )


def shield_badge(label: str, value: str, url: str, color: str, *, path: str | None = None) -> str:
    if path is None:
        path = f"static/v1?label={quote(label, safe='')}&message={quote(value, safe='')}"
        separator = "&"
    else:
        separator = "?"
    image = f"https://img.shields.io/{path}{separator}labelColor={LABEL_COLOR}&color={color}"
    return badge(label, value, url, image)


def registry_url(registry: str, name: str) -> str:
    return {
        "pypi": f"https://pypi.org/project/{quote(name, safe='')}/",
        "crates": f"https://crates.io/crates/{quote(name, safe='')}",
        "npm": f"https://www.npmjs.com/package/{quote(name, safe='@/')}",
        "ghcr": f"https://ghcr.io/{quote(name, safe='/')}",
    }[registry]


def branding(package: Package) -> str:
    settings, project, brand = package.settings, package.project, package.brand
    facts = []
    metrics = []
    for registry in REGISTRY_ORDER:
        distribution = settings["distributions"].get(registry)
        if not distribution:
            continue
        name = distribution["name"]
        url = registry_url(registry, name)
        published = distribution["published"]
        path = None
        if published and registry != "ghcr":
            prefix = {"pypi": "pypi/v", "crates": "crates/v", "npm": "npm/v"}[registry]
            path = f"{prefix}/{quote(name, safe='')}"
        facts.append(
            shield_badge(
                registry,
                name if published else f"{name} unpublished",
                url,
                REGISTRY_COLORS[registry] if published else AMBER,
                path=path,
            )
        )
        if published:
            custom = distribution.get("downloads_image")
            if custom:
                metrics.append(
                    badge(
                        distribution["downloads_label"], name, distribution["downloads_url"], custom
                    )
                )
            elif registry in REGISTRY_DOWNLOADS:
                label, prefix = REGISTRY_DOWNLOADS[registry]
                metrics.append(
                    shield_badge(label, name, url, CYAN, path=f"{prefix}/{quote(name, safe='')}")
                )
            else:
                metrics.append(
                    shield_badge("GHCR pull metrics", f"{name}: unavailable", url, SLATE)
                )
        else:
            metrics.append(
                shield_badge(f"{registry} downloads", f"{name}: unpublished", url, AMBER)
            )
    manifest_url = package.source_url("pyproject.toml")
    python = project.get("requires-python")
    facts.extend(
        [
            shield_badge("Source version", project["version"], manifest_url, INDIGO),
            shield_badge(
                "Python",
                python if python is not None else "not declared",
                manifest_url,
                TEAL if python is not None else SLATE,
            ),
            shield_badge("Layer", settings["layer"], manifest_url, VIOLET),
            shield_badge(
                "Lifecycle",
                settings["lifecycle"],
                package.source_url("README.md") + "#lifecycle-and-migration",
                LIFECYCLE_COLORS[settings["lifecycle"]],
            ),
            shield_badge(
                "License", project["license"], package.source_url(settings["license_file"]), PLUM
            ),
            shield_badge(
                "Notice",
                "attribution" if "notice_file" in settings else "not required",
                package.source_url(settings["notice_file"])
                if "notice_file" in settings
                else package.source_url(settings.get("readme", "README.md")) + "#notices",
                PLUM if "notice_file" in settings else SLATE,
            ),
        ]
    )
    readme_url = package.source_url(settings.get("readme", "README.md"))
    # No branch/version in the counter identity: package traffic survives releases.
    identity = (
        settings["repository"].removeprefix("https://")
        + "/"
        + "/".join(
            p
            for p in (settings["package_path"].strip("/"), settings.get("readme", "README.md"))
            if p and p != "."
        )
    )
    metrics.append(
        badge(
            "README hits",
            package.name,
            readme_url,
            f"https://hits.sh/{quote(identity, safe='/')}.svg?label=README%20hits"
            f"&labelColor={LABEL_COLOR}&color={CYAN}",
        )
    )
    statuses = settings["statuses"]
    certification_color = CERTIFICATION_COLORS[statuses["certification"]["label"]]
    evidence = [
        shield_badge(label, statuses[key]["label"], statuses[key]["url"], color)
        for key, label, color in (
            ("readme", "README standards", BLUE),
            ("tests", "Tests", TEAL),
            ("certification", "Certification", certification_color),
            ("governance", "Governance", INDIGO),
            ("evidence", "Evidence", VIOLET),
        )
    ]
    rows = [
        f'<p align="center"><a href="{html.escape(brand["homepage"], quote=True)}">'
        f'<img src="{html.escape(brand["logo_url"], quote=True)}" '
        f'alt="{html.escape(brand["logo_alt"], quote=True)}" width="300"></a></p>',
        f'<p align="center"><strong>{html.escape(package.name)}</strong></p>',
        f'<p align="center">{html.escape(project.get("description", ""))}</p>',
    ]
    rows.extend(
        '<p align="center">\n' + "\n".join(row) + "\n</p>" for row in (facts, metrics, evidence)
    )
    rows.append(
        '<p align="center">'
        + " · ".join(f'<a href="#{anchor}">{label}</a>' for label, anchor in NAVIGATION)
        + "</p>"
    )
    return "\n".join(rows)


def fenced(text: str, language: str) -> str:
    runs = [len(m.group()) for m in re.finditer(r"`+", text)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return f"{fence}{language}\n{text.rstrip()}\n{fence}"


def fragments(package: Package) -> dict[str, str]:
    data = {"branding": branding(package)}
    distribution = package.settings["distributions"].get("pypi")
    name = distribution["name"] if distribution else None
    for installer, command in (
        ("uv", "uv add"),
        ("pip", "python -m pip install"),
        ("poetry", "poetry add"),
    ):
        if not package.installable:
            content = (
                "This is a source-only workspace or test harness, not an installable distribution. "
                + (
                    "From its checkout, synchronize the declared environment:\n\n"
                    + fenced("uv sync", "bash")
                    if installer == "uv"
                    else "Use the uv checkout workflow above; this installer does not install the harness itself."
                )
            )
        elif name:
            if distribution["published"]:
                content = fenced(f"{command} {name}", "bash")
            else:
                source_command = {
                    "uv": "uv pip install .",
                    "pip": "python -m pip install .",
                    "poetry": f"poetry add /path/to/{name}",
                }[installer]
                instruction = (
                    "From a separate Poetry project, replace the path with your checkout"
                    if installer == "poetry"
                    else "From the source checkout"
                )
                content = f"`{name}` is not declared published. {instruction}:\n\n" + fenced(
                    source_command, "bash"
                )
        else:
            content = (
                "This installer manages Python distributions. This package declares no "
                "PyPI distribution; use the distribution links in Project Links."
            )
        data[f"installation.{installer}"] = content
    for key, section in (("quick_start", "example.quick-start"), ("usage", "example.usage")):
        example = package.settings["examples"][key]
        path = package.local(example["source"])
        if not path.is_file():
            raise ConfigurationError(f"missing example source: {path}")
        data[section] = (
            f"Source: [{example['source']}]({package.source_url(example['source'])}).\n\n"
            + fenced(path.read_text("utf-8"), example.get("language", "python"))
        )
    points = []
    for group, entries in (
        ("console_scripts", package.project.get("scripts", {})),
        ("gui_scripts", package.project.get("gui-scripts", {})),
        *sorted(package.project.get("entry-points", {}).items()),
    ):
        for name, target in sorted(entries.items()):
            points.append(f"- `{group}` → `{name}` → `{target}`")
    data["entry-points"] = "\n".join(points) or (
        "This package declares no command-line, GUI, or plugin entry points in its manifest."
    )
    links = [f"- [{name}]({url})" for name, url in sorted(package.project.get("urls", {}).items())]
    links += [
        f"- [{registry}: {d['name']}]({registry_url(registry, d['name'])})"
        for registry in REGISTRY_ORDER
        if (d := package.settings["distributions"].get(registry))
    ]
    data["project-links"] = "\n".join(links)
    data["license"] = (
        f"Licensed under `{package.project['license']}`. "
        f"See [LICENSE]({package.source_url(package.settings['license_file'])})."
    )
    data["notices"] = (
        f"See [NOTICE]({package.source_url(package.settings['notice_file'])}) for attribution."
        if "notice_file" in package.settings
        else "No separate NOTICE file is declared. Review the license and bundled third-party attributions."
    )
    return data


def region_spans(text: str) -> list[tuple[str, int, int]]:
    """Return managed region offsets; fenced marker lookalikes are not directives."""
    errors = region_errors(text)
    if errors:
        raise ConfigurationError("; ".join(errors))
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    spans = []
    opened = None
    pattern = re.compile(r"<!-- readme-standards:(begin|end) ([a-z0-9_.-]+) -->")
    for token in PARSER.parse(text):
        if token.type != "html_block":
            continue
        for match in pattern.finditer(token.content):
            start = offsets[token.map[0]] + match.start()
            end = offsets[token.map[0]] + match.end()
            operation, name = match.groups()
            if operation == "begin":
                opened = (name, start)
            elif opened:
                spans.append((name, opened[1], end))
                opened = None
    return spans


def render(text: str, package: Package) -> str:
    data = fragments(package)
    spans = region_spans(text)
    unknown = [name for name, _, _ in spans if name not in data]
    if unknown:
        raise ConfigurationError(f"unknown managed regions: {', '.join(unknown)}")
    for name, start, end in reversed(spans):
        text = text[:start] + block(name, data[name]) + text[end:]
    return text


SECTION_REGIONS = {
    "uv": "installation.uv",
    "pip": "installation.pip",
    "poetry": "installation.poetry",
    "example": "example.quick-start",
    "common-workflows": "example.usage",
    "entry-points": "entry-points",
    "project-links": "project-links",
    "license": "license",
    "notices": "notices",
}


def repair(text: str, package: Package) -> str:
    """Reorder known sections and insert omissions; refuse ambiguity or content loss."""
    spans = region_spans(text)
    data = fragments(package)
    if any(name not in data for name, _, _ in spans):
        raise ConfigurationError("unknown managed region; resolve manually before repair")
    headings, _ = parse(text)
    preamble = "".join(text.splitlines(keepends=True)[: headings[0].line - 1]) if headings else ""
    if preamble.strip() or (text.strip() and not headings):
        raise ConfigurationError(
            "content precedes the first heading; move it manually before repair"
        )
    known = {section.title: section for section in SECTIONS}
    bodies = {}
    for index, heading in enumerate(headings):
        is_title = heading.level == 1 and heading.title == package.name
        if not is_title and heading.title not in known:
            raise ConfigurationError(
                f"unknown heading {heading.title!r}; map it manually before repair"
            )
        key = "package" if is_title else known[heading.title].id
        if key in bodies:
            raise ConfigurationError(
                f"duplicate heading {heading.title!r}; resolve manually before repair"
            )
        body = heading.body
        # Structural separators are canonicalized, never prose or fenced examples.
        body_lines = body.splitlines(keepends=True)
        remove = set()
        for token in PARSER.parse(body):
            if token.type == "hr" and token.level == 0:
                remove.update(range(*token.map))
        bodies[key] = "".join(line for i, line in enumerate(body_lines) if i not in remove).strip()
    title_body = bodies.get("package", "")
    existing_brand = any(name == "branding" for name, _, _ in region_spans(title_body))
    if not existing_brand:
        title_body = block("branding", data["branding"]) + (
            "\n\n" + title_body if title_body else ""
        )
    output = [f"# {package.name}", "", title_body]
    for section in SECTIONS:
        if section.level == 2:
            output.extend(["", "---"])
        body = bodies.get(section.id, "")
        region = SECTION_REGIONS.get(section.id)
        if region and not any(name == region for name, _, _ in region_spans(body)):
            body = block(region, data[region]) + ("\n\n" + body if body else "")
        elif not body and section.content == "authored":
            body = f"<!-- AUTHOR REQUIRED: {section.title}; supply package-specific guidance. -->"
        output.extend(["", "#" * section.level + " " + section.title])
        if body:
            output.extend(["", body])
    return render("\n".join(output).rstrip() + "\n", package)


def diff(before: str, after: str, filename: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=filename,
            tofile=filename,
        )
    )

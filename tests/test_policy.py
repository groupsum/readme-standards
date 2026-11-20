import json

import pytest
from jsonschema import Draft202012Validator

from readme_standards.check import check
from readme_standards.config import schema
from readme_standards.document import parse
from readme_standards.policy import SECTIONS, outline


def test_policy_is_complete_and_has_only_package_title_exception():
    rows = outline("example-package")
    assert len(rows) == 56
    assert rows[0]["title"] == "example-package"
    assert len({r["title"] for r in rows}) == len(rows)
    previous = {}
    for row in rows:
        if row["parent"]:
            assert previous[row["parent"]]["level"] == row["level"] - 1
        previous[row["id"]] = row
    assert {r["level"] for r in rows} == {1, 2, 3, 4}
    Draft202012Validator.check_schema(schema())
    assert json.loads(json.dumps(rows)) == rows


def test_complete_package_passes(package):
    assert check(package) == []


@pytest.mark.parametrize("section", SECTIONS, ids=lambda section: section.id)
def test_every_required_heading_is_checked(package, section):
    text = package.readme.read_text("utf-8")
    text = text.replace("#" * section.level + " " + section.title + "\n", "", 1)
    package.readme.write_text(text, encoding="utf-8")
    assert any(d.rule == "heading.missing" and section.title in d.message for d in check(package))


def test_wrong_order_level_and_parent_are_reported(package):
    text = package.readme.read_text("utf-8").replace(
        "### Why This Package", "##### Why This Package"
    )
    text = (
        text.replace("### Features", "### TEMP")
        .replace("### Non-Goals", "### Features")
        .replace("### TEMP", "### Non-Goals")
    )
    package.readme.write_text(text, encoding="utf-8")
    rules = {d.rule for d in check(package)}
    assert {"heading.level", "heading.parent", "heading.order"} <= rules


def test_fenced_headings_comments_and_markers_do_not_count(package):
    text = package.readme.read_text("utf-8")
    text += "\n```markdown\n## Fake\n<!-- readme-standards:begin unknown -->\n```\n\n<!--\n## Hidden\n-->\n"
    package.readme.write_text(text, encoding="utf-8")
    assert check(package) == []


def test_setext_and_literal_html(package):
    assert parse("Title\n=====\n\nSection\n-------\n")[0][1].level == 2
    package.readme.write_text(
        package.readme.read_text("utf-8") + "\n<h2>Extra</h2>\n", encoding="utf-8"
    )
    assert any(d.rule == "heading.html" for d in check(package))


@pytest.mark.parametrize(
    "body", ["", "N/A", "TODO: write this", "{{description}}", "<!-- AUTHOR REQUIRED -->"]
)
def test_missing_or_placeholder_authored_content_fails(package, body):
    text = package.readme.read_text("utf-8")
    start = text.index("### Summary\n") + len("### Summary\n")
    end = text.index("### Why This Package")
    package.readme.write_text(text[:start] + "\n" + body + "\n\n" + text[end:], encoding="utf-8")
    assert any(d.rule.startswith("content.") for d in check(package))


def test_explicit_non_applicability_is_allowed(package):
    text = package.readme.read_text("utf-8")
    target = "The fixture documents extensions with a distinct package-specific explanation."
    text = text.replace(
        target,
        "This package exposes no extension hooks; compose it through its public constructor.",
    )
    package.readme.write_text(text, encoding="utf-8")
    assert check(package) == []

import pytest

from readme_standards.check import check
from readme_standards.config import ConfigurationError
from readme_standards.document import BEGIN, END
from readme_standards.render import branding, render, repair


def test_repair_is_idempotent_and_preserves_prose(package):
    original = package.readme.read_text("utf-8")
    assert repair(original, package) == original
    damaged = original.replace("### Why This Package", "##### Why This Package")
    repaired = repair(damaged, package)
    assert repaired == original
    package.readme.write_text(repaired, encoding="utf-8")
    assert check(package) == []


def test_missing_heading_is_inserted_without_fabricating_prose(package):
    text = package.readme.read_text("utf-8")
    start = text.index("### Why This Package")
    end = text.index("### When to Use")
    repaired = repair(text[:start] + text[end:], package)
    assert "### Why This Package\n\n<!-- AUTHOR REQUIRED:" in repaired
    assert "The fixture documents summary" in repaired
    package.readme.write_text(repaired, encoding="utf-8")
    assert any(d.rule.startswith("content.") for d in check(package))


@pytest.mark.parametrize(
    "extra", ["\n## Unknown\n\nKeep this content.\n", "\n### Summary\n\nDuplicate prose.\n"]
)
def test_ambiguous_repair_refuses_without_mutation(package, extra):
    text = package.readme.read_text("utf-8") + extra
    with pytest.raises(ConfigurationError):
        repair(text, package)


def test_plain_document_is_never_discarded(package):
    with pytest.raises(ConfigurationError, match="precedes"):
        repair("Important authored content with no heading.\n", package)


def test_nested_unclosed_and_unknown_regions_refuse(package):
    text = package.readme.read_text("utf-8")
    with pytest.raises(ConfigurationError):
        render(text + BEGIN.format(name="branding"), package)
    with pytest.raises(ConfigurationError):
        render(text + BEGIN.format(name="unknown") + "\n" + END.format(name="unknown"), package)


def test_render_only_changes_generated_regions(package):
    text = package.readme.read_text("utf-8")
    changed = text.replace("Source version: 0.1.0", "Source version: wrong")
    assert render(changed, package) == text
    assert render(text, package) == text


def test_badge_and_fragment_order_and_package_scope(package):
    html = branding(package)
    assert html.index("Source version:") < html.index("Python:") < html.index("Layer:")
    assert html.index("Layer:") < html.index("Lifecycle:") < html.index("License:")
    assert html.index("README standards:") < html.index("Tests:") < html.index("Certification:")
    assert "hits.sh/github.com/groupsum/readme-standards/README.md.svg" in html
    assert "example-package unpublished" in html
    assert "pypi/dm/example-package" not in html
    package.settings["distributions"]["pypi"]["published"] = True
    assert "pypi/dm/example-package" in branding(package)


def test_wrong_badge_or_counter_cannot_pass(package):
    text = package.readme.read_text("utf-8").replace(
        "hits.sh/github.com/groupsum", "hits.sh/github.com/global"
    )
    package.readme.write_text(text, encoding="utf-8")
    assert any(d.rule == "generated.stale" for d in check(package))


def test_moving_region_to_wrong_section_fails(package):
    text = package.readme.read_text("utf-8")
    start = text.index(BEGIN.format(name="entry-points"))
    end = text.index(END.format(name="entry-points")) + len(END.format(name="entry-points"))
    region = text[start:end]
    text = text[:start] + text[end:]
    text = text.replace("### Summary\n", "### Summary\n\n" + region + "\n")
    package.readme.write_text(text, encoding="utf-8")
    assert any(d.rule == "generated.location" for d in check(package))

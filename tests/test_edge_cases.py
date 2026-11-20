import pytest

from readme_standards.check import check
from readme_standards.config import ConfigurationError, load_package
from readme_standards.render import render, repair


@pytest.mark.parametrize("name", ["pip", "uv", "Overview"])
def test_package_title_can_equal_a_fixed_section(package, name):
    manifest = package.root / "pyproject.toml"
    manifest.write_text(
        manifest.read_text("utf-8").replace('name = "example-package"', f'name = "{name}"'),
        encoding="utf-8",
    )
    package = load_package(package.root)
    text = package.readme.read_text("utf-8").replace("# example-package\n", f"# {name}\n", 1)
    text = render(text, package)
    package.readme.write_text(text, encoding="utf-8")
    assert check(package) == []
    assert repair(text, package) == text


def test_inline_html_heading_is_rejected(package):
    text = package.readme.read_text("utf-8") + "\nParagraph <h5>Hidden heading</h5>\n"
    package.readme.write_text(text, encoding="utf-8")
    assert any(d.rule == "heading.html" for d in check(package))


def test_global_custom_download_counter_is_rejected(package):
    manifest = package.root / "pyproject.toml"
    text = manifest.read_text("utf-8").replace(
        "published = false",
        'published = false\ndownloads_url = "https://example.org/global"\ndownloads_image = "https://example.org/global.svg"\ndownloads_label = "Monthly downloads"',
    )
    manifest.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="exact distribution"):
        load_package(package.root)


def test_positive_claim_requires_evidence(package):
    manifest = package.root / "pyproject.toml"
    text = manifest.read_text("utf-8").replace('label = "CI gate"', 'label = "tests all passed"')
    manifest.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="evidence"):
        load_package(package.root)

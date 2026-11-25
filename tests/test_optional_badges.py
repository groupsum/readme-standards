import json

import pytest

from readme_standards.check import check
from readme_standards.cli import main
from readme_standards.config import ConfigurationError, load_package
from readme_standards.render import render
from readme_standards.ssot import ssot_badge


@pytest.fixture
def configured_package(package):
    manifest = package.root / "pyproject.toml"
    with manifest.open("a", encoding="utf-8") as file:
        file.write(
            """
[tool.readme_standards.community]
discord = "https://discord.gg/example"
crude = "https://crude.dev/"
github_discussions = "https://github.com/example/project/discussions"

[tool.readme_standards.ssot_governance]
scope = "repository"
report_url = "https://example.org/validation.json"
badge_endpoint = "https://example.org/badge.json?branch=master&scope=repository"
"""
        )
    return load_package(package.root)


@pytest.fixture
def validation_report(configured_package):
    return {
        "repository": configured_package.settings["repository"],
        "scope": "repository",
        "package_path": ".",
        "commit": "a" * 40,
        "policy_version": "v1",
        "validation": {"passed": True, "registry_path": ".ssot/registry.json", "failures": []},
    }


def test_optional_badges_render_in_managed_region(configured_package):
    package = configured_package
    original = package.readme.read_text("utf-8")
    assert "Discord: Join" not in original
    assert "SSOT Governance:" not in original
    updated = render(original, package)
    assert "Governance: repository policy" in updated
    assert "SSOT Governance: repository validation report" in updated
    assert 'href="https://example.org/validation.json"' in updated
    assert (
        "endpoint?url=https%3A%2F%2Fexample.org%2Fbadge.json%3Fbranch%3Dmaster%26scope" in updated
    )
    assert 'href="https://discord.gg/example"><img alt="Discord: Join"' in updated
    assert updated.index("Discord: Join") < updated.index("Crude: Discuss")
    assert updated.index("Crude: Discuss") < updated.index("GitHub Discussions: Discuss")
    assert updated.index("GitHub Discussions: Discuss") < updated.index('href="#overview"')
    package.readme.write_text(updated, encoding="utf-8")
    assert check(package) == []
    assert render(updated, package) == updated


def test_ssot_badge_cli_reads_ci_report(configured_package, validation_report, capsys):
    report = configured_package.root / "validation.json"
    report.write_text(json.dumps(validation_report), encoding="utf-8")
    assert (
        main(
            [
                "ssot-badge",
                "--root",
                str(configured_package.root),
                "--report",
                str(report),
                "--commit",
                "a" * 40,
                "--policy-version",
                "v1",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out) == {
        "schemaVersion": 1,
        "label": "SSOT Governance",
        "message": "passing",
        "color": "166534",
        "labelColor": "1E293B",
    }


def test_ssot_badge_distinguishes_current_failure_and_stale_report(
    configured_package, validation_report
):
    validation_report["validation"].update(passed=False, failures=["Missing evidence"])
    assert ssot_badge(configured_package, validation_report, "a" * 40, "v1")["message"] == "failing"
    assert ssot_badge(configured_package, validation_report, "b" * 40, "v1")["message"] == "stale"
    assert ssot_badge(configured_package, validation_report, "a" * 40, "v2")["message"] == "stale"


def test_ssot_badge_rejects_wrong_package_and_inconsistent_report(
    configured_package, validation_report
):
    configured_package.settings["ssot_governance"]["scope"] = "package"
    configured_package.settings["package_path"] = "packages/example"
    validation_report["scope"] = "package"
    with pytest.raises(ConfigurationError, match="repository and scope"):
        ssot_badge(configured_package, validation_report, "a" * 40, "v1")
    validation_report["package_path"] = "packages/example"
    assert ssot_badge(configured_package, validation_report, "a" * 40, "v1")["message"] == "passing"
    validation_report["validation"]["failures"] = ["Missing evidence"]
    with pytest.raises(ConfigurationError, match="consistent findings"):
        ssot_badge(configured_package, validation_report, "a" * 40, "v1")

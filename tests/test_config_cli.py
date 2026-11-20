import json

import pytest

from readme_standards.cli import main
from readme_standards.config import ConfigurationError, discover, load_package


def test_missing_config_cannot_escape_inventory(tmp_path):
    root = tmp_path / "nested"
    root.mkdir()
    (root / "pyproject.toml").write_text('[project]\nname = "missing"\n', encoding="utf-8")
    assert discover(tmp_path, True) == [root]
    with pytest.raises(ConfigurationError, match="missing"):
        load_package(root)
    assert main(["check", "--root", str(tmp_path), "--all"]) == 1


def test_bad_inventory_does_not_silently_pass(tmp_path):
    with pytest.raises(ConfigurationError, match="no .* manifests"):
        discover(tmp_path, True)
    (tmp_path / "pyproject.toml").write_text("invalid TOML = [", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        discover(tmp_path, True)


def test_paths_and_unknown_config_rejected(package):
    with pytest.raises(ConfigurationError, match="escapes"):
        package.local("../private.txt")
    path = package.root / "pyproject.toml"
    path.write_text(
        path.read_text("utf-8").replace(
            'policy = "package-guide-v1"', 'policy = "package-guide-v1"\nunknown_setting = true'
        ),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="Additional properties"):
        load_package(package.root)


def test_pypi_identity_must_match_manifest(package):
    path = package.root / "pyproject.toml"
    text = path.read_text("utf-8").replace(
        '[tool.readme_standards.distributions.pypi]\nname = "example-package"',
        '[tool.readme_standards.distributions.pypi]\nname = "global-metric"',
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="identity"):
        load_package(package.root)


def test_check_json_and_preview_do_not_write(package, capsys):
    before = package.readme.read_bytes()
    assert main(["check", "--root", str(package.root), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["passed"]
    assert main(["repair", "--root", str(package.root)]) == 0
    assert package.readme.read_bytes() == before


def test_scaffold_is_explicit_and_fails_until_authored(package):
    package.readme.unlink()
    assert main(["scaffold", "--root", str(package.root)]) == 0
    assert not package.readme.exists()
    assert main(["scaffold", "--root", str(package.root), "--write"]) == 1
    assert package.readme.exists()
    assert "AUTHOR REQUIRED" in package.readme.read_text("utf-8")
    assert main(["scaffold", "--root", str(package.root), "--write"]) == 2


def test_schema_and_outline_commands(capsys):
    assert main(["schema"]) == 0
    assert json.loads(capsys.readouterr().out)["additionalProperties"] is False
    assert main(["outline", "--package", "custom", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["title"] == "custom"

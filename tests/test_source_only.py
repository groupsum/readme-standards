from readme_standards.check import check
from readme_standards.config import load_package
from readme_standards.render import fragments, render


def test_source_only_workspaces_do_not_get_fictitious_wheel_install_commands(package):
    manifest = package.root / "pyproject.toml"
    manifest.write_text(
        manifest.read_text("utf-8") + "\n[tool.uv]\npackage = false\n", encoding="utf-8"
    )
    package = load_package(package.root)
    assert not package.installable
    generated = fragments(package)
    assert "uv sync" in generated["installation.uv"]
    assert "pip install" not in generated["installation.pip"]
    assert "poetry add" not in generated["installation.poetry"]
    package.readme.write_text(render(package.readme.read_text("utf-8"), package), encoding="utf-8")
    assert check(package) == []

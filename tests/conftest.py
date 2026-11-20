from pathlib import Path

import pytest

from readme_standards.config import load_package
from readme_standards.policy import SECTIONS
from readme_standards.render import repair

pytest_plugins = ["pytester"]
REPOSITORY = Path(__file__).resolve().parents[1]


@pytest.fixture
def package_factory():
    def make(root, *, complete=True):
        root.mkdir(parents=True, exist_ok=True)
        source = (REPOSITORY / "pyproject.toml").read_text("utf-8")
        settings = "[tool.readme_standards]" + source.split("[tool.readme_standards]", 1)[1]
        settings = settings.replace('name = "readme-standards"', 'name = "example-package"')
        settings = settings.replace("published = true", "published = false")
        project = (
            '[project]\nname = "example-package"\nversion = "0.1.0"\n'
            'description = "A fixture package for README policy tests."\n'
            'readme = "README.md"\nrequires-python = ">=3.11"\nlicense = "Apache-2.0"\n'
        )
        (root / "pyproject.toml").write_text(project + settings, encoding="utf-8")
        (root / "docs").mkdir(exist_ok=True)
        (root / "docs/brands.toml").write_bytes((REPOSITORY / "docs/brands.toml").read_bytes())
        for name in ("LICENSE", "NOTICE"):
            (root / name).write_bytes((REPOSITORY / name).read_bytes())
        (root / "examples").mkdir(exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "tests/test_examples.py").write_text(
            "def test_example():\n    assert 1 == 1\n", encoding="utf-8"
        )
        for name in ("quick_start", "usage"):
            (root / f"examples/{name}.py").write_text('print("fixture result")\n', encoding="utf-8")
            (root / f"examples/{name}.stdout").write_text("fixture result\n", encoding="utf-8")
        package = load_package(root)
        readme = repair("", package)
        if complete:
            for section in SECTIONS:
                if section.content == "authored":
                    readme = readme.replace(
                        f"<!-- AUTHOR REQUIRED: {section.title}; supply package-specific guidance. -->",
                        f"The fixture documents {section.title.lower()} with a distinct package-specific explanation.",
                    )
        package.readme.write_text(readme, encoding="utf-8")
        return package

    return make


@pytest.fixture
def package(tmp_path, package_factory):
    return package_factory(tmp_path / "package")

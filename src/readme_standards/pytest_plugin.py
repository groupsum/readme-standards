"""Collect one read-only README test per discovered package, independently of testpaths."""

from pathlib import Path

import pytest

from .check import check_package
from .config import ConfigurationError, discover


def pytest_addoption(parser):
    group = parser.getgroup("readme-standards")
    group.addoption(
        "--readme-standards", action="store_true", help="collect package README policy tests"
    )
    group.addoption(
        "--readme-root", default=None, help="package or inventory root (defaults to pytest rootdir)"
    )
    group.addoption(
        "--readme-all", action="store_true", help="discover all Python package manifests below root"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    if not config.getoption("--readme-standards"):
        return
    root = Path(config.getoption("--readme-root") or config.rootpath).resolve()
    try:
        roots = discover(root, config.getoption("--readme-all"))
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error
    for package_root in roots:
        relative = package_root.relative_to(root).as_posix()
        item = ReadmeItem.from_parent(
            session, name=f"readme-standards[{relative}]", root=package_root
        )
        items.append(item)


class ReadmeItem(pytest.Item):
    def __init__(self, *, root, **kwargs):
        super().__init__(**kwargs)
        self.package_root = root

    def runtest(self):
        issues = check_package(self.package_root)
        if issues:
            raise ReadmeFailure("\n".join(map(str, issues)))

    def repr_failure(self, excinfo, style=None):
        if isinstance(excinfo.value, ReadmeFailure):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style=style)

    def reportinfo(self):
        return self.package_root / "pyproject.toml", 0, self.name


class ReadmeFailure(Exception):
    """Concise pytest failure with rule IDs and source locations."""

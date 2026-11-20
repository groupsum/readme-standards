import zipfile

import pytest

from readme_standards.artifacts import check_wheel


def wheel(
    package, tmp_path, *, description=None, name="example-package", version="0.1.0", notice=True
):
    path = tmp_path / "example_package-0.1.0-py3-none-any.whl"
    metadata = (
        f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n"
        "Description-Content-Type: text/markdown\nLicense-Expression: Apache-2.0\n"
        "License-File: LICENSE\nLicense-File: NOTICE\n\n"
    )
    metadata += package.readme.read_text("utf-8") if description is None else description
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("example_package-0.1.0.dist-info/METADATA", metadata)
        for filename in ("LICENSE", "NOTICE"):
            if filename != "NOTICE" or notice:
                archive.writestr(
                    f"example_package-0.1.0.dist-info/licenses/{filename}",
                    package.local(filename).read_bytes(),
                )
    return path


def test_wheel_readme_and_legal_documents(package, tmp_path):
    assert check_wheel(package, wheel(package, tmp_path)) == []


@pytest.mark.parametrize(
    "options,rule",
    [
        ({"description": "stale README"}, "wheel.readme"),
        ({"notice": False}, "wheel.legal"),
        ({"name": "wrong-package"}, "wheel.name"),
        ({"version": "9.0"}, "wheel.version"),
    ],
)
def test_wheel_mismatches_fail(package, tmp_path, options, rule):
    assert rule in {d.rule for d in check_wheel(package, wheel(package, tmp_path, **options))}

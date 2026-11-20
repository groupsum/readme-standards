def test_plugin_adds_item_despite_testpaths(pytester, package_factory):
    package_factory(pytester.path)
    pytester.makeini("[pytest]\ntestpaths = tests\n")
    result = pytester.runpytest_subprocess("--readme-standards", "-q")
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines(["*2 passed*"])


def test_plugin_is_opt_in(pytester):
    pytester.makepyfile("def test_normal():\n    assert True\n")
    result = pytester.runpytest_subprocess("-q")
    result.assert_outcomes(passed=1)


def test_plugin_can_gate_without_python_tests(pytester, package_factory):
    package = package_factory(pytester.path)
    (package.root / "tests/test_examples.py").write_text(
        "# Referenced test file for this collection fixture.\n", encoding="utf-8"
    )
    result = pytester.runpytest_subprocess("--readme-standards", "-q")
    result.assert_outcomes(passed=1)


def test_missing_document_fails_as_readable_pytest_item(pytester, package_factory):
    package = package_factory(pytester.path)
    package.readme.unlink()
    result = pytester.runpytest_subprocess("--readme-standards", "-q")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(["*readme.missing*required README*"])


def test_unconfigured_nested_package_is_not_skipped(pytester, package_factory):
    package_factory(pytester.path)
    child = pytester.path / "pkgs/missing"
    child.mkdir(parents=True)
    (child / "pyproject.toml").write_text('[project]\nname = "missing"\n', encoding="utf-8")
    result = pytester.runpytest_subprocess("--readme-standards", "--readme-all", "-q")
    result.assert_outcomes(passed=2, failed=1)
    assert "config: missing [tool.readme_standards]" in result.stdout.str()

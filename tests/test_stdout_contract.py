from readme_standards.check import check
from readme_standards.config import load_package
from readme_standards.render import render


def test_examples_that_return_values_without_printing_can_expect_empty_stdout(package):
    source = package.local(package.settings["examples"]["quick_start"]["source"])
    source.write_text('assert "example".upper() == "EXAMPLE"\n', encoding="utf-8")
    package.local(package.settings["examples"]["quick_start"]["expected_stdout"]).write_text(
        "", encoding="utf-8"
    )
    package.readme.write_text(render(package.readme.read_text("utf-8"), package), encoding="utf-8")
    assert check(package) == []


def test_assertion_based_examples_can_declare_successful_exit_without_a_stdout_fixture(package):
    manifest = package.root / "pyproject.toml"
    text = manifest.read_text("utf-8").replace(
        'expected_stdout = "examples/quick_start.stdout"', "expected_exit_code = 0"
    )
    manifest.write_text(text, encoding="utf-8")
    package = load_package(package.root)
    assert check(package) == []


def test_top_level_await_is_not_an_executable_python_example(package):
    source = package.local(package.settings["examples"]["quick_start"]["source"])
    source.write_text("await something()\n", encoding="utf-8")
    package.readme.write_text(render(package.readme.read_text("utf-8"), package), encoding="utf-8")
    assert any(d.rule == "example.syntax" for d in check(package))

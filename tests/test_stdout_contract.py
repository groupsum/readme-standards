from readme_standards.check import check
from readme_standards.render import render


def test_examples_that_return_values_without_printing_can_expect_empty_stdout(package):
    source = package.local(package.settings["examples"]["quick_start"]["source"])
    source.write_text('assert "example".upper() == "EXAMPLE"\n', encoding="utf-8")
    package.local(package.settings["examples"]["quick_start"]["expected_stdout"]).write_text(
        "", encoding="utf-8"
    )
    package.readme.write_text(render(package.readme.read_text("utf-8"), package), encoding="utf-8")
    assert check(package) == []

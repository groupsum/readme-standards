import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["quick_start", "usage"])
def test_readme_example_stdout(name):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / f"examples/{name}.py")],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.stdout == (root / f"examples/{name}.stdout").read_text("utf-8")

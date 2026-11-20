"""Built-wheel checks and explicitly requested installed-example execution."""

import email.policy
import os
import subprocess
import tempfile
import venv
import zipfile
from email.parser import BytesParser
from pathlib import Path

from packaging.utils import canonicalize_name

from .check import Diagnostic
from .config import Package


def check_wheel(package: Package, wheel: Path) -> list[Diagnostic]:
    issues = []

    def fail(rule: str, message: str) -> None:
        issues.append(Diagnostic(str(wheel), 1, rule, message))

    try:
        with zipfile.ZipFile(wheel) as archive:
            metadata_paths = [
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_paths) != 1:
                fail("wheel.metadata", "expected exactly one distribution METADATA")
                return issues
            message = BytesParser(policy=email.policy.default).parsebytes(
                archive.read(metadata_paths[0])
            )
            if canonicalize_name(message.get("Name", "")) != canonicalize_name(package.name):
                fail("wheel.name", "wheel name does not match manifest")
            if message.get("Version") != package.project["version"]:
                fail("wheel.version", "wheel version does not match manifest")
            if not message.get("Description-Content-Type", "").startswith("text/markdown"):
                fail("wheel.content-type", "wheel README must declare text/markdown")
            body = message.get_payload(decode=True).decode("utf-8")
            if not isinstance(body, str) or body.replace("\r\n", "\n").rstrip(
                "\n"
            ) != package.readme.read_text("utf-8").replace("\r\n", "\n").rstrip("\n"):
                fail("wheel.readme", "wheel description differs from source README")
            if message.get("License-Expression") != package.project["license"]:
                fail("wheel.license", "wheel License-Expression differs from manifest")
            license_headers = message.get_all("License-File", [])
            prefix = metadata_paths[0].removesuffix("METADATA") + "licenses/"
            for key in ("license_file", "notice_file"):
                if key not in package.settings:
                    continue
                declared = package.settings[key]
                if declared not in license_headers:
                    fail("wheel.legal", f"{declared} is absent from License-File metadata")
                target = prefix + declared
                if (
                    target not in archive.namelist()
                    or archive.read(target) != package.local(declared).read_bytes()
                ):
                    fail(
                        "wheel.legal",
                        f"{declared} is missing or differs from the package's legal document",
                    )
    except (OSError, zipfile.BadZipFile, ValueError) as error:
        fail("wheel.invalid", str(error))
    return issues


def run_examples(package: Package, wheel: Path) -> None:
    """Install a wheel into a new venv and assert both declared stdout fixtures.

    Explicit execution, not a sandbox. Only run for trusted projects/wheels.
    Dependencies are installed normally by pip; callers control index settings.
    """
    problems = check_wheel(package, wheel)
    if problems:
        raise ValueError("\n".join(map(str, problems)))
    wheel = wheel.resolve()
    for example in package.settings["examples"].values():
        if example.get("language", "python") != "python":
            raise ValueError("installed example runner currently supports Python examples only")
    with tempfile.TemporaryDirectory(prefix="readme-standards-") as directory:
        root = Path(directory)
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)],
            cwd=root,
            check=True,
            timeout=300,
        )
        # Run each example without source-tree imports or inherited application credentials.
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "LANG"}
        }
        clean_env["PYTHONUTF8"] = "1"
        for name, example in package.settings["examples"].items():
            script = root / f"{name}.py"
            script.write_bytes(package.local(example["source"]).read_bytes())
            result = subprocess.run(
                [str(python), "-I", str(script)],
                cwd=root,
                env=clean_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=example.get("timeout", 30),
            )
            expected = (
                package.local(example["expected_stdout"]).read_text("utf-8")
                if "expected_stdout" in example
                else None
            )
            if expected is not None and result.stdout.replace("\r\n", "\n") != expected.replace(
                "\r\n", "\n"
            ):
                raise ValueError(
                    f"{name}: stdout differs from {example['expected_stdout']}: {result.stdout!r}"
                )

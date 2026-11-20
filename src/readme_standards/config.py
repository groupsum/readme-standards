"""Validated TOML inputs; no imports of the package being documented."""

import fnmatch
import json
import os
import re
import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from packaging.utils import canonicalize_name


class ConfigurationError(ValueError):
    """A package cannot be audited until its configuration is corrected."""


def schema() -> dict:
    return json.loads(files("readme_standards").joinpath("schema.json").read_text("utf-8"))


@dataclass(frozen=True)
class Package:
    root: Path
    project: dict
    settings: dict
    brand: dict
    installable: bool = True

    @property
    def name(self) -> str:
        return self.project["name"]

    @property
    def readme(self) -> Path:
        return self.local(self.settings.get("readme", "README.md"))

    def local(self, value: str) -> Path:
        path = (self.root / value).resolve()
        if not path.is_relative_to(self.root):
            raise ConfigurationError(f"package-local path escapes package directory: {value}")
        return path

    def source_url(self, path: str, tree: bool = False) -> str:
        from urllib.parse import quote

        prefix = self.settings["package_path"].strip("/")
        suffix = "/".join(p for p in (prefix, path) if p and p != ".")
        return (
            f"{self.settings['repository']}/{'tree' if tree else 'blob'}/"
            f"{quote(self.settings['ref'], safe='')}/{quote(suffix, safe='/')}"
        )


def load_package(root: Path) -> Package:
    root = root.resolve()
    try:
        data = tomllib.loads((root / "pyproject.toml").read_text("utf-8-sig"))
        project = data.get("project", {})
        settings = data.get("tool", {}).get("readme_standards")
        if not settings:
            raise ConfigurationError("missing [tool.readme_standards]")
        errors = sorted(
            Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(settings),
            key=lambda error: str(list(error.path)),
        )
        if errors:
            raise ConfigurationError(
                "; ".join(
                    f"{'.'.join(map(str, e.path)) or 'configuration'}: {e.message}" for e in errors
                )
            )
        if not isinstance(project.get("name"), str) or not project["name"]:
            raise ConfigurationError("[project].name is required")
        for key in ("description", "requires-python"):
            if not isinstance(project.get(key), str) or not project[key].strip():
                raise ConfigurationError(f"[project].{key} must be a nonempty string")
        if not isinstance(project.get("version"), str):
            raise ConfigurationError(
                "[project].version must be explicit; dynamic versions need an adapter"
            )
        license_value = project.get("license")
        if not isinstance(license_value, str) or not license_value.strip():
            raise ConfigurationError("[project].license must be an SPDX expression string")
        readme = settings.get("readme", "README.md")
        declared_readme = project.get("readme")
        if isinstance(declared_readme, dict):
            declared_readme = declared_readme.get("file")
        if declared_readme != readme:
            raise ConfigurationError("[project].readme must reference the configured README file")
        if (
            PurePosixPath(settings["package_path"]).is_absolute()
            or ".." in PurePosixPath(settings["package_path"]).parts
        ):
            raise ConfigurationError("package_path must be repository-relative without '..'")
        pypi = settings["distributions"].get("pypi")
        if pypi and canonicalize_name(pypi["name"]) != canonicalize_name(project["name"]):
            raise ConfigurationError("PyPI badge identity must match [project].name")
        for distribution in settings["distributions"].values():
            for key in ("downloads_url", "downloads_image"):
                if key in distribution:
                    target = unquote(distribution[key]).removesuffix(".svg").removesuffix(".json")
                    identity = re.escape(distribution["name"])
                    if not re.search(r"(?<![\w.@-])" + identity + r"(?![\w.@-])", target, re.I):
                        raise ConfigurationError(f"{key} must identify this exact distribution")
        for status in settings["statuses"].values():
            label = status["label"].casefold()
            if (
                label not in {"not certified", "not applicable"}
                and re.search(r"\b(?:verified|certified|pass(?:ed|ing)?)\b", label)
                and "evidence_file" not in status
            ):
                raise ConfigurationError("positive status labels require an evidence_file")
        catalog = root / settings["brand_catalog"]
        # Catalogs may be shared above a package directory; local examples may not.
        brands = tomllib.loads(catalog.read_text("utf-8-sig"))["brands"]
        brand = brands[settings["brand"]]
        if set(brand) != {"name", "homepage", "logo_url", "logo_alt"}:
            raise ConfigurationError("brand requires exactly name, homepage, logo_url, logo_alt")
        for key in ("homepage", "logo_url"):
            if urlsplit(brand[key]).scheme != "https" or not urlsplit(brand[key]).netloc:
                raise ConfigurationError(f"brand {key} must be an absolute HTTPS URL")
        if not all(isinstance(v, str) and v.strip() for v in brand.values()):
            raise ConfigurationError("brand fields must be nonempty strings")
        package = Package(
            root,
            project,
            settings,
            brand,
            data.get("tool", {}).get("uv", {}).get("package", True) is not False,
        )
        package.readme  # Validate containment, including symlinks.
        for key in ("license_file", "notice_file"):
            if key in settings:
                package.local(settings[key])
        return package
    except ConfigurationError:
        raise
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ConfigurationError(str(error)) from error


def discover(root: Path, all_packages: bool = False) -> list[Path]:
    """Discover manifests even when they omit this plugin's declaration."""
    root = root.resolve()
    if not all_packages:
        return [root]
    exclusions = []
    manifest = root / "pyproject.toml"
    if manifest.exists():
        try:
            exclusions = (
                tomllib.loads(manifest.read_text("utf-8-sig"))
                .get("tool", {})
                .get("readme_standards", {})
                .get("exclude", [])
            )
        except (OSError, ValueError) as error:
            raise ConfigurationError(f"cannot read inventory settings: {error}") from error
    found = []
    ignored = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in ignored and not d.startswith("."))
        path = Path(current)
        relative = path.relative_to(root).as_posix()
        if any(fnmatch.fnmatchcase(relative, pattern) for pattern in exclusions):
            dirs[:] = []
            continue
        if "pyproject.toml" in names:
            try:
                data = tomllib.loads((path / "pyproject.toml").read_text("utf-8-sig"))
            except (OSError, ValueError) as error:
                raise ConfigurationError(f"invalid manifest {path}: {error}") from error
            if "project" in data:
                found.append(path)
    if not found:
        raise ConfigurationError("inventory contains no [project] package manifests")
    return found

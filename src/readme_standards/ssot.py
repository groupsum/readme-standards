"""Convert a scoped SSOT Registry CI report to a Shields endpoint payload."""

import re

from .config import ConfigurationError, Package
from .render import AMBER, GREEN, LABEL_COLOR, RED


def ssot_badge(package: Package, report: object, commit: str, policy_version: str) -> dict:
    settings = package.settings
    if "ssot_governance" not in settings:
        raise ConfigurationError("ssot-badge requires [tool.readme_standards.ssot_governance]")
    scope = settings["ssot_governance"]["scope"]
    scope_path = settings["package_path"] if scope == "package" else "."
    if (
        not isinstance(report, dict)
        or report.get("repository") != settings["repository"]
        or report.get("scope") != scope
        or report.get("package_path") != scope_path
    ):
        raise ConfigurationError("SSOT report must match the configured repository and scope")
    report_commit = report.get("commit")
    report_policy = report.get("policy_version")
    if (
        not isinstance(report_commit, str)
        or not re.fullmatch(r"[0-9a-f]{40}", report_commit)
        or not re.fullmatch(r"[0-9a-f]{40}", commit)
        or not isinstance(report_policy, str)
        or not report_policy.strip()
        or not policy_version.strip()
    ):
        raise ConfigurationError(
            "SSOT report and badge require full commit SHAs and policy versions"
        )
    validation = report.get("validation")
    if not isinstance(validation, dict):
        raise ConfigurationError("SSOT report requires an SSOT Registry validation result")
    failures = validation.get("failures")
    if (
        not isinstance(failures, list)
        or not all(isinstance(item, str) and item.strip() for item in failures)
        or validation.get("passed") is not (not failures)
        or not isinstance(validation.get("registry_path"), str)
        or not validation["registry_path"].strip()
    ):
        raise ConfigurationError(
            "SSOT validation result requires a registry path and consistent findings"
        )

    if (report_commit, report_policy) != (commit, policy_version):
        message, color = "stale", AMBER
    elif validation["passed"]:
        message, color = "passing", GREEN
    else:
        message, color = "failing", RED
    return {
        "schemaVersion": 1,
        "label": "SSOT Governance",
        "message": message,
        "color": color,
        "labelColor": LABEL_COLOR,
    }

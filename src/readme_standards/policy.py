"""One ordered policy shared by scaffolding, repair, checking, and documentation."""

from dataclasses import asdict, dataclass

POLICY_VERSION = "package-guide-v1"


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    level: int
    parent: str
    content: str = "authored"


# H1 is always the manifest distribution name, the only variable heading label.
SECTIONS = (
    Section("overview", "Overview", 2, "package", "container"),
    Section("summary", "Summary", 3, "overview"),
    Section("why-this-package", "Why This Package", 3, "overview"),
    Section("when-to-use", "When to Use", 3, "overview"),
    Section("features", "Features", 3, "overview"),
    Section("non-goals", "Non-Goals", 3, "overview"),
    Section("getting-started", "Getting Started", 2, "package", "container"),
    Section("prerequisites", "Prerequisites", 3, "getting-started"),
    Section("installation", "Installation", 3, "getting-started", "container"),
    Section("uv", "uv", 4, "installation", "generated"),
    Section("pip", "pip", 4, "installation", "generated"),
    Section("poetry", "Poetry", 4, "installation", "generated"),
    Section("quick-start", "Quick Start", 3, "getting-started", "container"),
    Section("example", "Example", 4, "quick-start", "example"),
    Section("expected-result", "Expected Result", 4, "quick-start"),
    Section("usage", "Usage", 2, "package", "container"),
    Section("common-workflows", "Common Workflows", 3, "usage", "example"),
    Section("configuration", "Configuration", 3, "usage"),
    Section("error-handling", "Error Handling", 3, "usage"),
    Section("best-practices", "Best Practices", 3, "usage"),
    Section("package-boundary", "Package Boundary", 2, "package", "container"),
    Section("what-it-owns", "What It Owns", 3, "package-boundary"),
    Section(
        "public-api-and-import-surfaces", "Public API and Import Surfaces", 3, "package-boundary"
    ),
    Section("entry-points", "Entry Points", 3, "package-boundary", "generated"),
    Section("injected-dependencies", "Injected Dependencies", 3, "package-boundary"),
    Section("protocol-consumers", "Protocol Consumers", 3, "package-boundary"),
    Section("extensions", "Extensions", 3, "package-boundary"),
    Section("operations-and-readiness", "Operations and Readiness", 2, "package", "container"),
    Section("operational-requirements", "Operational Requirements", 3, "operations-and-readiness"),
    Section("health-and-observability", "Health and Observability", 3, "operations-and-readiness"),
    Section(
        "security-and-resource-limits",
        "Security and Resource Limits",
        3,
        "operations-and-readiness",
    ),
    Section("compatibility", "Compatibility", 3, "operations-and-readiness"),
    Section("verification", "Verification", 2, "package", "container"),
    Section("tests", "Tests", 3, "verification"),
    Section("certification-status", "Certification Status", 3, "verification"),
    Section("evidence", "Evidence", 3, "verification"),
    Section("faq", "FAQ", 2, "package", "container"),
    Section("why", "Why", 3, "faq"),
    Section("how", "How", 3, "faq"),
    Section("when", "When", 3, "faq"),
    Section(
        "documentation-and-related-packages",
        "Documentation and Related Packages",
        2,
        "package",
        "container",
    ),
    Section("more-documentation", "More Documentation", 3, "documentation-and-related-packages"),
    Section("related-packages", "Related Packages", 3, "documentation-and-related-packages"),
    Section("project-links", "Project Links", 3, "documentation-and-related-packages", "generated"),
    Section("contributing", "Contributing", 2, "package", "container"),
    Section("how-to-contribute", "How to Contribute", 3, "contributing"),
    Section("development-setup", "Development Setup", 3, "contributing"),
    Section("notes-for-maintainers", "Notes for Maintainers", 3, "contributing"),
    Section("governance", "Governance", 2, "package", "container"),
    Section("ownership-and-decision-making", "Ownership and Decision Making", 3, "governance"),
    Section("standards-and-policies", "Standards and Policies", 3, "governance"),
    Section("lifecycle-and-migration", "Lifecycle and Migration", 3, "governance"),
    Section("license-and-attribution", "License and Attribution", 2, "package", "container"),
    Section("license", "License", 3, "license-and-attribution", "generated"),
    Section("notices", "Notices", 3, "license-and-attribution", "generated"),
)


def outline(package_name: str = "<package name>") -> list[dict]:
    """Return the complete ordered heading tree, including content ownership."""
    return [dict(id="package", title=package_name, level=1, parent=None, content="generated")] + [
        asdict(section) for section in SECTIONS
    ]

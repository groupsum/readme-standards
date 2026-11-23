# readme-standards

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/groupsum/readme-standards"><img src="https://raw.githubusercontent.com/groupsum/readme-standards/master/docs/assets/readme-standards.svg" alt="Groupsum README Standards" width="300"></a></p>
<p align="center"><strong>readme-standards</strong></p>
<p align="center">Versioned package README generation, authoring checks, and pytest gates.</p>
<p align="center">
<a href="https://pypi.org/project/readme-standards/"><img alt="pypi: readme-standards" src="https://img.shields.io/pypi/v/readme-standards?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/pyproject.toml"><img alt="Source version: 0.1.2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/pyproject.toml"><img alt="Python: &gt;=3.11" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.11&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/pyproject.toml"><img alt="Layer: developer-tools" src="https://img.shields.io/static/v1?label=Layer&amp;message=developer-tools&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/readme-standards/"><img alt="Monthly PyPI downloads: readme-standards" src="https://img.shields.io/pypi/dm/readme-standards?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/README.md"><img alt="README hits: readme-standards" src="https://hits.sh/github.com/groupsum/readme-standards/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/groupsum/readme-standards/actions/workflows/ci.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/groupsum/readme-standards/actions/workflows/ci.yml"><img alt="Tests: repository CI" src="https://img.shields.io/static/v1?label=Tests&amp;message=repository%20CI&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/groupsum/readme-standards/blob/master/GOVERNANCE.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/groupsum/readme-standards/actions/workflows/ci.yml"><img alt="Evidence: test suite" src="https://img.shields.io/static/v1?label=Evidence&amp;message=test%20suite&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

README Standards is a Python library, command-line tool, and pytest plugin for consistent package documentation. It compares package READMEs with a versioned heading tree, renders metadata-driven fragments, and reports missing authored content.

### Why This Package

Monorepos can have hundreds of READMEs that disagree on structure and contain stale package badges. This tool centralizes the heading contract while keeping explanations and examples with each package.

### When to Use

Use it when Python distributions need the same documentation structure, package-specific branding, and a CI gate. It can render badges for additional declared registries; automatic manifest discovery currently supports Python pyproject.toml projects only.

### Features

- One package-name H1 and 55 fixed H2–H4 sections.
- CommonMark-aware checks with source locations.
- Deterministic branding, installer commands, entry points, and example inclusion.
- Conservative repair with a diff before an explicit write.
- Pytest collection independent of normal testpaths.
- Built-wheel README and legal-document checks.
- Explicit isolated installed-wheel Python example execution.

### Non-Goals

The plugin does not certify the quality or truth of arbitrary prose, award external certification, publish packages, manage Trusted Publishers, or execute examples during ordinary README checks. It does not yet discover Cargo, npm, or container manifests.

---

## Getting Started

### Prerequisites

Python 3.11 or later is required. Install the published distribution as a development dependency; Git is needed only for source development. Example execution additionally requires venv and pip plus access to the dependencies of the selected wheel.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add readme-standards
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install readme-standards
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add readme-standards
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [examples/quick_start.py](https://github.com/groupsum/readme-standards/blob/master/examples/quick_start.py).

```python
from readme_standards import outline

headings = outline("example-package")
assert headings[0]["title"] == "example-package"
assert headings[1]["title"] == "Overview"
print(f"{headings[0]['title']}: {len(headings)} required headings")
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example prints `example-package: 56 required headings`. Its assertions confirm that the package name is the H1 and Overview is the first fixed section.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [examples/usage.py](https://github.com/groupsum/readme-standards/blob/master/examples/usage.py).

```python
from readme_standards.document import parse

headings, separators = parse("# example-package\n\n---\n\n## Overview\n")
assert [h.title for h in headings] == ["example-package", "Overview"]
assert len(separators) == 1
print("Parsed package title, Overview, and one group separator.")
```
<!-- readme-standards:end example.usage -->

### Configuration

Declare `[tool.readme_standards]` in each package manifest. The complete machine-readable contract is [schema.json](https://github.com/groupsum/readme-standards/blob/master/src/readme_standards/schema.json); the repository [pyproject.toml](https://github.com/groupsum/readme-standards/blob/master/pyproject.toml) is a complete working configuration. Brand catalogs may be shared above package directories.

### Error Handling

Check failures identify a file, line, rule ID, and corrective action. CLI exit code 1 means policy violations; 2 means configuration or command errors. Repair refuses unknown or duplicate headings, malformed regions, and ambiguous preambles. Read-only checks never repair files.

### Best Practices

Keep authored explanations in README.md and runnable examples in maintained source files. Run render after metadata changes, review the diff, and gate both source and built artifacts. Pin the plugin revision in downstream dependency locks and review prose separately from structural checks.

---

## Package Boundary

### What It Owns

This package owns the package-guide-v1 outline, its configuration schema, managed fragment generation, diagnostics, and pytest adapter. Package authors own behavioral claims and prose; repository maintainers own shared branding and governance declarations.

### Public API and Import Surfaces

The stable top-level exports are `POLICY_VERSION` and `outline(package_name)`. CLI behavior and the versioned policy are public contracts. Modules such as `document`, `check`, and `render` expose implementation helpers that may evolve before 1.0; consumers should prefer the CLI or pytest integration.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `readme-standards` → `readme_standards.cli:main`
- `pytest11` → `readme_standards` → `readme_standards.pytest_plugin`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The checker reads an explicit package root, manifest, README, brand catalog, example files, and legal documents. It uses markdown-it-py for parsing, jsonschema for configuration, packaging for names, and pytest for test integration. It imports no target-package runtime code during ordinary checks.

### Protocol Consumers

Pytest loads the plugin through its pytest11 entry point. CI and developer tools consume the CLI text diagnostics or JSON report. Downstream repositories consume the packaged schema and versioned outline.

### Extensions

Version 0.1 provides no third-party policy or manifest-adapter hook. Propose new ecosystem adapters and policy versions through reviewed contributions. All package-guide-v1 heading labels remain fixed.

---

## Operations and Readiness

### Operational Requirements

Ordinary checks run locally without credentials or network access after dependencies are installed. Render and repair write only when --write is passed. Installed-wheel example execution is an explicit command and may install dependencies from configured indexes.

### Health and Observability

This is a command-line library, not a long-running service, so it exposes no health endpoint. Use process exit status, pytest results, and `check --format json` diagnostics to observe policy compliance.

### Security and Resource Limits

Run example execution only on trusted projects and wheels. A fresh venv and isolated Python imports are not an operating-system sandbox. Scripts have timeouts; package-local paths cannot escape the package directory. Ordinary checks do not fetch badge URLs or execute examples. See [SECURITY.md](https://github.com/groupsum/readme-standards/blob/master/SECURITY.md).

### Compatibility

The distribution requires Python >=3.11 and pytest >=8,<10. CI exercises Python 3.11 through 3.14 on Linux and Python 3.13 on Windows. Current discovery requires static PEP 621 name, version, README reference, and SPDX license metadata; dynamic versions need a future adapter.

---

## Verification

### Tests

Run `uv run pytest --readme-standards`. The suite checks every missing section, heading order and parents, authored omissions, safe repair, package-scoped badges, wheel metadata, and actual pytest subprocess integration. `tests/test_examples.py` executes both maintained examples.

### Certification Status

This project has no external certification. A passing README gate establishes the declared structural and mechanical checks only; it does not certify prose completeness, security, or runtime behavior of downstream packages.

### Evidence

The [CI workflow](https://github.com/groupsum/readme-standards/actions/workflows/ci.yml) runs tests, the source README gate, wheel checks, and installed-wheel examples. Its result applies to the tested commit. Positive configured status labels require a local evidence record matching package, version, policy, and checks; authors remain responsible for the record’s truth.

---

## FAQ

### Why

**Why keep an inapplicable section?** Stable locations help readers compare packages. Explain the absence concretely, such as declaring that no CLI entry points are registered, instead of removing the section or writing a bare applicability abbreviation.

### How

**How is prose protected?** Only marked generated regions are replaced by render. Repair moves known sections with their bodies and stops when unknown headings or duplicates make ownership ambiguous. Authored paragraphs remain in README.md.

### When

**When does a missing section fail?** Check and pytest fail immediately. Explicit repair can insert its heading and an authoring comment, but the content gate keeps failing until an explanation is written.

---

## Documentation and Related Packages

### More Documentation

See the [complete outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md), [branding contract](https://github.com/groupsum/readme-standards/blob/master/docs/branding.md), [tool schema](https://github.com/groupsum/readme-standards/blob/master/docs/configuration.md), [authoring guide](https://github.com/groupsum/readme-standards/blob/master/docs/authoring.md), and [implementation guide](https://github.com/groupsum/readme-standards/blob/master/docs/development.md).

### Related Packages

Pytest supplies collection and reporting; markdown-it-py supplies the CommonMark syntax tree; jsonschema validates configuration. This project complements project-specific documentation and example tests rather than replacing them.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/groupsum/readme-standards/tree/master/docs)
- [Homepage](https://github.com/groupsum/readme-standards)
- [Issues](https://github.com/groupsum/readme-standards/issues)
- [Repository](https://github.com/groupsum/readme-standards)
- [pypi: readme-standards](https://pypi.org/project/readme-standards/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow [CONTRIBUTING.md](https://github.com/groupsum/readme-standards/blob/master/CONTRIBUTING.md). Include the failing README scenario, a focused change, and regression tests. Preserve authored content and avoid weakening a gate merely to accept a broken document.

### Development Setup

Clone the repository, run `uv sync --group dev`, then `uv run pytest --readme-standards`. Use `uv run ruff check .` and `uv run ruff format --check .` for lint and formatting. Build with `uv build`.

### Notes for Maintainers

Keep schema, policy, renderer, tests, and docs synchronized. Run render when example formatting or package metadata changes. A changed heading contract needs a new policy identifier. Release through the tag-scoped Trusted Publishing workflow documented in docs/release.md; verify artifacts and a clean install after each publication.

---

## Governance

### Ownership and Decision Making

Groupsum maintains the project. Submit proposals through issues and pull requests; maintainers decide compatibility, policy changes, and releases. The governing record is [GOVERNANCE.md](https://github.com/groupsum/readme-standards/blob/master/GOVERNANCE.md).

### Standards and Policies

Package-guide-v1 requires the same heading labels, levels, parents, separators, and order in every package. H1 alone varies with the manifest name. CI checks the plugin’s own README and shipped schema. Content review remains required for package-specific claims.

### Lifecycle and Migration

Version 0.1 is active initial development. Existing repositories should audit first, map ambiguous headings manually, preview repair, fill authored gaps, and enable CI before adoption. This work does not migrate or republish downstream packages automatically.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/groupsum/readme-standards/blob/master/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/groupsum/readme-standards/blob/master/NOTICE) for attribution.
<!-- readme-standards:end notices -->

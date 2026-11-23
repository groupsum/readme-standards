# Tool schema

The authoritative JSON Schema is packaged at
[`src/readme_standards/schema.json`](../src/readme_standards/schema.json).
Print it with `readme-standards schema`. Unknown settings are errors.
All paths except brand_catalog are package-local and cannot escape through `..` or symlinks.

## Required package facts

The first adapter reads PEP 621 `[project]` metadata from pyproject.toml:
name, explicit version, readme filename, description, requires-python, SPDX license,
URLs, console/GUI scripts, and entry-point groups. Project.readme must point to the
configured README. Dynamic versions and legacy Poetry-only manifests are not supported
in 0.1; they fail rather than being assigned an invented value.

## Configuration fields

| Field | Required | Meaning |
| --- | --- | --- |
| policy | Yes | Exactly package-guide-v1 |
| readme | No | Defaults to README.md |
| brand | Yes | Key in the shared brand catalog |
| brand_catalog | Yes | TOML catalog path, relative to the package manifest; may point above package directory |
| repository | Yes | HTTPS github.com/owner/repository URL |
| ref | Yes | Source branch, tag, or commit used in generated links |
| package_path | Yes | Repository-relative package directory; `.` for root |
| layer | Yes | Package architectural layer |
| lifecycle | Yes | active, experimental, planning, deprecated, or retired |
| license_file | Yes | Package-local legal document |
| notice_file | No | Package-local notice when applicable |
| exclude | No | Root-relative fnmatch patterns excluding inventory subtrees; review these as policy exceptions |
| distributions | Yes | One or more pypi/crates/npm/ghcr declarations |
| examples | Yes | quick_start and usage source/output/test declarations |
| statuses | Yes | readme, tests, certification, governance, evidence status declarations |

Each distribution has `name` and boolean `published`. Optional custom metrics require
all three of downloads_url, downloads_image, and downloads_label. Registry order is fixed.
The PyPI name must canonically match project.name. Other registry identities are explicit
because cross-ecosystem distribution names can differ.

Each example has package-local `source` and `test` paths, plus either an `expected_stdout` fixture or explicit `expected_exit_code = 0`. Optional
language defaults to python; timeout defaults to 30 seconds and is limited to 1ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“300.
Source rendering supports fenced code labels; installed execution supports Python only.
An expected stdout file may be empty when the example returns values without printing.
Checking that a referenced test exists is not a claim that the test has executed.

Each status has `label` and an HTTPS `url`; optional evidence_file points to local JSON.
Positive labels such as verified, partial, passed, or passing require evidence_file.
Certification labels are limited to not certified, not applicable, partial, and verified.

```json
{
  "package": "example-package",
  "version": "0.1.0",
  "policy": "package-guide-v1",
  "status": "passed",
  "checks": ["quick-start-installed-wheel"]
}
```

This record establishes declared evidence identity, not an independently verified certificate.
Use immutable CI artifact/report URLs and record more provenance in your repository's
evidence format where needed. The plugin never upgrades a claim just because a link exists.

## Complete working configuration

The repository's [pyproject.toml](../pyproject.toml) exercises the full configuration.
For another package, copy its tool.readme_standards tables, set that package's identities,
point brand_catalog at the shared catalog, and provide the declared examples and legal files.

## Commands and exit codes

```text
readme-standards outline [--package NAME] [--format markdown|json]
readme-standards schema
readme-standards check [--root PATH] [--all] [--format text|json] [--wheel FILE]
readme-standards scaffold [--root PATH] [--all] [--write]
readme-standards repair [--root PATH] [--all] [--write]
readme-standards render [--root PATH] [--all] [--write]
readme-standards examples [--root PATH] --wheel FILE
```

Check never writes. Scaffold/repair/render print a unified diff by default; --write explicitly
applies it. Scaffold refuses an existing nonempty README. Repair inserts missing headings
and reorders known sections; render replaces only existing managed regions. Neither silently
discards ambiguous content. Batch writes are per-package, not an all-or-nothing transaction.

Exit 0: check passed or preview generated. Exit 1: policy nonconformance, including a newly
written scaffold whose prose is unfinished. Exit 2: configuration/command error. Explicit
example subprocess failures return nonzero; their traceback includes the failed process.
--wheel checks one package and cannot be combined with --all.

## Monorepo discovery

`check --all --root .` and `pytest --readme-standards --readme-all` discover all `[project]`
manifests, including packages missing the plugin declaration. Such omissions fail. Hidden
directories, virtual environments, build/dist, node_modules, and cache trees are skipped.
The initial adapter does not inventory every historical release or other ecosystem manifests.
Reviewed exclude patterns are needed for non-distributable fixtures and retired packages.

## Installation

```bash
uv add --dev "readme-standards==0.1.3"
```

Commit the resulting dependency lock. For source development, use an explicit Git revision
from groupsum/readme-standards. Release through the scoped workflow in docs/release.md.

## Source-only Python projects

When `[tool.uv].package = false`, installer fragments describe the checkout environment (`uv sync`) and explain why pip/Poetry do not install that harness. This preserves the common heading tree without inventing a wheel installation.

# Branding and badge contract

The package name is the H1. Immediately below it, one `branding` managed region
contains all of the following, in order. No additional Markdown heading is introduced.

| Order | Element | Source and scope |
| --- | --- | --- |
| 1 | Linked brand artwork | Shared catalog: absolute HTTPS logo, alt text, project destination |
| 2 | Prominent package identity | Exact project.name, plain HTML text |
| 3 | One-sentence description | project.description |
| 4 | Distribution/version badges | Declared registries, ordered PyPI → crates.io → npm → GHCR |
| 5 | Source version | Explicit project.version, labelled separately from published versions |
| 6 | Runtime compatibility | project.requires-python; no untested platform claims |
| 7 | Architectural layer | Package configuration |
| 8 | Lifecycle | Active, experimental, planning, deprecated, or retired |
| 9 | License | SPDX expression and package license destination |
| 10 | Notice | Package attribution destination or explicit absence of a separate notice |
| 11 | Download/metric badges | Exact distribution identity and explicit metric/time window |
| 12 | README hits | Stable repository + package path + README identity, not a repository-wide counter |
| 13 | README standards | Declared status and evidence destination |
| 14 | Tests | Declared status; identify repository-wide versus package-scoped checks honestly |
| 15 | Certification | Not certified, not applicable, partial, or verified |
| 16 | Governance | Applicable package or shared policy record |
| 17 | Evidence | Actual verification scope and supporting destination |
| 18 | Navigation | Overview · Installation · Quick Start · Usage · API · Contributing · Governance · License |

Badge rows group 4–10 (package facts), 11–12 (metrics), and 13–17 (checks/governance).
The artwork, identity, description, and navigation each have their own centered row.
Exactly one horizontal rule follows the fragment before Overview.

Published PyPI/npm packages use monthly downloads; crates.io uses total downloads.
GHCR is not assigned a fabricated download count: pull metrics display unavailable unless
an explicitly scoped custom metric is configured. Unpublished projects display unpublished,
not a broken version badge or an invented zero. PyPI/npm/crates version badges are dynamic;
GHCR shows the declared image identity without claiming a registry version lookup.

Built-in badges use navy labels and different colors for registries, package facts,
traffic, and verification. Active and verified states use green, deprecated and
unpublished states use amber, and retired packages use red. Slate marks unavailable
or inapplicable information. Every badge spells out its meaning in text, and custom
metric images retain their provider's styling.

Catalog example (shared path resolved relative to the package's pyproject.toml):

```toml
[brands.groupsum]
name = "Groupsum"
homepage = "https://github.com/groupsum/readme-standards"
logo_url = "https://raw.githubusercontent.com/groupsum/readme-standards/master/docs/assets/readme-standards.svg"
logo_alt = "Groupsum README Standards"
```

Generated fragments are embedded in committed README text, not runtime include directives,
so registry renderers do not need this plugin. Static checks compare the exact fragment
against declared inputs. They do not fetch remote images, validate external service counts,
or prove a linked report's truth. Positive status labels require matching local evidence;
review remains necessary. Private repositories may need a public brand-asset host.

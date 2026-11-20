# Authored content

All headings are generated from the policy; only the package-name H1 varies. Keep prose
directly in README.md. There is no required second copy of that prose in YAML or section files.

## Ownership

Generated blocks use standalone markers:

```markdown
<!-- readme-standards:begin installation.uv -->
...deterministically rendered installer instructions...
<!-- readme-standards:end installation.uv -->
```

Authors may add explanations outside those markers. Render only replaces marked content.
Repair moves complete known sections, inserts omissions, and normalizes group separators.
Unknown headings, duplicates, malformed markers, or an ambiguous preamble require manual
resolution. The renderer does not invent or overwrite behavioral explanations.

Scaffold inserts `AUTHOR REQUIRED` comments beneath authored leaf sections. These are
deliberate failures, not acceptable content. Check also rejects empty prose, unresolved
placeholders, bare N/A/none/not-applicable statements, and long identical explanations
repeated across sections. Structural completeness does not prove semantic adequacy.

## What authors must explain

| Sections | Required substance, assessed through review |
| --- | --- |
| Summary | Concrete package responsibility and deliverable |
| Why This Package / When to Use | Problem solved, appropriate consumers, and meaningful selection limits |
| Features / Non-Goals | Implemented behavior and explicit boundaries; distinguish plans |
| Prerequisites | Runtime, system, service, credential, and platform requirements that affect use |
| Expected Result | Observable result of the actual quick-start example |
| Configuration / Error Handling | Inputs, defaults, failure behavior, and caller responsibilities |
| Best Practices | Package-specific safe and useful usage guidance |
| What It Owns / Public API and Import Surfaces | Owned boundary, supported imports, and stability |
| Injected Dependencies / Protocol Consumers / Extensions | Collaborators, contracts, integration direction, and supported extension mechanisms |
| Operational Requirements / Health and Observability | Deployment assumptions and ways to observe operation, or why no service surface exists |
| Security and Resource Limits / Compatibility | Actual constraints and support guarantees, tied to evidence |
| Tests / Certification Status / Evidence | Reproduction commands, honest status, and scoped evidence links |
| FAQ: Why / How / When | Real questions as bold paragraphs and package-specific answers |
| More Documentation / Related Packages | Authoritative links and why related packages matter |
| How to Contribute / Development Setup / Notes for Maintainers | Actionable contribution, test, build, and maintenance instructions |
| Ownership and Decision Making / Standards and Policies / Lifecycle and Migration | Accountable owner, applicable policies, current lifecycle and migration path |

Generated entry points and legal/registry links need no duplicate authored prose.
Container introductions and additional diagrams, tables, explanations, or examples are
optional. Source, expected stdout fixture, and test reference are required for Quick Start
and Usage. Positive claims require evidence. A no-runtime planning package must demonstrate
its real limited contract rather than invent a runtime capability.

## Missing sections and incorrect order

The checker compares the parsed heading tree with the versioned policy, not with a list
declared by each README. Missing headings fail independently of empty content. Each heading
has an exact label, level, parent, and ordered position. Fenced examples and comments do not
introduce headings. HTML headings, headings inside quotes/lists, and H5/H6 are rejected.

Run `repair` to preview proposed changes; review and repeat with `--write` to apply them.
An inserted heading does not clear the content failure until its prose is supplied.
Use a concrete applicability explanation, for example: "This package registers no CLI
commands; applications consume its Python constructors." Do not remove the heading.

## Adoption sequence

1. Install and lock the plugin as a development dependency.
2. Add package configuration and shared branding, examples, legal documents, and test references.
3. Audit with check and map legacy headings to the fixed outline manually where ambiguous.
4. Preview repair, apply reviewed changes, and write the missing explanations.
5. Render after changes to metadata or examples, then run pytest and built-wheel verification.
6. Make the dedicated README CI job required in the repository's branch policy where appropriate.

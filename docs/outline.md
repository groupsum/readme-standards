# Package-guide-v1 outline

Every row is required once. H1 is the manifest package name; every other label is literal. No optional headings, H5/H6, or extra package-specific headings are allowed. Place exactly one `---` before each H2, including Overview after branding. Container introductions are optional; their child sections are required.

| Level | Exact label | Parent ID | Content owner |
| --- | --- | --- | --- |
| H1 | &lt;package name> | none | generated |
| H2 | Overview | package | container |
| H3 | Summary | overview | authored |
| H3 | Why This Package | overview | authored |
| H3 | When to Use | overview | authored |
| H3 | Features | overview | authored |
| H3 | Non-Goals | overview | authored |
| H2 | Getting Started | package | container |
| H3 | Prerequisites | getting-started | authored |
| H3 | Installation | getting-started | container |
| H4 | uv | installation | generated |
| H4 | pip | installation | generated |
| H4 | Poetry | installation | generated |
| H3 | Quick Start | getting-started | container |
| H4 | Example | quick-start | example |
| H4 | Expected Result | quick-start | authored |
| H2 | Usage | package | container |
| H3 | Common Workflows | usage | example |
| H3 | Configuration | usage | authored |
| H3 | Error Handling | usage | authored |
| H3 | Best Practices | usage | authored |
| H2 | Package Boundary | package | container |
| H3 | What It Owns | package-boundary | authored |
| H3 | Public API and Import Surfaces | package-boundary | authored |
| H3 | Entry Points | package-boundary | generated |
| H3 | Injected Dependencies | package-boundary | authored |
| H3 | Protocol Consumers | package-boundary | authored |
| H3 | Extensions | package-boundary | authored |
| H2 | Operations and Readiness | package | container |
| H3 | Operational Requirements | operations-and-readiness | authored |
| H3 | Health and Observability | operations-and-readiness | authored |
| H3 | Security and Resource Limits | operations-and-readiness | authored |
| H3 | Compatibility | operations-and-readiness | authored |
| H2 | Verification | package | container |
| H3 | Tests | verification | authored |
| H3 | Certification Status | verification | authored |
| H3 | Evidence | verification | authored |
| H2 | FAQ | package | container |
| H3 | Why | faq | authored |
| H3 | How | faq | authored |
| H3 | When | faq | authored |
| H2 | Documentation and Related Packages | package | container |
| H3 | More Documentation | documentation-and-related-packages | authored |
| H3 | Related Packages | documentation-and-related-packages | authored |
| H3 | Project Links | documentation-and-related-packages | generated |
| H2 | Contributing | package | container |
| H3 | How to Contribute | contributing | authored |
| H3 | Development Setup | contributing | authored |
| H3 | Notes for Maintainers | contributing | authored |
| H2 | Governance | package | container |
| H3 | Ownership and Decision Making | governance | authored |
| H3 | Standards and Policies | governance | authored |
| H3 | Lifecycle and Migration | governance | authored |
| H2 | License and Attribution | package | container |
| H3 | License | license-and-attribution | generated |
| H3 | Notices | license-and-attribution | generated |

## Content ownership

- `container`: child sections supply content; direct introductory prose is optional.
- `authored`: nonempty explanatory prose is required; unresolved placeholders and bare applicability statements fail. Concrete reasons for non-applicability are accepted.
- `generated`: the exact managed fragment is required; author additions outside its markers are optional.
- `example`: maintained source is rendered in a managed region; source, expected stdout, and a test reference are required. Explanatory prose outside the region is optional.

These mechanical checks do not judge semantic truth. Review claims and run installed examples. More detailed obligations for prose are described in docs/authoring.md.

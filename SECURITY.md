# Security

Ordinary README validation is read-only and does not fetch remote resources or import
the package being documented. Configured package-local file paths are checked for containment.
Shared brand catalogs are explicit inputs and may live above individual package directories.

Render and repair require --write to apply changes. Review changes to schemas, brand catalogs,
inventory exclusions, evidence declarations, and included example source as code changes.

The examples command executes trusted source and installs a trusted wheel plus dependencies.
A virtual environment is not a security sandbox. Run untrusted contributions in an isolated
CI runner without secrets. Python example execution has a configured timeout and removes
application credentials from the child environment, but package installation uses pip's normal
configuration and may need index access.

Use GitHub private vulnerability reporting when available. Never include credentials or
private package contents in public reports.

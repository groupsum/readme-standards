# Trusted PyPI release

The only authorized publisher tuple for this project is:

- PyPI project: readme-standards
- GitHub repository: groupsum/readme-standards
- Caller workflow: release.yml
- GitHub environment: pypi

The workflow invokes the shared cobycloud/actions composite action in its own publishing
job (PyPI does not accept reusable publishing workflows), sets publish-mode to
trusted, and passes no API token. It builds and checks the artifacts before the separate
publishing job receives OIDC permissions. Dispatch on an immutable vVERSION tag whose
version matches pyproject.toml. An immutable vVERSION-pypi.N publication-attempt tag is
also accepted when an unpublished version needs a workflow correction. Existing tags
must not be moved. The environment restricts deployment to version tags.

Before releasing, run the source and wheel gates and review README claims. After the
workflow succeeds, verify both PyPI artifacts, their SHA-256 digests, project metadata,
and a clean installation including the CLI, schema, and pytest entry point. PyPI
publication is permanent; a correction requires a new version, not replacing files.

Downstream adoption pins the published version as a development dependency. Repository
documentation changes do not themselves publish downstream package versions.

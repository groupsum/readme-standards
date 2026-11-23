# Implementation and pytest integration

## Architecture

1. `policy.py`: immutable Section records define labels, levels, parents, order, and content ownership.
2. `schema.json` and `config.py`: validate tool configuration and load PEP 621 metadata without
   importing target-package code. Discover package manifests independently of plugin declarations.
3. `document.py`: parse CommonMark tokens and managed-region markers with source locations.
4. `render.py`: build package-scoped fragments and make conservative repairs. Preview is default.
5. `check.py`: produce structured, read-only diagnostics for structure, content, fragments,
   legal/example files, and evidence identity.
6. `artifacts.py`: verify wheel metadata/description/legal bytes and explicitly run installed examples.
7. `pytest_plugin.py`: add custom pytest Items with readable failures.
8. `cli.py`: expose check, scaffold, repair, render, outline, schema, and installed-example commands.

## How the pytest plugin is made

The distribution declares this entry point:

```toml
[project.entry-points.pytest11]
readme_standards = "readme_standards.pytest_plugin"
```

`pytest_addoption` registers --readme-standards, --readme-root, and --readme-all. With the
flag enabled, `pytest_collection_modifyitems` discovers package roots and appends a custom
ReadmeItem per package. Each item's runtest calls the same checker as the CLI. Its
repr_failure prints rule IDs and file/line diagnostics. Tests are added independently of
normal testpaths, including when there are no ordinary Python tests.

Without the flag, the installed plugin adds no README items. Install it in the development
environment and put `--readme-standards` in your existing pytest addopts or CI command.
Do not replace existing addopts when adopting it. If plugin autoload is disabled, use:

```bash
pytest -p readme_standards.pytest_plugin --readme-standards --readme-all --readme-root .
```

Pytest plugin autoload/entry points and custom Items are documented in the
[official plugin guide](https://docs.pytest.org/en/stable/how-to/writing_plugins.html) and
[non-Python test example](https://docs.pytest.org/en/stable/example/nonpython.html).

## Local verification

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest --readme-standards
uv build
uv run twine check dist/*
uv run readme-standards check --wheel dist/readme_standards-0.1.3-py3-none-any.whl
uv run readme-standards examples --wheel dist/readme_standards-0.1.3-py3-none-any.whl
```

The final command installs the wheel and its normal dependencies in a new temporary venv,
copies both examples outside the source checkout, executes with isolated Python imports,
and compares stdout with committed fixtures. This is explicit execution of trusted code,
not a sandbox. Ordinary pytest README items only check static inputs; run this command
in the release job to establish installed behavior.

The workflow in `.github/workflows/ci.yml` runs this sequence on Linux and Windows with
read-only repository permissions. It has no publication credentials and does not publish.
Build artifacts are uploaded for inspection. Dependency versions are locked in uv.lock.

## Initial scope and limitations

No Cargo/npm/container manifest adapter, source-distribution content parity check, remote
badge/link liveness check, automatic prose author, semantic documentation score, external
certifier, or index publication command is implemented. Wheel and stdout checks validate
their stated scope; a test-file reference alone does not prove tests were executed. Additional
example assets/services/credential-dependent examples require an integration test adapter.

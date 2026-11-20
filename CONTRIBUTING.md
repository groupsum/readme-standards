# Contributing

Open an issue describing the package scenario and expected diagnostic. Keep changes
focused and add regressions for incorrect acceptance, content loss, or unsafe repair.

Run `uv sync --group dev`, `uv run ruff check .`, and `uv run pytest --readme-standards`.
Build with `uv build`, then check the wheel using the commands in docs/development.md.

Do not update generated fragments by hand. Edit metadata or source examples and run
`uv run readme-standards render --write`. Review the diff and rerun the gate.

Report security concerns privately through GitHub's private vulnerability reporting
when available; do not place credentials, private source, or exploit secrets in issues.

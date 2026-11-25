"""Explicit commands: validation never writes; mutations require --write."""

import argparse
import json
import sys
from pathlib import Path

from .artifacts import check_wheel, run_examples
from .check import check_package
from .config import ConfigurationError, discover, load_package, schema
from .policy import outline
from .render import diff, render, repair
from .ssot import ssot_badge


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="readme-standards")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "scaffold", "repair", "render", "examples"):
        command = sub.add_parser(name)
        command.add_argument("--root", type=Path, default=Path.cwd())
        if name in {"check", "scaffold", "repair", "render"}:
            command.add_argument("--all", action="store_true", dest="all_packages")
        if name in {"scaffold", "repair", "render"}:
            command.add_argument(
                "--write", action="store_true", help="apply changes; default prints a diff"
            )
        if name == "check":
            command.add_argument("--format", choices=("text", "json"), default="text")
        if name in {"check", "examples"}:
            command.add_argument("--wheel", type=Path, required=name == "examples")
    sub.add_parser("schema")
    command = sub.add_parser("ssot-badge", help="convert an SSOT validation report to Shields JSON")
    command.add_argument("--root", type=Path, default=Path.cwd())
    command.add_argument("--report", type=Path, required=True)
    command.add_argument("--commit", required=True, help="full commit SHA expected for this badge")
    command.add_argument("--policy-version", required=True, help="expected SSOT validation policy")
    command = sub.add_parser("outline")
    command.add_argument("--package", default="<package name>")
    command.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            print(json.dumps(schema(), indent=2))
            return 0
        if args.command == "ssot-badge":
            package = load_package(args.root)
            report = json.loads(args.report.read_text("utf-8-sig"))
            print(json.dumps(ssot_badge(package, report, args.commit, args.policy_version)))
            return 0
        if args.command == "outline":
            rows = outline(args.package)
            if args.format == "json":
                print(json.dumps(rows, indent=2))
            else:
                print("| Level | Heading | Parent | Content |\n| --- | --- | --- | --- |")
                for row in rows:
                    print(
                        f"| H{row['level']} | {row['title']} | {row['parent'] or 'none'} | {row['content']} |"
                    )
            return 0
        if args.command == "examples":
            package = load_package(args.root)
            issues = check_package(args.root)
            if issues:
                print("\n".join(map(str, issues)), file=sys.stderr)
                return 1
            run_examples(package, args.wheel)
            print("Both declared examples passed against the installed wheel.")
            return 0
        if args.command == "check" and args.wheel and args.all_packages:
            raise ConfigurationError("--wheel checks one package; do not combine it with --all")
        roots = discover(args.root, args.all_packages)
        issues = []
        for root in roots:
            if args.command in {"scaffold", "repair", "render"}:
                package = load_package(root)
                before = package.readme.read_text("utf-8") if package.readme.exists() else ""
                if args.command == "scaffold" and before:
                    raise ConfigurationError(f"{package.readme} already exists; use repair")
                after = (
                    render(before, package) if args.command == "render" else repair(before, package)
                )
                print(diff(before, after, str(package.readme)), end="")
                if args.write and after != before:
                    package.readme.parent.mkdir(parents=True, exist_ok=True)
                    package.readme.write_text(after, encoding="utf-8", newline="\n")
                # Preview must not pretend the on-disk document has been changed.
                if not args.write:
                    continue
            issues.extend(check_package(root))
        if args.command == "check" and args.wheel:
            issues.extend(check_wheel(load_package(args.root), args.wheel))
        if args.command == "check" and args.format == "json":
            print(
                json.dumps(
                    {
                        "packages": len(roots),
                        "passed": not issues,
                        "diagnostics": [issue.as_dict() for issue in issues],
                    },
                    indent=2,
                )
            )
        elif issues:
            print("\n".join(map(str, issues)), file=sys.stderr)
        elif args.command == "check":
            print(f"README standards passed for {len(roots)} package(s).")
        return 1 if issues else 0
    except (ConfigurationError, OSError, ValueError) as error:
        print(f"readme-standards: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

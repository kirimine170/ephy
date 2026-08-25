#!/usr/bin/env python3
"""Clone missing repositories into a non-Git Ephy workspace root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence


DIRECTORY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "workspace" / "repositories.json"


def load_manifest(path: Path = MANIFEST_PATH) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("repositories"), list):
        raise ValueError("unsupported workspace manifest")
    return data["repositories"]


def resolve_workspace_root(explicit_root: str | None) -> Path:
    root = (
        Path(explicit_root).expanduser()
        if explicit_root
        else Path(__file__).resolve().parents[2]
    ).resolve()
    if not root.is_dir():
        raise ValueError(f"workspace root is not a directory: {root}")
    if (root / ".git").exists():
        raise ValueError("workspace root must not be a Git repository")
    return root


def selected(repository: dict[str, Any], args: argparse.Namespace) -> bool:
    is_private = repository["visibility"] == "private"
    is_optional = not repository["required"]
    if is_private and not args.include_private:
        return False
    if is_optional and not args.include_optional:
        return False
    return bool(repository["auto_clone"] or is_private or is_optional)


def validate_entry(repository: dict[str, Any]) -> None:
    required_fields = {
        "id",
        "github",
        "directory",
        "visibility",
        "required",
        "auto_clone",
    }
    if set(repository) != required_fields:
        raise ValueError(f"invalid manifest fields for {repository.get('id', '<unknown>')}")
    if not DIRECTORY_PATTERN.fullmatch(repository["directory"]):
        raise ValueError(f"unsafe local directory: {repository['directory']!r}")
    if repository["visibility"] not in {"public", "private", "internal"}:
        raise ValueError(f"invalid visibility for {repository['id']}")
    if repository["visibility"] != "public" and repository["auto_clone"]:
        raise ValueError(f"private repository cannot auto-clone: {repository['id']}")


def bootstrap(root: Path, repositories: Sequence[dict[str, Any]], args: argparse.Namespace) -> int:
    root = root.resolve()
    failures = 0
    for repository in repositories:
        validate_entry(repository)
        if not selected(repository, args):
            print(f"skip  {repository['id']}（explicit option required）")
            continue
        destination = root / repository["directory"]
        try:
            destination.resolve().relative_to(root)
        except ValueError:
            print(f"error {repository['id']}: destination escapes workspace", file=sys.stderr)
            failures += 1
            continue
        if destination.exists():
            state = "Git repository" if (destination / ".git").exists() else "existing path"
            print(f"keep  {repository['id']}（{state}，never overwritten）")
            continue
        url = f"https://github.com/{repository['github']}.git"
        print(f"clone {repository['id']} -> {destination.name}")
        if args.dry_run:
            continue
        result = subprocess.run(
            ["git", "clone", url, str(destination)],
            cwd=root,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            failures += 1
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="workspace root; defaults to the parent of ephy")
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="allow selected private repositories to be cloned",
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="include optional repositories; combine with --include-private when needed",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = resolve_workspace_root(args.root)
        failures = bootstrap(root, load_manifest(), args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"bootstrap failed: {exc}", file=sys.stderr)
        return 1
    if failures:
        print(f"bootstrap completed with {failures} failure(s)", file=sys.stderr)
        return 1
    print("workspace bootstrap check completed without modifying existing repositories．")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

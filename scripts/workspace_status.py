#!/usr/bin/env python3
"""Report repository state without modifying the workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence

from bootstrap_workspace import load_manifest, resolve_workspace_root


def git_output(repository: Path, *arguments: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def metadata_value(path: Path, section: str, field: str) -> str:
    if not path.is_file():
        return "missing"
    current_section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == f"{section}:":
            current_section = section
            continue
        if line and not line.startswith(" "):
            current_section = None
        prefix = f"  {field}:"
        if current_section == section and line.startswith(prefix):
            raw = line[len(prefix):].strip()
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                value = raw
            return "null" if value is None else str(value)
    return "missing"


def report_repository(root: Path, repository: dict[str, object]) -> None:
    path = root / str(repository["directory"])
    print(str(repository["id"]))
    print(f"  path: {path}")
    if not (path / ".git").exists():
        print("  state: missing or not a Git repository")
        return

    _, branch = git_output(path, "branch", "--show-current")
    _, porcelain = git_output(path, "status", "--porcelain")
    _, remote = git_output(path, "remote", "get-url", "origin")
    _, last_commit = git_output(path, "log", "-1", "--format=%h %cI %s")
    upstream_code, counts = git_output(
        path, "rev-list", "--left-right", "--count", "HEAD...@{upstream}"
    )
    if upstream_code == 0 and len(counts.split()) == 2:
        ahead, behind = counts.split()
    else:
        ahead, behind = "unknown", "unknown"
    metadata = path / ".ephy" / "project.yaml"
    print(f"  branch: {branch or '(detached)'}")
    print(f"  worktree: {'dirty' if porcelain else 'clean'}")
    print(f"  ahead/behind: {ahead}/{behind}")
    print(f"  remote: {remote or 'missing'}")
    print(f"  last commit: {last_commit or 'none'}")
    print(
        "  metadata: "
        f"id={metadata_value(metadata, 'project', 'id')}，"
        f"status={metadata_value(metadata, 'project', 'status')}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="workspace root; defaults to the parent of ephy")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = resolve_workspace_root(args.root)
        repositories = load_manifest()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"status failed: {exc}", file=sys.stderr)
        return 1
    for repository in repositories:
        report_repository(root, repository)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
